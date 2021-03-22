from spotify_api import SpotifyAPI, client_id, client_secret
import pandas as pd
import streamlit as st
import time


if __name__ == "__main__":
    st.title('Spotify Explorer')
    client = SpotifyAPI(client_id, client_secret)
    # Invoke streamlit
    stsearch = st.text_input(
        "Enter the search item (song/artist/album or track) you want to search for")

    if stsearch != "":
        with st.spinner('Calling all stations...'):
            time.sleep(2)
        all = client.get_meta(stsearch, search_type="track")
        df = pd.DataFrame(
            all, columns=['track_name', 'track_id', 'artist_name', 'artist_id', 'images'])
        st.image(df['images'][0])
        artistid = df['artist_id'].iloc[0]
        trackid = df['track_id'].iloc[0]
        # client.get_recomended_songs(limit=10)
    st.title(f'For {stsearch.title()} Spotify Recommends...')
    add_selectbox = st.selectbox(
        'How many songs to recommend ? ', ('', '10', '20', '30', '50', '100'))
    if add_selectbox != "":
        reccs = client.get_reccomended_songs(
            limit=add_selectbox, seed_artists=str(artistid), seed_tracks=str(trackid))
        st.text('Spotify Recommends...')
        df2 = pd.DataFrame(reccs, columns=["Songs", "Artists", "Link"]).rename_axis(
            'Index', axis=1)
        st.table(df2)
        link = '[GitHub](https://github.com/vishwanath79/spotifier)'
        st.markdown(link, unsafe_allow_html=True)
