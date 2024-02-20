import os
import json
import yt_dlp
import mysql.connector
import subprocess
from datetime import datetime
import urllib.request
import urllib.parse
import re
import shutil
from yt_dlp.utils import DownloadError, ExtractorError

script_directory = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(script_directory, 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

db_config = config['database']
options = config['yt_dlp_options']

local_songs_path = os.path.join(script_directory, config['paths']['local_songs'])
valid_songs_path = os.path.join(script_directory, config['paths']['valid_songs'])
to_validate_songs_path = os.path.join(script_directory, config['paths']['to_validate_songs'])

ignore_keywords = config['ignore_keywords']
search_terms = config['search_terms']

def print_separator():
    print(f"{'=' * 80}")

def update_yt_dlp():
    try:
        print(f"Mise à jour de yt-dlp...")
        subprocess.run(["pip", "install", "--upgrade", "yt-dlp"], check=True)
        print(f"yt-dlp a été mis à jour avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la mise à jour de yt-dlp: {e}")

def move_folder(src, dest):
    try:
        shutil.move(src, dest)
        print(f"Dossier déplacé de {src} à {dest}.")

        if os.path.exists(src):
            print(f"Attention : Le dossier source {src} existe toujours après le déplacement.")
        else:
            print(f"Le dossier source {src} a été correctement déplacé.")

    except Exception as e:
        print(f"Erreur lors du déplacement du dossier : {e}")
     
def check_existing_info(folder_path, youtube_id):
    info_json_path = os.path.join(folder_path, "info.json")
    if os.path.exists(info_json_path):
        with open(info_json_path, 'r') as f:
            existing_info = json.load(f)
        return existing_info.get("youtube_url") == youtube_id
    return False

def read_blocked_videos():
    try:
        with open("blocked_videos.txt", "r") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()

def write_blocked_video(title, blocked_videos):
    if title not in blocked_videos:
        with open("blocked_videos.txt", "a") as f:
            f.write(f"{title}\n")
        blocked_videos.add(title)

def clean_title(title):
    invalid_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_characters:
        title = title.replace(char, '-')
    title = title.replace("...", "")
    return title

def create_info_json(folder_path, youtube_id):
    info = {
        "youtube_url": youtube_id,
        "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(folder_path, "info.json"), 'w') as f:
        json.dump(info, f)
    print(f"info.json créé.")

def search_theme_song(title, year=None, blocked_videos=set(), french_title=None):
    def perform_youtube_search(title, year):
        if title in blocked_videos:
            print(f"Le film {title} est dans la liste des vidéos bloquées. Passer à la suivante.")
            return None
        print(f"Recherche de la chanson thème pour le film '{title}' ({year if year else 'N/A'})...")
        search_query = f"{title} {year if year else ''} " + " | ".join(search_terms)
        query = urllib.parse.urlencode({"search_query": search_query})
        search_url = "http://www.youtube.com/results?" + query
        print(f"Requête YouTube : {search_url}")
        content = urllib.request.urlopen(search_url)
        results = re.findall(r'\/watch\?v=(.{11})', content.read().decode())
        search_limit = 6

        for idx, result in enumerate(results):
            if idx >= search_limit:
                print(f"Limite de {search_limit} vidéos atteinte, passage à la prochaine vidéo.")
                break

            video_url = "http://www.youtube.com/watch?v=" + result
            try:
                print(f"Tentative d'extraction des informations de la vidéo : {video_url}")
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                    video_info = ydl.extract_info(video_url, download=False)
                video_title = video_info.get('title', "")
                view_count = video_info.get('view_count', 0)
                print(f"Titre de la vidéo : {video_title}, Nombre de vues : {view_count}")

                if any(keyword.lower() in video_title.lower() for keyword in ignore_keywords):
                    print(f"Ignoré en raison des mots-clés à ignorer.")
                    continue
                if clean_title(title) not in clean_title(video_title):
                    print(f"Ignoré car le titre ne correspond pas.")
                    continue
                if view_count < 1000:
                    print(f"Ignoré car le nombre de vues est inférieur à 1000.")
                    continue

                print(f"Vidéo acceptée.")
                return video_url
            except yt_dlp.utils.DownloadError:
                print(f"Erreur de téléchargement. Passer à la vidéo suivante.")
                continue

        print(f"Aucune vidéo trouvée.")
        return None

    youtube_url = perform_youtube_search(title, year)
    
    if youtube_url is None and french_title:
        print(f"Aucune vidéo trouvée avec le titre anglais. Recherche avec le titre français...")
        youtube_url = perform_youtube_search(french_title, year)
    
    return youtube_url

def main():
    update_yt_dlp()
    blocked_videos = read_blocked_videos()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    found_urls = {}

    query = "SELECT tmdb_id, title, youtube_id, validation_status FROM movies WHERE youtube_id != 'none' AND youtube_id != ''"
    cursor.execute(query)
    rows = cursor.fetchall()

    for tmdb_id, title, youtube_id, validation_status in rows: 
        print("Traitement du film {title} (ID: {tmdb_id}")
        print(f"Debug: validation_status = {validation_status}")

        folder_name = f"{tmdb_id}-{clean_title(title)}"
        dest_folder_path = os.path.join(valid_songs_path, folder_name) if validation_status == 'OK' else os.path.join(to_validate_songs_path, folder_name)

        if validation_status == 'Blocked':
            blocked_folder_path = "./local_songs/_Blocked"
            blocked_dest_folder_path = os.path.join(blocked_folder_path, folder_name)
            if os.path.exists(dest_folder_path):
                move_folder(dest_folder_path, blocked_dest_folder_path)
            continue 
        if validation_status == 'OK':
            dest_folder_path = os.path.join(valid_songs_path, folder_name)
        else:
            dest_folder_path = os.path.join(to_validate_songs_path, folder_name)
        print(f"Debug: dest_folder_path = {dest_folder_path}")
        should_download = True

        if check_existing_info(dest_folder_path, youtube_id):
            print("Les fichiers pour '{title}' sont déjà OK. Pas de téléchargement nécessaire.")
            should_download = False
        else:
            other_folder_path = os.path.join(to_validate_songs_path if validation_status == 'OK' else valid_songs_path, folder_name)
            if check_existing_info(other_folder_path, youtube_id):
                print(f"Les fichiers pour '{title}' sont déjà OK mais dans le mauvais dossier. Déplacement nécessaire.")
                move_folder(other_folder_path, dest_folder_path)
                should_download = False

        if should_download:
            try:
                os.makedirs(dest_folder_path, exist_ok=True) 
            except Exception as e:
                print(f"Erreur lors de la création du dossier : {e}")
            options['outtmpl'] = os.path.join(dest_folder_path, "theme.%(ext)s")

            if youtube_id not in found_urls:
                try:
                    print(f"Téléchargement du thème depuis {youtube_id}...")
                    with yt_dlp.YoutubeDL(options) as ydl:
                        ydl.download([youtube_id])
                    print(f"Thème téléchargé.")
                    print(f"Debug: folder_path = {dest_folder_path}")
                    create_info_json(dest_folder_path, youtube_id)
                    found_urls[youtube_id] = True
                except yt_dlp.utils.DownloadError:
                    print(f"ERREUR : La vidéo pour '{title}' est bloquée.")
                    cursor.execute("UPDATE movies SET youtube_id = 'none', validation_status = 'KO' WHERE tmdb_id = %s", (tmdb_id,))
                    conn.commit()
                    

    cursor.execute("SELECT tmdb_id, title, french_title, COALESCE(YEAR(release_date), 'N/A') FROM movies WHERE youtube_id = 'none' OR youtube_id = ''")    
    rows = cursor.fetchall()

    for tmdb_id, title, french_title, year in rows: 
        print_separator() 
        if title in blocked_videos:
            print(f"Le film {title} est dans la liste des vidéos bloquées. Passer à la suivante.")
            continue  
        if validation_status != 'OK':
            youtube_url = search_theme_song(title, year, blocked_videos, french_title=french_title)
            validation_status_row = cursor.fetchone()
            if validation_status_row:
                validation_status = validation_status_row[0]
            else:
                validation_status = 'KO' 

            if tmdb_id not in found_urls:
                try:
                    if not youtube_url:
                        youtube_url = search_theme_song(title, year, blocked_videos)

                    if youtube_url:
                        folder_name = f"{tmdb_id}-{clean_title(title)}"
                        if validation_status == 'OK':
                            folder_path = os.path.join(valid_songs_path, folder_name)
                        else:
                            folder_path = os.path.join(to_validate_songs_path, folder_name)
                        os.makedirs(folder_path, exist_ok=True)
                        options['outtmpl'] = os.path.join(folder_path, "theme.%(ext)s")
                        
                        with yt_dlp.YoutubeDL(options) as ydl:
                            ydl.download([youtube_url])
                        print(f"Debug: dest_folder_path = {folder_path}")
                        create_info_json(folder_path, youtube_url)                
                        cursor.execute("UPDATE movies SET youtube_id = %s, validation_status = 'KO' WHERE tmdb_id = %s", (youtube_url, tmdb_id))
                        conn.commit()
                        
                        print(f"Succès : La vidéo pour '{title}' a été téléchargée.")
                        found_urls[tmdb_id] = True
                    else:
                        cursor.execute("UPDATE movies SET youtube_id = 'none', validation_status = 'KO' WHERE tmdb_id = %s", (tmdb_id,))
                        conn.commit()
                        print(f"ERREUR : La vidéo pour '{title}' est bloquée.")
                        write_blocked_video(title, blocked_videos) 
                except Exception as e:
                    print(f"Une erreur inattendue s'est produite : {e}")
                    cursor.execute("UPDATE movies SET youtube_id = 'none', validation_status = 'KO' WHERE tmdb_id = %s", (tmdb_id,))
                    conn.commit()

    conn.close()

if __name__ == "__main__":
    main()

