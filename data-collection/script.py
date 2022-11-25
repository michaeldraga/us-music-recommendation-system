import asyncio
import json
import os
import aiohttp
import dotenv
from SpotifyApi import SpotifyApi
import pandas as pd

dotenv.load_dotenv()

spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
spotify_access_token = None


def print_json(data: dict):
    print(json.dumps(data, indent=4))


def print_list(data: list):
    str = '[\n'
    for item in data:
        str += f'    {repr(item)},\n'
    str += ']'
    print(str)


def read_text_file(filename: str):
    with open(filename, 'r') as file:
        return file.read()


async def main():
    demo_track_id = '11dFghVXANMlKmJXsNCbNl'

    cois = read_text_file('categories_of_interest.txt')
    cois = cois.split('\n')

    async with aiohttp.ClientSession() as session:
        async with SpotifyApi(client_id=spotify_client_id, client_secret=spotify_client_secret, session=session) as spotify:
            (_, _, data) = await spotify.fetch_all_categories(session, limit=50)
            print_json(data)
            category_df = pd.DataFrame(data={
                'id': [category['id'] for category in data['categories']['items']],
                'name': [category['name'] for category in data['categories']['items']]
            })

            # print(category_df.sort_values(by='name'))
            # print(category_df.sort_values(by='name').iloc[0])

            (_, _, playlists) = await spotify.fetch_all_playlists_in_category(session, category_df.iloc[0]['id'])
            playlists_df = pd.DataFrame(data={
                'id': [playlist.id for playlist in playlists],
                'name': [playlist.name for playlist in playlists],
            })
            # print_list(playlists)
            # print(playlists_df.sort_values(by='name'))

            (_, _, tracks) = await spotify.fetch_all_tracks_in_playlist(session, playlists_df.iloc[0]['id'])
            (_, _, tracks) = await spotify.fetch_all_tracks_in_playlist(session, playlists_df.iloc[0]['id'])
            (_, _, features) = await spotify.fetch_many_audio_features(session, [track.id for track in tracks])
            print_list(tracks)
            tracks_df = pd.DataFrame(data={
                'id': [track.id for track in tracks],
                'name': [track.name for track in tracks],
                'duration_ms': [track.duration_ms for track in tracks],
                'popularity': [track.popularity for track in tracks],
                'explicit': [track.explicit for track in tracks],
            })

            features_df = pd.DataFrame(data={
                'track_id': [feature.track_id for feature in features],
                'danceability': [feature.danceability for feature in features],
                'energy': [feature.energy for feature in features],
                'key': [feature.key for feature in features],
                'loudness': [feature.loudness for feature in features],
                'mode': [feature.mode for feature in features],
                'speechiness': [feature.speechiness for feature in features],
                'acousticness': [feature.acousticness for feature in features],
                'instrumentalness': [feature.instrumentalness for feature in features],
                'liveness': [feature.liveness for feature in features],
                'valence': [feature.valence for feature in features],
                'tempo': [feature.tempo for feature in features],
                'time_signature': [feature.time_signature for feature in features],
            })

            tracks_with_features_df = pd.merge(
                tracks_df, features_df, left_on='id', right_on='track_id').drop('track_id', axis=1)
            print(tracks_with_features_df)

            # write to csv
            tracks_with_features_df.to_csv(
                'tracks_with_features_demo.csv', index=False)

            # print(category_df[category_df['name'].isin(cois)].sort_values(by='name'))
            # sorted_cois = sorted(cois)
            # for category in sorted_cois:
            #     print(category)

            # print(category_df)
            # (_, status, data) = await spotify.fetch_track(session, demo_track_id)
            # print_json(data)
            # (_, status, data) = await spotify.fetch_audio_analysis(session, demo_track_id)
            # print_json(data)
            # (_, status, data) = await spotify.fetch_audio_features(session, demo_track_id)
            # print_json(data)
            # (_, status, data) = await spotify.fetch_many_tracks(session, [demo_track_id, demo_track_id, demo_track_id])
            # print_json(data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
