import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def get_service_for_authorized_user():
    # Set the scopes for the YouTube API
    SCOPES = ["https://www.googleapis.com/auth/youtube"]

    # Your client ID and client secret from Google Cloud Console
    CLIENT_CREDENTIALS_FILE = 'client_credentials.json'

    # Define the redirect URI
    REDIRECT_URI = 'http://localhost:50500/callback'

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CREDENTIALS_FILE, SCOPES, redirect_uri=REDIRECT_URI)
    credentials = flow.run_local_server(port=50500)
    # Save the credentials for future use
    # with open('client_credentials.json', 'w') as token:
    #     token.write(credentials.to_json())

    # Create a YouTube API service object
    youtube_service = build('youtube', 'v3', credentials=credentials)

    # Now you can use `youtube_service` to make authorized API requests
    # For example, to retrieve user playlists:
    return youtube_service, credentials

