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
