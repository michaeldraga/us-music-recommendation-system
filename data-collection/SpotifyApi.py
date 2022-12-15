from aiohttp import ClientSession
import time
import json
import base64
from typing import MutableSequence, Union


def format_query(**kwargs):
    return '&'.join([f'{key}={value}' for key, value in kwargs.items()])


def print_json(data: dict):
    print(json.dumps(data, indent=4))

class SpotifyApi:
    def __init__(self, client_id, client_secret, session: ClientSession):
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = session
        self.load_cache()

    cache = {
        'artists': {},
        'playlists': {},
        'tracks': {},
        'categories': {}
    }
    cache_hits = 0

    def save_to_cache(self, type: str, key: str, value: any):
        self.cache[type][key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def get_from_cache(self, key: str, id: str):
        try:
            if id in self.cache[key] and time.time() - self.cache[key][id]['timestamp'] < 60 * 60 * 24:
                    self.cache_hits += 1
                    return self.cache[key][id]['value']
        except KeyError:
            pass
        return None

    def save_cache(self):
        with open('cache.json', 'w') as file:
            json.dump(self.cache, file)
    
    def load_cache(self):
        try:
            with open('cache.json', 'r') as file:
                self.cache = json.load(file)
        except FileNotFoundError:
            pass

    class AudioFeatures:
        def __init__(self, track_id: str, danceability: float, energy: float, key: int, loudness: float, mode: int, speechiness: float, acousticness: float, instrumentalness: float, liveness: float, valence: float, tempo: float, time_signature: int):
            self.track_id = track_id
            self.danceability = danceability
            self.energy = energy
            self.key = key
            self.loudness = loudness
            self.mode = mode
            self.speechiness = speechiness
            self.acousticness = acousticness
            self.instrumentalness = instrumentalness
            self.liveness = liveness
            self.valence = valence
            self.tempo = tempo
            self.time_signature = time_signature
        
        def __repr__(self):
            return f'AudioFeatures({self.track_id})'
        
        def __str__(self):
            str = 'AudioFeatures(\n'
            for key, value in self.__dict__.items():
                str += f'\t{key}: {value}\n'
            str += ')'
            return str

        @staticmethod
        def from_response(data: dict) -> 'SpotifyApi.AudioFeatures':
            return SpotifyApi.AudioFeatures(
                track_id=data['track_href'].split('/')[-1],
                danceability=data['danceability'],
                energy=data['energy'],
                key=data['key'],
                loudness=data['loudness'],
                mode=data['mode'],
                speechiness=data['speechiness'],
                acousticness=data['acousticness'],
                instrumentalness=data['instrumentalness'],
                liveness=data['liveness'],
                valence=data['valence'],
                tempo=data['tempo'],
                time_signature=data['time_signature']
            )

        

    class Artist:
        def __init__(self, id: str, name: str, genres: list[str], uri: str) -> None:
            self.id = id
            self.name = name
            self.genres = genres
            self.uri = uri

        def __str__(self) -> str:
            str = 'Artist(\n'
            for key, value in self.__dict__.items():
                str += f'\t{key}: {value}\n'
            str += ')'
            return str

        def __repr__(self) -> str:
            return f'Artist({self.id}, {self.name})'

        @staticmethod
        def from_response(data: dict):
            # print(data)
            return SpotifyApi.Artist(
                data['id'],
                data['name'],
                None,
                data['uri'],
            )

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'genres': self.genres,
                'uri': self.uri
            }
        
        @staticmethod
        def from_dict(data: dict):
            return SpotifyApi.Artist(
                data['id'],
                data['name'],
                data['genres'],
                data['uri']
            )

    class Album:
        def __init__(self, id: str, name: str, uri: str, artists: list['SpotifyApi.Artist']):
            self.id = id
            self.name = name
            self.uri = uri
            self.artists = artists

        def __str__(self) -> str:
            str = 'Album(\n'
            for key, value in self.__dict__.items():
                str += f'\t{key}: {value}\n'
            str += ')'
            return str

        def __repr__(self) -> str:
            return f'Album({self.id}, {self.name})'

        @staticmethod
        def from_response(data: dict):
            return SpotifyApi.Album(
                data['id'],
                data['name'],
                data['uri'],
                [SpotifyApi.Artist.from_response(artist) for artist in data['artists']]
            )

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'uri': self.uri,
                'artists': [artist.to_dict() for artist in self.artists]
            }
        
        @staticmethod
        def from_dict(data: dict):
            return SpotifyApi.Album(
                data['id'],
                data['name'],
                data['uri'],
                [SpotifyApi.Artist.from_dict(artist) for artist in data['artists']]
            )

    class Playlist:
        def __init__(self, collaborative: bool, description: str, id: str, name: str, uri: str):
            self.collaborative = collaborative
            self.description = description
            self.id = id
            self.name = name
            self.uri = uri

        def __str__(self) -> str:
            str = 'Playlist(\n'
            for key, value in self.__dict__.items():
                str += f'\t{key}: {value}\n'
            str += ')'
            return str

        def __repr__(self) -> str:
            return f'Playlist({self.id}, {self.name})'

        @staticmethod
        def from_response(data: dict):
            # print(data)
            return SpotifyApi.Playlist(
                data['collaborative'],
                data['description'],
                data['id'],
                data['name'],
                data['uri']
            )

        def to_dict(self):
            return {
                'collaborative': self.collaborative,
                'description': self.description,
                'id': self.id,
                'name': self.name,
                'uri': self.uri
            }
        
        @staticmethod
        def from_dict(data: dict):
            return SpotifyApi.Playlist(
                data['collaborative'],
                data['description'],
                data['id'],
                data['name'],
                data['uri']
            )

    class Track:
        def __init__(self, id: str, album: 'SpotifyApi.Album', artists_ids: list[str], disc_number: int, duration_ms: int, explicit: bool, is_local: bool, name: str, popularity: int, track_number: int, preview_url: str, uri: str):
            self.id = id
            self.album = album
            self.artists_ids = artists_ids
            self.disc_number = disc_number
            self.duration_ms = duration_ms
            self.explicit = explicit
            self.is_local = is_local
            self.name = name
            self.popularity = popularity
            self.track_number = track_number
            self.preview_url = preview_url
            self.uri = uri

        def __str__(self) -> str:
            str = 'Track(\n'
            for key, value in self.__dict__.items():
                str += f'\t{key}: {value}\n'
            str += ')'
            return str

        def __repr__(self) -> str:
            return f'Track({self.id}, {self.name})'

        @staticmethod
        def from_response(data: dict):
            return SpotifyApi.Track(
                data['id'],
                SpotifyApi.Album.from_response(data['album']),
                [artist['id'] for artist in data['artists']],
                data['disc_number'],
                data['duration_ms'],
                data['explicit'],
                data['is_local'],
                data['name'],
                data['popularity'],
                data['track_number'],
                data['preview_url'],
                data['uri']
            )
        
        def to_dict(self):
            return {
                'id': self.id,
                'album': self.album.to_dict(),
                'artists_ids': self.artists_ids,
                'disc_number': self.disc_number,
                'duration_ms': self.duration_ms,
                'explicit': self.explicit,
                'is_local': self.is_local,
                'name': self.name,
                'popularity': self.popularity,
                'track_number': self.track_number,
                'preview_url': self.preview_url,
                'uri': self.uri
            }
        
        @staticmethod
        def from_dict(data: dict):
            return SpotifyApi.Track(
                data['id'],
                SpotifyApi.Album.from_dict(data['album']),
                data['artists_ids'],
                data['disc_number'],
                data['duration_ms'],
                data['explicit'],
                data['is_local'],
                data['name'],
                data['popularity'],
                data['track_number'],
                data['preview_url'],
                data['uri']
            )


    class TrackFeatures:
        def __init__(self, id: str, acousticness: float, danceability: float, energy: float, instrumentalness: float, key: int, liveness: float, loudness: float, mode: int, speechiness: float, tempo: float, time_signature: int, valence: float) -> None:
            self.id = id
            self.acousticness = acousticness
            self.danceability = danceability
            self.energy = energy
            self.instrumentalness = instrumentalness
            self.key = key
            self.liveness = liveness
            self.loudness = loudness
            self.mode = mode
            self.speechiness = speechiness
            self.tempo = tempo
            self.time_signature = time_signature
            self.valence = valence

        def __str__(self) -> str:
            str = 'Track(\n'
            for key, value in self.__dict__.items():
                str += f'\t{key}: {value}\n'
            str += ')'
            return str

        def __repr__(self) -> str:
            return f'Track({self.id}, {self.name})'

        @staticmethod
        def from_response(data: dict):
            return SpotifyApi.Track(
                data['id'],
                data['acousticness'],
                data['danceability'],
                data['energy'],
                data['instrumentalness'],
                data['key'],
                data['liveness'],
                data['loudness'],
                data['mode'],
                data['speechiness'],
                data['tempo'],
                data['time_signature'],
                data['valence']
            )

    class TrackWithFeatures:
        def __init__(self, track: 'SpotifyApi.Track', features: 'SpotifyApi.TrackFeatures') -> None:
            self.track = track
            self.features = features

        def __str__(self) -> str:
            str = 'TrackWithFeatures(\n'
            for key, value in self.__dict__.items():
                str += f'\t{key}: {value}\n'
            str += ')'
            return str

        def __repr__(self) -> str:
            return f'TrackWithFeatures({self.track.id}, {self.track.name})'

        @staticmethod
        def from_response(track_data: dict, features_data: dict):
            return SpotifyApi.TrackWithFeatures(
                SpotifyApi.Track.from_response(track_data),
                SpotifyApi.TrackFeatures.from_response(features_data)
            )


    class StoredToken:
        def __init__(self, access_token: str, token_type: str, expires_in: int, created_at: int) -> None:
            self.access_token = access_token
            self.token_type = token_type
            self.expires_in = expires_in
            self.created_at = created_at

        @staticmethod
        def from_stored_json(data: dict) -> 'SpotifyApi.StoredToken':
            return SpotifyApi.StoredToken(
                data['access_token'],
                data['token_type'],
                data['expires_in'],
                data['created_at']
            )

        def is_expired(self) -> bool:
            return self.created_at + self.expires_in < time.time()

        def __str__(self) -> str:
            return json.dumps({
                'access_token': self.access_token,
                'token_type': self.token_type,
                'expires_in': self.expires_in,
                'created_at': self.created_at
            })

        def to_json(self) -> str:
            return str(self)

        @staticmethod
        def from_json(json_str: str) -> 'SpotifyApi.StoredToken':
            data = json.loads(json_str)
            return SpotifyApi.StoredToken(
                access_token=data['access_token'],
                token_type=data['token_type'],
                expires_in=data['expires_in'],
                created_at=data['created_at']
            )

        @staticmethod
        def from_response(response: dict) -> 'SpotifyApi.StoredToken':
            return SpotifyApi.StoredToken(
                access_token=response['access_token'],
                token_type=response['token_type'],
                expires_in=response['expires_in'],
                created_at=time.time()
            )

    async def __aenter__(self):
        print('enter async context')
        await self.initialize_authentication(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __authenticate_using_credentials(self, session: ClientSession):
        url = 'https://accounts.spotify.com/api/token'
        params = {
            'grant_type': 'client_credentials'
        }
        headers = {
            'Authorization': 'Basic {}'.format(base64.b64encode('{}:{}'.format(self.client_id, self.client_secret).encode('utf-8')).decode('utf-8'))
        }
        try:
            async with session.post(url, data=params, headers=headers) as response:
                content = await response.json()
                return (url, 'OK', content)
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)

    async def initialize_authentication(self, session: ClientSession) -> None:
        global spotify_access_token
        stored_token = self.__get_stored_token()

        if stored_token is None or stored_token.is_expired():
            if stored_token is None:
                print(
                    'No stored token found. Retrieving a new one using client credentials.')
            else:
                print(
                    'Stored token is expired. Retrieving a new one using client credentials.')

            (_, status, data) = await self.__authenticate_using_credentials(session)
            if status != 'OK':
                print('Failed to retrieve token.')
                return
            stored_token = SpotifyApi.StoredToken.from_response(data)
            self.__store_token(stored_token)
            print('Using new token {}'.format(stored_token.access_token))
        else:
            print('Using stored token: {}'.format(stored_token))

        self.access_token = stored_token.access_token

    def __get_stored_token(self) -> 'SpotifyApi.StoredToken':
        try:
            with open('token.json', 'r') as f:
                data = json.load(f)
                return SpotifyApi.StoredToken.from_stored_json(data)
        except:
            return None

    def __store_token(self, token: Union[dict, 'SpotifyApi.StoredToken']):
        with open('token.json', 'w') as f:
            if type(token) is SpotifyApi.StoredToken:
                token = token.__dict__

            json.dump(token, f)

    def __get_auth_header(self) -> dict:
        return {'Authorization': 'Bearer {}'.format(self.access_token)}

    async def fetch_all_categories(self, session: ClientSession, offset=0, limit=20, locale='en_EN'):
        url = 'https://api.spotify.com/v1/browse/categories?{}'.format(
            format_query(offset=offset, limit=limit, locale=locale))
        try:
            async with session.get(url, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()

                print_json(content)

                # for c in content['categories']['items']:
                #     self.save_to_cache('categories', c['id'], c)

                # return (url, 'OK', [self.get_from_cache('categories', c['id']) for c in content['categories']['items']])
                return (url, 'OK', content['categories']['items'])
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)

    async def fetch_all_playlists_in_category(self, session: ClientSession, category_id: str, offset=0, limit=20, country='US'):
        # return cached playlists if available
        # if category_id in self.cache['categories']:
        #     print(self.get_from_cache('categories', category_id))
        #     for playlist_id in [self.get_from_cache('playlists', playlist['id']) for playlist in self.get_from_cache('categories', category_id)]:
        #         print(self.get_from_cache('playlists', playlist_id))
        #     return (None, 'OK', [SpotifyApi.Playlist.from_dict(self.get_from_cache('playlists', playlist_id)) for playlist_id in self.get_from_cache('categories', category_id)])

        url = 'https://api.spotify.com/v1/browse/categories/{}/playlists?{}'.format(
            category_id, format_query(offset=offset, limit=limit, country=country))
        try:
            async with session.get(url, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()

                if content is None:
                    return (url, 'ERROR', response.text())

                playlists = [SpotifyApi.Playlist.from_response(
                    p) for p in content['playlists']['items']]
                
                self.save_to_cache('categories', category_id, [p.to_dict() for p in playlists])

                return (url, 'OK', playlists)
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)

    async def fetch_all_tracks_in_playlist(self, session: ClientSession, playlist_id: str, offset=0, limit=100):
        # return cached tracks if available
        if playlist_id in self.cache['playlists']:
            print('cache hit playlist')
            return (None, 'OK', [SpotifyApi.Track.from_dict(self.get_from_cache('tracks', track_id)) for track_id in self.get_from_cache('playlists', playlist_id)])

        url = 'https://api.spotify.com/v1/playlists/{}/tracks?{}'.format(
            playlist_id, format_query(offset=offset, limit=limit))
        try:
            async with session.get(url, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()

                if content is None:
                    return (url, 'ERROR', response.text())

                tracks = [SpotifyApi.Track.from_response(a['track']) for a in content['items']]

                # for track in tracks:
                #     for i in range(len(track.artists)):
                #         artist = track.artists[i]
                #         if artist.id in self.cache['artists']:
                #             track.artists[i] = self.cache['artists'][artist.id]
                #         else:
                #             (_, _, newArtist) = await self.fetch_artist(session, artist.id)
                #             artistObject = SpotifyApi.Artist.from_response(newArtist)
                #             artistObject.genres = newArtist['genres']
                #             self.cache['artists'][artist.id] = artistObject
                #             track.artists[i] = self.cache['artists'][artist.id]

                for track in tracks:
                    self.save_to_cache('tracks', track.id, track.to_dict())
                
                self.save_to_cache('playlists', playlist_id, [track.id for track in tracks])

                return (url, 'OK', tracks)

        except Exception as e:
            print('error')
            print(e)
            return (url, 'ERROR', None)

    async def fetch_track(self, session: ClientSession, id: str):
        url = 'https://api.spotify.com/v1/tracks/{}'.format(id)
        try:
            async with session.get(url, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()
                return (url, 'OK', content)
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)

    async def fetch_many_tracks(self, session: ClientSession, ids: MutableSequence[str]):
        if len(ids) == 0:
            return []
        elif len(ids) > 50:
            print('Warning: You passed more than 50 ids. Only the first 50 will be used.')
            ids = ids[:50]

        url = 'https://api.spotify.com/v1/tracks'
        params = {
            'ids': ','.join(filter(lambda id: id not in self.cache['tracks'] ,ids))
        }
        try:
            async with session.get(url, params=params, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()
                tracks = [SpotifyApi.Track.from_response(a) for a in content['tracks']]
                print('am i even here? wtf')
                for track in tracks:
                    print('but here though')
                    for i in range(len(track.artists_ids)):
                        print('here please')
                        artist = track.artists_ids[i]
                        if artist.id in self.cache['artists']:
                            track.artists_ids[i] = self.cache['artists'][artist.id]
                        else:
                            (_, _, newArtist) = await self.fetch_artist(session, artist.id)
                            self.cache['artists'][artist.id] = newArtist
                            track.artists_ids[i] = self.cache['artists'][artist.id]

                    self.cache['tracks'][track.id] = track

                return (url, 'OK', [self.cache['tracks'][track_id] for track_id in ids])
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)
    
    async def fetch_artist(self, session: ClientSession, id: str):
        url = 'https://api.spotify.com/v1/artists/{}'.format(id)
        try:
            async with session.get(url, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()
                return (url, 'OK', content)
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)

    async def fetch_many_artists(self, session: ClientSession, ids: MutableSequence[str]):
        if len(ids) == 0:
            return []
        elif len(ids) > 50:
            print('Warning: You passed more than 50 ids. Only the first 50 will be used.')
            ids = ids[:50]

        url = 'https://api.spotify.com/v1/artists'
        params = {
            'ids': ','.join(filter(lambda id: id not in self.cache['artists'] ,ids))
        }
        try:
            async with session.get(url, params=params, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()
                artists = [SpotifyApi.Artist.from_response(a) for a in content['artists']]

                for artist in artists:
                    self.save_to_cache('artists', artist.id, artist.to_dict())
                
                return (url, 'OK', [SpotifyApi.Artist.from_dict(self.cache['artists'][artist_id]) for artist_id in ids])
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)

    async def fetch_audio_analysis(self, session: ClientSession, id: str):
        url = 'https://api.spotify.com/v1/audio-analysis/{}'.format(id)
        try:
            async with session.get(url, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()
                return (url, 'OK', content)
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)

    async def fetch_audio_features(self, session: ClientSession, id: str):
        url = 'https://api.spotify.com/v1/audio-features/{}'.format(id)
        try:
            async with session.get(url, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()

                if content is None:
                    print(response.status)
                    return (url, 'ERROR', response.text())

                return (url, 'OK', content)
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)

    async def fetch_audio_features_for_tracks(self, session: ClientSession, ids: MutableSequence[str]):
        if len(ids) == 0:
            return []
        elif len(ids) > 100:
            print(
                'Warning: You passed more than 100 ids. Only the first 100 will be used.')
            ids = ids[:100]

        url = 'https://api.spotify.com/v1/audio-features'
        params = {
            'ids': ','.join(ids)
        }
        try:
            async with session.get(url, params=params, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()
                features = [SpotifyApi.AudioFeatures.from_response(f) for f in content['audio_features']]
                return (url, 'OK', features)
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)
