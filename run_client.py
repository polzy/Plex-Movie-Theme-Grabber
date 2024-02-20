from concurrent.futures import ThreadPoolExecutor
import os
import json
import shutil
import glob
import mysql.connector
import requests
from datetime import datetime
from plexapi.server import PlexServer

script_directory = os.path.dirname(os.path.abspath(__file__))
with open('config.json', 'r') as f:
    config = json.load(f)

conn = mysql.connector.connect(**config['database'])
cursor = conn.cursor()

tmdb_api_key = config['tmdb_api_key']
plex_config = config['plex']
plex_url = plex_config['url']
plex_token = plex_config['token']

local_songs_path = os.path.join(script_directory, "local_songs")


valid_only = config.get('Valid_only', 'yes') 

plex = PlexServer(plex_url, plex_token)
movies_section = plex.library.section('films')
movies = movies_section.all(sort='addedAt:desc')

def get_french_title(tmdb_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={tmdb_api_key}&language=fr")
    if response.status_code == 200:
        movie_data = response.json()
        return movie_data.get('title', '')
    else:
        print(f"Erreur lors de la récupération des données pour le film avec TMDB ID: {tmdb_id}")

        return None
    
def search_movie_by_imdb(imdb_id):
    response = requests.get(f"https://api.themoviedb.org/3/find/{imdb_id}", params={
        'api_key': tmdb_api_key,
        'external_source': 'imdb_id'
    })
    if response.status_code == 200:
        results = response.json().get('movie_results', [])
        return results[0] if results else None
    else:
        print(f"Erreur lors de la recherche de films avec IMDB ID: {response.status_code}")
        return None
    
# Parcourir les dossiers de films
for movie in movies:
    print(f"Traitement du film : {movie.title}")
    imdb_id = None
    tmdb_id = None

    for guid in movie.guids:
        if 'imdb://' in guid.id:
            imdb_id = guid.id.split('imdb://')[1]
            print("ID IMDb:", imdb_id)
        elif 'tmdb://' in guid.id:
            tmdb_id = guid.id.split('tmdb://')[1]
            print("ID TMDb:", tmdb_id)

    if not tmdb_id and imdb_id:

        response = requests.get(f"https://api.themoviedb.org/3/find/{imdb_id}", params={
            'api_key': tmdb_api_key,
            'external_source': 'imdb_id'
        })
        if response.status_code == 200:
            results = response.json().get('movie_results', [])
            if results:
                tmdb_id = results[0]['id']
                print(f"ID TMDb trouvé via IMDb ID:", tmdb_id)
            else:
                print(f"Aucun ID TMDb correspondant trouvé pour l'ID IMDb donné.")
        else:
            print(f"Erreur lors de la recherche de l'ID TMDb via l'API.")
            tmdb_id = None

    for media in movie.media:
        is_blocked = False
        movie_title = movie.title
        movie_year = movie.year
        movie_rating_key = movie.ratingKey
        split_path = movie.locations[0].split('\\')
        movie_path = '\\'.join(split_path[:-1])
        original_folder_name = movie_path
        
        if imdb_id:
            result = search_movie_by_imdb(imdb_id)
            if result:
                tmdb_id_api = result['id']
                title = result['title']
                release_date = result['release_date']
                poster_path = result.get('poster_path', '')
                popularity = result.get('popularity', 0)
                imdb_id_api = result.get('imdb_id', '') 

            # Obtenez le titre en français
            french_title = get_french_title(tmdb_id)
            print(f"Titre français : {french_title}")
            folder_name_pattern = f"{tmdb_id}-*"
            valid_folder_pattern = os.path.join(local_songs_path, '_Valid', folder_name_pattern)
            to_validate_folder_pattern = os.path.join(local_songs_path, '_to_validate', folder_name_pattern)
            blocked_folder_pattern = os.path.join(local_songs_path, '_Blocked', folder_name_pattern)

            found_folders = []
            if valid_only.lower() == 'yes':
                found_folders += glob.glob(valid_folder_pattern)
            else:
                found_folders += glob.glob(valid_folder_pattern)
                found_folders += glob.glob(to_validate_folder_pattern)
                found_folders += glob.glob(blocked_folder_pattern)

            folder_path = found_folders[0] if found_folders else None
            print(f"Dossier local song : {folder_path}")
            blocked_folders = glob.glob(blocked_folder_pattern)
            is_blocked = bool(blocked_folders)
            if is_blocked:
                is_blocked = True
                print(f"Le film est bloqué")
                movie_folder_path = os.path.join(movie_path, original_folder_name)
                theme_dest_path = os.path.join(movie_folder_path, "theme.mp3")
                info_dest_path = os.path.join(movie_folder_path, "info.json")

                if os.path.exists(theme_dest_path):
                    os.remove(theme_dest_path)
                    print(f"theme.mp3 et info.json supprimé car le film est bloqué.")

                if os.path.exists(info_dest_path):
                    os.remove(info_dest_path)
                    print(f"info.json supprimé car le film est bloqué.")
        if folder_path is not None and os.path.exists(folder_path) and not is_blocked:       
            if os.path.exists(folder_path):
                theme_path = os.path.join(folder_path, "theme.mp3")
                info_path = os.path.join(folder_path, "info.json")
                
                if os.path.exists(theme_path) and os.path.exists(info_path):
                  print(f"theme.mp3 et info.json sont présents dans local_songs.")

                movie_folder_path = os.path.join(movie_path, original_folder_name) 
                theme_dest_path = os.path.join(movie_folder_path, "theme.mp3")
                info_dest_path = os.path.join(movie_folder_path, "info.json")

                if os.path.exists(theme_dest_path) and not os.path.exists(info_dest_path):
                    os.remove(theme_dest_path)
                    print(f"theme.mp3 supprimé car info.json manquant.")
#pas de soft link 
                if os.path.exists(info_path):
                    if not os.path.exists(info_dest_path) or (os.path.exists(info_dest_path) and json.load(open(info_dest_path))['creation_date'] < json.load(open(info_path))['creation_date']):
                        # Copier les fichiers
                        if os.path.exists(theme_path) and os.path.exists(info_path):
                            shutil.copy(theme_path, theme_dest_path)
                            shutil.copy(info_path, info_dest_path)
                            print(f"Copie des fichiers vers : {movie_folder_path} (ID TMDb: {tmdb_id})")
#pas de soft link 
#Code pour softlink
#                if os.path.exists(info_path):
#                    if not os.path.exists(info_dest_path) or (os.path.exists(info_dest_path) and json.load(open(info_dest_path))['creation_date'] < json.load(open(info_path))['creation_date']):
#                        # Copier les fichiers
#                        if os.path.exists(theme_path) and os.path.exists(info_path):
#                            if os.path.islink(theme_dest_path):
#                                os.remove(theme_dest_path)
#                            if os.path.islink(info_dest_path):
#                                os.remove(info_dest_path)                    
#                            # Créer des liens symboliques
#                            os.symlink(theme_path, theme_dest_path)
#                            os.symlink(info_path, info_dest_path)
#                            print(f"Copie des fichiers vers : {movie_folder_path} (ID TMDb: {tmdb_id})")
#Code pour softlink
                        else:
                            print(f"Erreur : Les fichiers n'existent pas. (ID TMDb: {tmdb_id})")
                    else:
                        print(f"theme.mp3 est déjà à la dernière version (ID TMDb: {tmdb_id}).")
        else:
            if tmdb_id:
                cursor.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id = %s", (tmdb_id,))
                count = cursor.fetchone()[0]
                if count == 0:
                    print(f"Film non trouvé dans la base de données. Ajout à la base de données.")
                    user_media = config['user_media']
                    user_media_date = datetime.now().strftime('%Y-%m-%d')
                    validation_status = "KO"
                    youtube_id = "none"

                    params = (
                        tmdb_id, title, french_title, release_date or None, 
                        user_media, user_media_date, validation_status, 
                        youtube_id, poster_path, popularity, imdb_id
                    )

                    cursor.execute("""
                        INSERT INTO movies (
                            tmdb_id, title, french_title, release_date, 
                            user_media, user_media_date, validation_status, 
                            youtube_id, poster_path, popularity, imdb_id
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, params)

                    print(f"Ajout du film à la base de données : {title} (ID TMDb: {tmdb_id})")
                    conn.commit()
                else:
                    print(f"Le film avec ID TMDb: {tmdb_id} existe déjà dans la base de données. Aucune action effectuée.")
            else:
                print(f"Aucun ID TMDb valide trouvé pour l'ajout à la base de données.")        

conn.close()
print(f"===== Script terminé. =====")
