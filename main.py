import os

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

import streamlit as st
import pandas as pd

import json

client_id = ''
client_secret = ''
redirect_uri = 'http://127.0.0.1:5000/callback'
scope = 'playlist-read-private,streaming,user-top-read,user-read-recently-played,playlist-modify-private,playlist-modify-public'

### get track info from list of track_ids
### was unable to get sp.tracks(track_ids) to work properly after troubleshooting
### common causes such as token issues, invalid track_ids, and number of track_ids
def get_tracks(track_ids):
    tracks = []
    for tid in track_ids:
        try:
            track = sp.track(tid)
            if track:
                tracks.append({
                    'track_name': track['name'],
                    'artists': ', '.join(artist['name'] for artist in track['artists']),
                    'song duration': track['duration_ms']
                })  
        except Exception as e:
            print(f"Skipping track, error occured: {e}")
    return tracks

### get list of track_ids for recent listening history
def get_listening_history():
    l_history = sp.current_user_recently_played(limit=25)
    track_ids = [item['track']['id'] for item in l_history['items'] if item['track'] and item['track']['id'] and not item['track']['id'].startswith('spotify:local:')]
    track_ids = list(set(track_ids))
    return get_tracks(track_ids)

### handles access and authorization flows, as well as redirect page
sp_oauth = SpotifyOAuth(
    client_id = client_id, 
    client_secret = client_secret,
    redirect_uri = redirect_uri,
    scope = scope,
    cache_path='.cache',
    show_dialog = True
)

sp = Spotify(auth_manager=sp_oauth)

### set up streamlit web page
st.set_page_config(page_title='Spotify Recent Listen History and Top Songs', page_icon=':musical_note:')
st.title('Listening History Analysis and Top Songs')
st.write('Discover insights about your Spotify listening history and top songs')


if 'history' not in st.session_state:
    st.session_state.history = None

if st.session_state.history is None:
    tracks = get_listening_history()
    df = pd.DataFrame(tracks)
    df['song info'] = df['track_name'] + " - " + df['artists']
    # convert song duration in ms into MM:SS format
    song_lengths = []
    for d in df['song duration']:
        minutes, ms = divmod(d, 60000) # 60000 ms in a minute, remainder in ms
        song_lengths.append(f"{minutes}:{ms//1000:02}")
    df['song length'] = song_lengths
    st.session_state.history = df
    
if st.session_state.history is not None:
    st.subheader('Recently Played Songs')
    st.dataframe(st.session_state.history[['song info', 'song length']])

### get top songs based on input time range, returns list of track objects
def top_songs(range, limit=20):
    songs = sp.current_user_top_tracks(limit=limit, time_range=range)
    songs = songs['items']

    #df = pd.DataFrame(top_songs) # testing
    df = pd.DataFrame(songs)
    df['song info'] = df['name'] + ' - ' + df['artists'].apply(lambda x: ', '.join([a['name'] for a in x]))
    df['album name'] = df['album'].apply(lambda x: x['name'])
    return songs


### create playlist with given songs
def create_playlist(name, desc):
    playlist_id = sp.current_user_playlist_create(name=name,public=True,description=desc)
    playlist_id = playlist_id['id']
    song_ids = st.session_state.df['song id'].tolist()
    sp.playlist_add_items(playlist_id, song_ids)


###### TOP SONGS ######
st.write("User's top songs")
s_artist, m_artist, l_artist = st.columns(3)

### initialize session_state variables
if 'time_frame' not in st.session_state:
    st.session_state.time_frame = 'short_term'

buttons = ['songs_gathered']
for key in buttons:
    if key not in st.session_state:
        st.session_state[key] = False

if 'df' not in st.session_state:
    st.session_state.df = None

### buttons to choose which time frame to search over
if s_artist.button('Short time frame'):
    st.write('Short term')
    st.session_state.time_frame = 'short_term'
if m_artist.button('Medium time frame'):
    st.write('Medium term')
    st.session_state.time_frame = 'medium_term'
if l_artist.button('Long time frame'):
    st.write('Long term')
    st.session_state.time_frame = 'long_term'


### initially only wanted this button to operate once, but realized better functionality
### when able to be used more than once in a single session
if st.button('Top Songs'):
    st.write(f'Gathering Top Songs over {st.session_state.time_frame}')
    st.session_state.songs_gathered = True
    song_list = top_songs(st.session_state.time_frame)
    df = pd.DataFrame(song_list)
    df['song info'] = df['name'] + ' - ' + df['artists'].apply(lambda x: ', '.join([a['name'] for a in x]))
    df['album name'] = df['album'].apply(lambda x: x['name'])
    df['song id'] = df['id']
    st.subheader('Top Songs')
    st.session_state.df = df
    
### only display table when data is populated, and keep data displayed after next button press    
if st.session_state.df is not None:
    st.dataframe(st.session_state.df[['song info', 'album name', 'song id']])


### create spotify playlist for user account
### additionaly confirmation to create playlist?
if st.button('create playlist', disabled=not st.session_state.songs_gathered):
    st.write('Creating playlist, finished product will be found in your Spotify library.')
    playlist_name = 'Top songs'
    playlist_desc = f'top songs over {st.session_state.time_frame}'
    create_playlist(playlist_name, playlist_desc)
