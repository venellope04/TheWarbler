import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
from pytube import YouTube
import os
import sys
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt



# Authenticate with Spotify API
def authenticate_spotify():
    return Spotify(auth_manager=SpotifyOAuth(client_id='7ad1f5cf25c24d6f85cc1293d2272a2b',
                                             client_secret='335924fadb4e4b8ab98e19b55077ff0d',
                                             redirect_uri='http://localhost:8888/callback',
                                             scope='playlist-read-private'))

# Authenticate with YouTube API
def authenticate_youtube():
    return build('youtube', 'v3', developerKey='AIzaSyBbnc6ADPi132GEaCd6xasPtb_QTrSJ1i4')

def get_spotify_playlist_songs(sp, playlist_url):
    playlist_id = playlist_url.split('/')[-1].split('?')[0]  # Extract playlist ID from URL
    results = sp.playlist_tracks(playlist_id)
    song_titles = [track['track']['name'] for track in results['items']]
    artist_names = [track['track']['artists'][0]['name'] for track in results['items']]
    return song_titles, artist_names

def search_songs_on_youtube(youtube, song_titles, artist_names):
    song_links = []
    for title, artist in zip(song_titles, artist_names):
        search_query = f'{title} by {artist}'  # Combine title and artist for a more specific search
        search_response = youtube.search().list(
            q=search_query,
            part='id',
            type='video',
            maxResults=1
        ).execute()
        if 'items' in search_response and len(search_response['items']) > 0:
            video_id = search_response['items'][0]['id']['videoId']
            song_links.append(f'https://www.youtube.com/watch?v={video_id}')
    return song_links

def download_and_convert_to_mp3(song_links, download_dir):
    downloaded_mp3_paths = []
    for link in song_links:
        full_path, title = download_video(link, download_dir)
        if full_path.endswith('.mp3'):
            downloaded_mp3_paths.append(full_path)
    return downloaded_mp3_paths

def download_video(url, save_dir="C:/DISHA/songs"):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        sanitized_title = sanitize_filename(yt.title)
        filename = f'{sanitized_title}.mp3'
        full_path = os.path.join(save_dir, filename)
        video.download(output_path=save_dir, filename=filename)
        return full_path, yt.title
    except Exception as e:
        return str(e), None

def sanitize_filename(title):
    """
    Replace characters in the title that are not allowed in filenames with underscores.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '_')
    return title

def main():
    # Authenticate with Spotify and YouTube APIs
    sp = authenticate_spotify()
    youtube = authenticate_youtube()

    # Create the application instance
    app = QApplication(sys.argv)

    # Create the main window
    window = QWidget()
    window.setWindowTitle('Warbler')
    window.setGeometry(100, 100, 400, 200)

    # Create layout
    layout = QVBoxLayout()

    # Create playlist URL input field
    playlist_url_input = QLineEdit()
    
# Set the width of the QLineEdit widget
    playlist_url_input.setFixedWidth(300)

# Set the height of the QLineEdit widget
    playlist_url_input.setFixedHeight(30)

# Set a border style for the QLineEdit widget
    playlist_url_input.setStyleSheet("border: 2px solid #ccc;")

# Set the font size of the QLineEdit widget
    font =playlist_url_input.font()
    font.setPointSize(12)
    playlist_url_input.setFont(font)

# Add some padding to the text inside the QLineEdit widget
    playlist_url_input.setTextMargins(8, 0, 0, 0)

# Add the QLineEdit widget to the layout
    layout.addWidget(playlist_url_input)
    playlist_url_input.setPlaceholderText('Enter Spotify playlist URL')


    # Create download button
    download_button = QPushButton('Download')
    
    download_button.setFont(QFont("Arial", 10))
    download_button.setStyleSheet("background-color: #fff; border: 2px solid #CCCCCC; border-radius: 5px; padding: 5px 10px;")


    # Create message label
    message_label = QLabel()

    # Function to handle download button click
    def download_clicked():
        # Get the playlist URL from the input field
        playlist_url = playlist_url_input.text()

        # Get song titles from the Spotify playlist
        song_titles, artist_names = get_spotify_playlist_songs(sp, playlist_url)

        # Search for songs on YouTube
        song_links = search_songs_on_youtube(youtube, song_titles, artist_names)

        # Download and convert songs to MP3
        downloaded_mp3_paths = download_and_convert_to_mp3(song_links, "C:/DISHA/songs")

        # Display message
        message_label.setText(f"Downloaded MP3s saved to: C:/DISHA/songs")

    # Connect download button click event to handler function
    download_button.clicked.connect(download_clicked)

    # Add widgets to layout
    layout.addWidget(playlist_url_input)
    layout.addWidget(download_button)
    layout.addWidget(message_label)

    # Set layout for the window
    window.setLayout(layout)

    # Show the window
    window.show()

    # Execute the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
