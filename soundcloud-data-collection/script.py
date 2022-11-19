import random
import time
import array
import itertools
from typing import Tuple, MutableSequence
import os
import aiohttp
from aiohttp import ClientSession
import asyncio
import dotenv

dotenv.load_dotenv()

soundcloud_client_id = os.getenv('SOUNDCLOUD_CLIENT_ID')
soundcloud_client_secret = os.getenv('SOUNDCLOUD_CLIENT_SECRET')

soundcloud_oauth_token = '2-293426--5bqiwZgbWKbdvk5ghnBnhRO'


def get_auth_header():
    return {'Authorization': 'OAuth {}'.format(soundcloud_oauth_token)}


async def fetch_oauth_client_token(session: ClientSession):
    url = 'https://api.soundcloud.com/oauth2/token'
    params = {
        'client_id': soundcloud_client_id,
        'client_secret': soundcloud_client_secret,
        'grant_type': 'client_credentials'
    }
    try:
        async with session.post(url, data=params) as response:
            content = await response.json()
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)


async def fetch_track(session: ClientSession, id: int):
    url = 'https://api.soundcloud.com/tracks/{}'.format(id)

    try:
        async with session.get(url, headers=({} | get_auth_header())) as response:
            content = await response.json()
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)


async def fetch_tracks(session: ClientSession, ids: MutableSequence[int]):
    tasks = []
    for id in ids:
        tasks.append(asyncio.create_task(fetch_track(session, id)))

    responses = await asyncio.gather(*tasks)
    return responses


async def fetch_favoriters(session: ClientSession, track_id: int) -> Tuple[str, str, array.array]:
    url = 'https://api.soundcloud.com/tracks/{}/favoriters'.format(track_id)

    try:
        async with session.get(url, headers=({} | get_auth_header())) as response:
            content = await response.json()
            time.sleep(0.05)
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)


async def fetch_user(session: ClientSession, id: int):
    url = 'https://api.soundcloud.com/users/{}'.format(id)

    try:
        async with session.get(url, headers=(get_auth_header())) as response:
            content = await response.json()
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)


async def fetch_liked_tracks(session: ClientSession, user_id: int):
    url = 'https://api.soundcloud.com/users/{}/likes/tracks'.format(user_id)

    try:
        async with session.get(url, params={'limit': 100}, headers=({} | get_auth_header())) as response:
            content = await response.json()
            time.sleep(0.05)
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)


async def fetch_test_api(session: ClientSession, i: int):
    url = 'https://postman-echo.com/get?q={}'.format(i)
    try:
        async with session.get(url) as response:
            content = await response.json()
            return (url, 'OK', content)
    except Exception as e:
        print(e)
        return (url, 'ERROR', None)


def get_list_content_from_many_response(response: MutableSequence[Tuple[str, str, array.array]]):
    content = map(lambda x: x[2], response)
    return list(content)

async def gather_with_concurrency(n, *coros):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros))


visited_tracks: set[int] = set()
visited_users: set[int] = set()
tracks: dict[int, any] = {}

# {
#  "id": 1309196527,
#  "created_at": "2016/03/29 17:00:00 +0000",
#  "user_id": 100000,
#  "track_data": { ... }
# }

demo = False


async def main():
    track_id = 1309196527
    tasks = []

    next_track_ids = [track_id]

    if demo:
        async with aiohttp.ClientSession() as session:
            # soundcloud_oauth_token = (await fetch_oauth_client_token(session))[2]['access_token']
            # print('fetched new token')
            # print(soundcloud_oauth_token)
            (_, _, track) = await fetch_track(session, track_id)
            # print(track)
            (_, _, favoriters) = await fetch_favoriters(session, track_id)
            # print(favoriters)
            (_, _, user) = await fetch_user(session, track['user']['id'])
            names = map(lambda x: x['username'], favoriters)
            ids = map(lambda x: x['id'], favoriters)
            print(list(ids))
            # print(user)
            (_, _, liked_tracks) = await fetch_liked_tracks(session, track['user']['id'])
            titles = map(lambda x: x['title'], liked_tracks)
            print(list(titles))
            # for i in range(20):
            #     tasks.append(asyncio.create_task(fetch_test_api(session, i)))
            # responses = await asyncio.gather(*tasks)
            # for response in responses:
            #     print(response)
    else:
        async with aiohttp.ClientSession() as session:
            global soundcloud_oauth_token
            # soundcloud_oauth_token = (await fetch_oauth_client_token(session))[2]['access_token']
            print(soundcloud_oauth_token)

            counter = 0
            while counter < 2:
                counter += 1
                print('iteration {}'.format(counter))
                print(next_track_ids)
                next_tracks = await fetch_tracks(session, next_track_ids)
                print(next_tracks)
                liking_users_responses = await gather_with_concurrency(50, *map(lambda x: fetch_favoriters(session, x[2]['id']), next_tracks))
                # print(liking_users_responses)
                liking_users = get_list_content_from_many_response(
                    liking_users_responses)
                flat_liking_users = list(
                    itertools.chain.from_iterable(liking_users))
                liking_users_ids = list(
                    map(lambda x: x['id'], flat_liking_users))

                liked_tracks_tasks = []
                for user_id in liking_users_ids:
                    if user_id not in visited_users:
                        visited_users.add(user_id)
                        liked_tracks_tasks.append(asyncio.create_task(
                            fetch_liked_tracks(session, user_id)))
                liked_tracks_responses = await gather_with_concurrency(50, *liked_tracks_tasks)
                liked_tracks = list(itertools.chain.from_iterable(
                    get_list_content_from_many_response(liked_tracks_responses)))
                # print(liked_tracks)

                next_track_ids = []
                for track in liked_tracks:
                    if track['id'] not in visited_tracks:
                        visited_tracks.add(track['id'])
                        tracks[track['id']] = {
                            'id': track['id'],
                            'created_at': time.time(),
                            'track_data': track
                        }
                        next_track_ids.append(track['id'])
                print(next_track_ids)
                print(tracks.keys())
                print('next_track_ids', len(next_track_ids))
                print('visited_tracks', len(visited_tracks))
                print(len(tracks.keys()))
                next_track_ids = random.sample(next_track_ids, 3)
        
    genres = {}
    genre_list = []
    for track in tracks.values():
        genre = track['track_data']['genre']
        # for genre in track['track_data']['genre'].split(' '):
        if genre not in genres:
            genre_list.append(genre)
            genres[genre] = 0
        genres[genre] += 1
    
    print(genres)
    genre_list = list(filter(None, genre_list))
    genre_list.sort()
    for genre in genre_list:
        print(genre)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
