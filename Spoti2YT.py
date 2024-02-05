import time
import requests
from YTRequestHelper import *

SPOTIFY_SAMPLE_PLAYLIST_URL = "https://open.spotify.com/playlist/04T2TVrG4zMzp9XRSgPwqE?si=71a308b0a76a43c6"
YOUTUBE_SAMPLE_PLAYLIST_URL = "https://music.youtube.com/playlist?list=PLNJxw6sW4nmyXV36PINlEVOOR_Dva2G61"
use_samples = input("Use samples? ") == "1"
current_song_name = ""
failed_insert_songs = []
def main():
    
    # Get all spotify playlist items
    tracks = get_playlist_tracks_by_url()
    tracks.reverse()

    # Insert each item in YT Playlist
    yt_service, credentials = get_service_for_authorized_user()
    for track in tracks:
        track_name = get_track_name(track)
        query = track_name
        search_response = yt_service.search().list(
            q=query,
            type='video',
            part='id,snippet'
        ).execute()
        song = search_response.get('items', [])
        song_id = song[0]['id']['videoId']
        insert_song_into_playlist(song_id, credentials)

# Functions

def insert_song_into_playlist(song_id, credentials, song_name = ""):
    if (use_samples):
        playlist_url = YOUTUBE_SAMPLE_PLAYLIST_URL    
    else:
        playlist_url = input("Enter the Youtube Music playlist URL: ")
    
    playlist_id = get_youtube_playlist_id_from_url(playlist_url)
    post_song_to_playlist(song_id, playlist_id, credentials, song_name)

def post_song_to_playlist(song_id, playlist_id, credentials, song_name = ""):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    scopes = ["https://www.googleapis.com/auth/youtube"]
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_credentials.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    # # credentials = flow.run_console()
    # credentials = flow.run_local_server(port=50500)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": playlist_id,
            "position": 0,
            "resourceId": {
              "kind": "youtube#video",
              "videoId": song_id
            }
          }
        }
    )
    max_retries = 4
    retry_count = 0
    backoff_time = 1
    while retry_count < max_retries:
        try:
            response = request.execute()
            print(f'Song {response["snippet"]["title"]} added successfully.')
            return response
        except Exception as e:
            retry_count += 1
            print(f"An error occurred while inserting a song. Retrying: {retry_count}")
            time.sleep(backoff_time)
            backoff_time *= 2
            
    print("Song {song_name} could not be inserted. Continuing")
    failed_insert_songs.append(song_name)

def get_spotify_playlist_id_from_url(playlist_url):
    return get_partial_playlist_id_from_url(playlist_url, "playlist/")[:playlist_url.index("?")]

def get_youtube_playlist_id_from_url(playlist_url):
    return get_partial_playlist_id_from_url(playlist_url, "list=")
    

def get_partial_playlist_id_from_url(playlist_url: str, playlist_text) -> str:
    return playlist_url[playlist_url.index(playlist_text) + len(playlist_text): ]

def get_playlist_tracks_by_url():
    if (use_samples):
        playlist_url = SPOTIFY_SAMPLE_PLAYLIST_URL
    else:
        playlist_url = input("Enter the spotify playlist URL: ")
    return get_playlist_tracks_from_url(playlist_url)

def get_playlist_tracks_from_url(playlist_url):
    playlist_id = get_spotify_playlist_id_from_url(playlist_url)
    token = get_token()
    return get_playlist_tracks(playlist_id, token)


def get_playlist_tracks(playlist_id, token):

    tracks_url = "https://api.spotify.com/v1/playlists/{0}/tracks?offset=0&limit=100".format(playlist_id)
    # tracks_url = "https://api.spotify.com/v1/playlists/{0}/tracks".format(playlist_id)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    items = []
    while tracks_url:
        
        response = requests.get(tracks_url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Unable to retrieve tracks from playlist: {response.text}")
        

        json = response.json()
        tracks_url = get_next_url_and_add_songs_to_list_from_json(items, json)

    return items

def get_next_url_and_add_songs_to_list_from_json(items, json):
    songs_key = "tracks"
    if songs_key in json:
        json = json["tracks"]
    songs_key = "items"
    tracks_url = json["next"]
    items.extend(json[songs_key])
    return tracks_url

def get_token():
    CLIENT_ID = "6a2642391a344ec6906a2acd1cd7612d"
    CLIENT_SECRET = "8a698c413cdf43faa5102bc910b9c127"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {
    "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(TOKEN_URL, data=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Unable to retrieve access token: {response.text}")
    return response.json()["access_token"]
    

def get_track_name(track):
    track_artist = track["track"]["artists"][0]["name"]
    track_name = track["track"]["name"]
    return f"{track_artist} - {track_name}"

main()
