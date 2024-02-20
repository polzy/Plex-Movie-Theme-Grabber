# Plex-Movie-Theme-Grabber
This script, Plex Movie Theme Grabber, is designed to enhance your Plex movie watching experience by automatically fetching and integrating theme songs and additional metadata for your movie collection directly into Plex. It leverages The Movie Database (TMDB) API to find movie information based on IMDb IDs, downloads theme songs for movies, and updates local movie directories with fetched content. Additionally, it offers functionality to clean up and manage theme songs for blocked movies, ensuring that your Plex server remains organized and up-to-date.

Features:

Fetches French titles and additional metadata for movies using TMDB API.
Searches for movies on TMDB based on IMDb IDs.
Downloads and integrates theme songs and metadata into local movie directories.
Manages theme songs for blocked movies by removing or updating as necessary.
Configurable through a JSON file, allowing for easy customization and flexibility.
Utilizes Python's requests and PlexAPI for efficient data fetching and Plex server interaction.
How to Use:

Obtain an API key from TMDB and input it into the config.json file.
Configure your Plex server details, database settings, and local song paths in config.json.
Run the script and let it automate the process of enhancing your Plex movie collection.
Requirements:

Python 3.6 or later.
PlexAPI, requests, and mysql.connector Python libraries.
A valid TMDB API key.
Access to a Plex server with an active token.
This script is perfect for Plex enthusiasts looking to automate the enrichment of their movie library with theme songs and detailed metadata, creating a more immersive viewing experience.

Note: This script is intended for personal use. Please ensure you have the rights to download and use the theme songs and metadata for your movie collection.
