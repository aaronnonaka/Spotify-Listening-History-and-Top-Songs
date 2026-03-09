# Spotify-Listening-History-and-Top-Songs
Python application that queries Spotify API to gather user listing data

Features:
- Utilizes Spotipy library to make calls for listening data for user
- Processes data and displays results, such as song name, artist, album, and song length, using Streamlit web application and Pandas data library
- Interactive interface to allow user to choose what time range to query for top songs
- Creates and populates Spotify playlist on to user's account based on collected songs

Usage:
- Acquire user credentials for use of the Spotify API: client id, and client secret
- Run the project using Streamlit: "streamlit run main.py"
- Listening history will automatically be queried and displayed when web application launches
- Select from the 3 button options for time range you wish to search for your top songs
- Short term: last ~4 weeks; Medium term: last ~6 months; Long term: about ~1 year
- Press the "Top Songs" button to generate a table with your top 20 songs, in order
- Press the "Create Playlist" button to create a public playlist on your Spotify account, with those top 20 songs in it

Screenshots:
Recent History listing your 25 most recent songs listened
<img width="1112" height="1004" alt="image" src="https://github.com/user-attachments/assets/386f8b8e-0381-4e0c-8c43-0edafc00eaa8" />

Top songs also being displayed after user makes selections
<img width="728" height="1168" alt="image" src="https://github.com/user-attachments/assets/8a479709-0f22-43b4-8bce-660938f52fff" />

Playlist created on the Spotify user's account
<img width="1563" height="1198" alt="image" src="https://github.com/user-attachments/assets/fd777599-5b54-4160-a7cd-0c5fc00063d2" />
