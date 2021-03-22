
import os
import requests
import spotipy
import base64
# To access authorised Spotify data
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import datetime

user_id = os.environ['SPOTIFY_USER_ID']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']


scope = 'user-top-read'


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id, client_secret, *args, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret

    # Given a client id and client secret, gets client credentials from the Spotify API.
    def get_client_credentials(self):
        ''' Returns a base64 encoded string '''
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("check client IDs")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_header(self):  # Get header
        client_creds_b64 = self.get_client_credentials()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self):  # Get token
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):  # perform auth only if access token has expired
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_header()

        r = requests.post(token_url, data=token_data, headers=token_headers)

        if r.status_code not in range(200, 299):
            print("Could not authenticate client")
        data = r.json()
        now = datetime.datetime.now()
        access_token = data["access_token"]
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):

        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    # search for an artist/track based on a search type provided
    def search(self, query, search_type="artist"):
        access_token = self.get_access_token()
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer { access_token}"}
        # using the  search API at https://developer.spotify.com/documentation/web-api/reference/search/search/
        search_url = "https://api.spotify.com/v1/search?"
        data = {"q": query, "type": search_type.lower()}
        from urllib.parse import urlencode
        search_url_formatted = urlencode(data)
        search_r = requests.get(
            search_url+search_url_formatted, headers=headers)
        if search_r.status_code not in range(200, 299):
            print("Encountered isse=ue")
            return search_r.json()
        return search_r.json()

    def get_meta(self, query, search_type="track"):  # meta data of a track
        resp = self.search(query, search_type)
        all = []
        for i in range(len(resp['tracks']['items'])):
            track_name = resp['tracks']['items'][i]['name']
            track_id = resp['tracks']['items'][i]['id']
            artist_name = resp['tracks']['items'][i]['artists'][0]['name']
            artist_id = resp['tracks']['items'][i]['artists'][0]['id']
            album_name = resp['tracks']['items'][i]['album']['name']
            images = resp['tracks']['items'][i]['album']['images'][0]['url']

            raw = [track_name, track_id, artist_name, artist_id, images]
            all.append(raw)

        return all

    def get_reccomended_songs(self, limit=5, seed_artists='', seed_tracks='', market="US",
                              seed_genres="rock", target_danceability=0.1):  # reccomendations API
        access_token = self.get_access_token()
        endpoint_url = "https://api.spotify.com/v1/recommendations?"
        all_recs = []
        self.limit = limit
        self.seed_artists = seed_artists
        self.seed_tracks = seed_tracks
        self.market = market
        self.seed_genres = seed_genres
        self.target_danceability = target_danceability

        # API query plus some additions
        query = f'{endpoint_url}limit={limit}&market={market}&seed_genres={seed_genres}&target_danceability={target_danceability}'
        query += f'&seed_artists={seed_artists}'
        query += f'&seed_tracks={seed_tracks}'
        response = requests.get(query, headers={
                                "Content-type": "application/json", "Authorization": f"Bearer {access_token}"})
        json_response = response.json()

        # print(json_response)
        if response:
            print("Reccomended songs")
            for i, j in enumerate(json_response['tracks']):
                track_name = j['name']
                artist_name = j['artists'][0]['name']
                link = j['artists'][0]['external_urls']['spotify']

                print(f"{i+1}) \"{j['name']}\" by {j['artists'][0]['name']}")
                reccs = [track_name, artist_name, link]
                all_recs.append(reccs)
            return all_recs
