import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import pandas as pd

# Spotify credentials
SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''

def get_playlist_songs(playlist_url):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))

    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    playlist = sp.playlist(playlist_id)

    songs = []
    offset = 0
    limit = 100 #per 1 request

    while True:
        result = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        
        # Loop through each item and add song details to the list
        for item in result['items']:
            track = item['track']
            songs.append({
                'name': track['name'],
                'artist': ", ".join(artist['name'] for artist in track['artists']),
                'spotify_url': track['external_urls']['spotify']
            })

        if len(result['items']) < limit:
            break

        offset += limit

    return songs, playlist['name']

def search_and_download(song, artist, folder_name):
    query = f"{song} {artist}"
    options = {
        'format': 'bestaudio/best',
        'outtmpl': f'{folder_name}/{song}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            ydl.download([f"ytsearch1:{query}"])
            print(f"pass: {song}")
        except Exception as e:
            print(f"Failed to download {song}: {e}")

def save_to_csv(songs, playlist_name):
    df = pd.DataFrame(songs)
    df.to_csv(f"{playlist_name}.csv", index=False)
    print(f"saved playlist to {playlist_name}.csv")

def main():
    playlist_url = input("Enter Spotify Playlist URL: ")
    songs, playlist_name = get_playlist_songs(playlist_url)

    playlist_folder_name = playlist_name.replace("/", " ").strip()
    if not os.path.exists(playlist_folder_name):
        os.mkdir(playlist_folder_name)

    for song in songs:
        song['name'] = song['name'].replace("/", " ")

    save_to_csv(songs, playlist_folder_name)

    for song in songs:
        search_and_download(song['name'], song['artist'], playlist_folder_name)

    print(f"downloaded in folder: {playlist_folder_name}")

if __name__ == "__main__":
    main()
