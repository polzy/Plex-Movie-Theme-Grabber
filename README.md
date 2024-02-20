This GitHub repository hosts a collection of scripts designed to automate the enhancement of your Plex media server by adding theme songs and metadata to your movie collection. The repository comprises two main Python scripts and an upcoming HTML interface for easy song validation.

#Plex Movie Theme Grabber
Automates fetching and integrating theme songs and metadata for movies in your Plex server. It leverages The Movie Database (TMDB) API for metadata and supports dynamic path configurations for storing theme songs.

#Plex Music Video Fetcher
Utilizes yt-dlp to download theme songs from YouTube when direct theme song files are missing. It intelligently manages song downloads, avoiding blocked content and organizing songs based on validation status.

#Upcoming: HTML Interface for Song Validation
A user-friendly HTML interface will soon be added to this repository, allowing for easier validation of downloaded theme songs against the database. This interface aims to streamline the process of confirming whether a downloaded song is appropriate for the corresponding movie in your collection.

#Key Features:
Automated Theme Song Downloads: From YouTube using yt-dlp.
Metadata Integration: Creates info.json for each movie.
Smart Content Management: Handles valid, to-validate, and blocked songs.
Database Connectivity: Updates movie information in a MySQL database.
Easy Song Validation: Through an upcoming HTML interface linked to the database.
Quick Start:
Prerequisites: Python 3.6+, yt-dlp, mysql.connector, colorama, and FFmpeg.
Configuration: Update database settings in the scripts and ensure paths to song directories are correctly set.
Execution: Run the scripts to enhance your Plex movie collection with theme songs and metadata.
Validation Interface: Stay tuned for the addition of an HTML interface for easy song validation.
These tools are designed for personal use to improve your Plex viewing experience. Always ensure to comply with copyright laws and YouTube's terms of service.
