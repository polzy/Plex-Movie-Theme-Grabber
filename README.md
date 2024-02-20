# Enhancement Scripts for Plex Media Server

As a novice programmer, I've embarked on a project to automate the enhancement of my Plex media server by adding theme songs and metadata to my movie collection. This GitHub repository contains my initial efforts in Python scripting and an upcoming HTML interface for song validation. I warmly welcome any improvements, suggestions, or contributions to refine these scripts further.

## Plex Movie Theme Grabber

This script fetches and integrates theme songs and metadata for movies in your Plex server using The Movie Database (TMDB) API. It's designed with flexibility in mind, supporting dynamic path configurations for storing theme songs.

## Plex Music Video Fetcher

When direct theme song files are missing, this script comes into play, downloading theme songs from YouTube with `yt-dlp`. It smartly manages downloads, skipping blocked content and organizing songs by validation status.

## Upcoming: HTML Interface for Song Validation

To simplify the validation of downloaded theme songs against the database, I'm working on a user-friendly HTML interface. This addition aims to make it easier to verify the suitability of songs for the corresponding movies in your collection.

### Key Features

- **Automated Downloads:** Uses `yt-dlp` for theme song retrieval from YouTube.
- **Metadata Management:** Automatically creates `info.json` files for each movie.
- **Intelligent Song Handling:** Differentiates between valid, to-validate, and blocked songs.
- **Database Integration:** Seamlessly updates movie information in a MySQL database.
- **Ease of Validation:** The forthcoming HTML interface will facilitate easy song validation.

### Getting Started

1. **Requirements:** Python 3.6+, `yt-dlp`, `mysql.connector`, FFmpeg.
2. **Setup:** Adjust the database configuration and song directory paths in the scripts.
3. **Usage:** Enhance your Plex collection by running the scripts.
4. **Validation:** Look out for the HTML interface for straightforward song validation.

This project is a personal initiative to augment the Plex experience, adhering to copyright laws and YouTube's terms of service. Contributions to improve and refine these scripts are highly appreciated.

### 🚀 How It Works
The process is divided into three main steps, designed to be as smooth and user-friendly as possible:

### 📑 Step 1: Database Update (run_client.py)
Objective: Scan your Plex Media Server for movies and update the MySQL database with metadata from The Movie Database (TMDB) API for any new or outdated entries.
Details: It cross-references movies in your Plex library with the database, fetching and updating metadata as needed.
### 🎵 Step 2: Theme Song Downloading (run_server.py)
Objective: For movies lacking theme songs, this script searches YouTube for potential matches, downloading the audio for manual validation.
Workflow:
Downloads are temporarily marked as KO (to be validated) in the database.
Audio files are initially stored in _to_validate, awaiting manual review.
### ✅ Step 3: Manual Validation (Web Interface)
Overview: An easy-to-use web interface lists movies with theme songs marked as KO, allowing for straightforward manual validation.
Actions:
Approve: Move validated songs to _Valid, marking them as OK in the database.
Reject/Replace: Reject unsuitable songs or replace them by providing an alternative YouTube link.
### 📁 Directory Structure
_Valid: Holds theme songs that have passed manual validation.
_to_validate: Contains songs awaiting approval or replacement.
_Blocked: For movies where no suitable theme song could be sourced.
### 🌟 Getting Started
### To get started with enhancing your Plex library:

Ensure you have Python 3.6+ and the necessary libraries installed.
Update config.json with your Plex server, database details, and TMDB API key.
Run run_client.py to update your database with the latest movie metadata.
Execute run_server.py to begin the theme song downloading process.
Use the web interface for the final step of manual song validation.
### 🙌 Contribute

Your contributions are welcome! Whether it's improving the scripts, enhancing the web interface, or reporting bugs, feel free to fork this project and submit your pull requests.
