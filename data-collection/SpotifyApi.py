from aiohttp import ClientSession
import time
import json
import base64
from typing import MutableSequence, Union

class StoredToken:
    def __init__(self, access_token: str, token_type: str, expires_in: int, created_at: int) -> None:
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.created_at = created_at

    @staticmethod
    def from_stored_json(data: dict) -> 'StoredToken':
        return StoredToken(
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
    def from_json(json_str: str) -> 'StoredToken':
        data = json.loads(json_str)
        return StoredToken(
            access_token=data['access_token'],
            token_type=data['token_type'],
            expires_in=data['expires_in'],
            created_at=data['created_at']
        )

    @staticmethod
    def from_response(response: dict) -> 'StoredToken':
        return StoredToken(
            access_token=response['access_token'],
            token_type=response['token_type'],
            expires_in=response['expires_in'],
            created_at=time.time()
        )


class SpotifyApi:
    def __init__(self, client_id, client_secret, session: ClientSession):
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = session

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
                print('No stored token found. Retrieving a new one using client credentials.')
            else:
                print('Stored token is expired. Retrieving a new one using client credentials.')

            (_, status, data) = await self.__authenticate_using_credentials(session)
            if status != 'OK':
                print('Failed to retrieve token.')
                return
            stored_token = StoredToken.from_response(data)
            self.__store_token(stored_token)
            print('Using new token {}'.format(stored_token.access_token))
        else:
            print('Using stored token: {}'.format(stored_token))

        self.access_token = stored_token.access_token

    def __get_stored_token(self) -> StoredToken:
        try:
            with open('token.json', 'r') as f:
                data = json.load(f)
                return StoredToken.from_stored_json(data)
        except:
            return None


    def __store_token(self, token: Union[dict, StoredToken]):
        with open('token.json', 'w') as f:
            if type(token) is StoredToken:
                token = token.__dict__

            json.dump(token, f)


    def __get_auth_header(self) -> dict:
        return {'Authorization': 'Bearer {}'.format(self.access_token)}


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
            'ids': ','.join(ids)
        }
        try:
            async with session.get(url, params=params, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()
                return (url, 'OK', content)
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
                return (url, 'OK', content)
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)

    async def fetch_many_audio_features(self, session: ClientSession, ids: MutableSequence[str]):
        if len(ids) == 0:
            return []
        elif len(ids) > 100:
            print('Warning: You passed more than 100 ids. Only the first 100 will be used.')
            ids = ids[:100]

        url = 'https://api.spotify.com/v1/audio-features'
        params = {
            'ids': ','.join(ids)
        }
        try:
            async with session.get(url, params=params, headers=({} | self.__get_auth_header())) as response:
                content = await response.json()
                return (url, 'OK', content)
        except Exception as e:
            print(e)
            return (url, 'ERROR', None)




