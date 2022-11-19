import random
import time
import array
import itertools
from typing import Tuple, MutableSequence, Union
import os
import aiohttp
from aiohttp import ClientSession
import asyncio
import dotenv
import json
import base64

dotenv.load_dotenv()

spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
spotify_access_token = None


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


def get_stored_token() -> StoredToken:
    try:
        with open('token.json', 'r') as f:
            data = json.load(f)
            return StoredToken.from_stored_json(data)
    except:
        return None


def store_token(token: Union[dict, StoredToken]):
    with open('token.json', 'w') as f:
        if type(token) is StoredToken:
            token = token.__dict__

        json.dump(token, f)


def get_auth_header() -> dict:
    return {'Authorization': 'Bearer {}'.format(spotify_access_token)}


async def authenticate_using_credentials(session: ClientSession):
    url = 'https://accounts.spotify.com/api/token'
    params = {
        'grant_type': 'client_credentials'
    }
    headers = {
        'Authorization': 'Basic {}'.format(base64.b64encode('{}:{}'.format(spotify_client_id, spotify_client_secret).encode('utf-8')).decode('utf-8'))
    }
    try:
        async with session.post(url, data=params, headers=headers) as response:
            content = await response.json()
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)

async def initialize_authentication(session: ClientSession) -> None:
    global spotify_access_token
    stored_token = get_stored_token()

    if stored_token is None:
        print('No stored token found. Retrieving a new one using client credentials.')
        (_, status, data) = await authenticate_using_credentials(session)
        if status != 'OK':
            print('Failed to retrieve token.')
            return
        stored_token = StoredToken.from_response(data)
        store_token(stored_token)

    if stored_token.is_expired():
        print('Stored token is expired. Retrieving a new one using client credentials.')
        (_, status, data) = await authenticate_using_credentials(session)
        if status != 'OK':
            print('Failed to retrieve token.')
            return
        store_token(data)
        stored_token = data

    print('Using token: {}'.format(stored_token))
    spotify_access_token = stored_token.access_token

async def fetch_track(session: ClientSession, id: str):
    url = 'https://api.spotify.com/v1/tracks/{}'.format(id)
    try:
        async with session.get(url, headers=({} | get_auth_header())) as response:
            content = await response.json()
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)

async def fetch_audio_analysis(session: ClientSession, id: str):
    url = 'https://api.spotify.com/v1/audio-analysis/{}'.format(id)
    try:
        async with session.get(url, headers=({} | get_auth_header())) as response:
            content = await response.json()
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)

async def fetch_audio_features(session: ClientSession, id: str):
    url = 'https://api.spotify.com/v1/audio-features/{}'.format(id)
    try:
        async with session.get(url, headers=({} | get_auth_header())) as response:
            content = await response.json()
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)

def print_json(data: dict):
    print(json.dumps(data, indent=4))

async def main():
    global spotify_access_token
    demo_track_id = '11dFghVXANMlKmJXsNCbNl'

    async with aiohttp.ClientSession() as session:
        await initialize_authentication(session)        
        (_, status, data) = await fetch_track(session, demo_track_id)
        print_json(data)
        (_, status, data) = await fetch_audio_analysis(session, demo_track_id)
        print_json(data)
        (_, status, data) = await fetch_audio_features(session, demo_track_id)
        print_json(data)

        
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
