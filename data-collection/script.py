import random
import time
import array
import itertools
from typing import Tuple, MutableSequence, Union
import os
import aiohttp
from aiohttp import ClientSession
import asyncio
from SpotifyApi import SpotifyApi
import dotenv
import json
import base64

dotenv.load_dotenv()

spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
spotify_access_token = None


def print_json(data: dict):
    print(json.dumps(data, indent=4))


async def main():
    global spotify_access_token
    demo_track_id = '11dFghVXANMlKmJXsNCbNl'

    async with aiohttp.ClientSession() as session:
        async with SpotifyApi(client_id=spotify_client_id, client_secret=spotify_client_secret, session=session) as spotify:
            (_, status, data) = await spotify.fetch_track(session, demo_track_id)
            print_json(data)
            (_, status, data) = await spotify.fetch_audio_analysis(session, demo_track_id)
            print_json(data)
            (_, status, data) = await spotify.fetch_audio_features(session, demo_track_id)
            print_json(data)
            (_, status, data) = await spotify.fetch_many_tracks(session, [demo_track_id, demo_track_id, demo_track_id])
            print_json(data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
