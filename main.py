import os

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

import streamlit as st
import pandas as pd

client_id = ''
client_secret = ''
redirect_uri = 'http://127.0.0.1:5000/callback'
scope = 'playlist-read-private,streaming,user-top-read,user-read-recently-played,playlist-modify-private'

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
st.set_page_config(page_title='Spotify Recent Listen History', page_icon=':musical_note:')
st.title('Listening History Analysis')
st.write('Discover insights about your Spotify listening history')

###### CHANGE - put in session_state var to only make once and never again ######
tracks = get_listening_history()
### create DataFrame and calculate columns to display
df = pd.DataFrame(tracks)
df['song info'] = df['track_name'] + " - " + df['artists']
# convert song duration in ms into MM:SS format
song_lengths = []
for d in df['song duration']:
    minutes, ms = divmod(d, 60000) # 60000 ms in a minute, remainder in ms
    song_lengths.append(f"{minutes}:{ms//1000:02}")
df['song length'] = song_lengths

st.subheader('Recently Played Songs')
st.dataframe(df[['song info', 'song length']])

### get top songs based on input time range, returns list of track objects
def top_songs(time_range, limit=20):
    songs = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    songs = songs['items']
    return songs

### button functions for top songs
st.write("User's top songs")
s_artist, m_artist, l_artist = st.columns(3)
time_frame = 'short_term'
if s_artist.button('Short time frame'):
    st.write('Short term')
    time_frame = 'short_term'
if m_artist.button('Medium time frame'):
    st.write('Medium term')
    time_frame = 'medium_term'
if l_artist.button('Long time frame'):
    st.write('Long term')
    time_frame = 'long_term'

### button function to display and create playlist of top songs
def disable_button(key):
    st.session_state[key] = True

buttons = ['button_pressed']
for key in buttons:
    if key not in st.session_state:
        st.session_state[key] = False


### initially only wanted this button to operate once, but realized better functionality
### when able to be used more than once in a single sitting
if st.button('Top Songs'):
    song_list = top_songs(time_frame)
    st.write(song_list)

if st.button('create playlist', on_click=disable_button, args=('button_pressed',), disabled=st.session_state.button_pressed):
    st.write('Creating playlist, finished product will be found in your Spotify library.')
