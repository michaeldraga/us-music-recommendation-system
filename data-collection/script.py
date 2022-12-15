import asyncio
from datetime import datetime, timedelta
import json
import os
import aiohttp
import dotenv
from SpotifyApi import SpotifyApi 
import pandas as pd
from typing import MutableSequence

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

def artists_list_to_dataframe(artists: MutableSequence['SpotifyApi.Artist']) -> pd.DataFrame:
    return pd.DataFrame(data={
        'artist_id': [artist.id for artist in artists],
        'name': [artist.name for artist in artists],
        'genres': ["/".join(artist.genres) for artist in artists],
    })

def track_list_to_dataframe(tracks: MutableSequence['SpotifyApi.Track']) -> pd.DataFrame:
    # print('track_list_to_dataframe')
    # print([track.artists for track in tracks])
    # print([track.artists[0].genres for track in tracks])
    return pd.DataFrame(data={
        'id': [track.id for track in tracks],
        'name': [track.name for track in tracks],
        'artists_ids': ["/".join(track.artists_ids) for track in tracks],
        # 'artists_genres': ["/".join(["/".join(artist.genres) for artist in track.artists_ids]) for track in tracks],
        'album': [track.album.name for track in tracks],
        'preview_url': [track.preview_url for track in tracks],
        'duration_ms': [track.duration_ms for track in tracks],
        'popularity': [track.popularity for track in tracks],
        'explicit': [track.explicit for track in tracks],
    })


def features_list_to_dataframe(features: MutableSequence['SpotifyApi.AudioFeatures']) -> pd.DataFrame:
    return pd.DataFrame(data={
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

async def get_all_category_dataframe(session: aiohttp.ClientSession, spotify: 'SpotifyApi', cache=False) -> pd.DataFrame:
    (_, _, data) = await spotify.fetch_all_categories(session, limit=50)
    print(data)
    category_df = pd.DataFrame(data={
        'id': [category['id'] for category in data],
        'name': [category['name'] for category in data]
    })

    if cache:
        spotify.save_cache()

    return category_df

async def get_all_playlists_for_category_dataframe(session: aiohttp.ClientSession, spotify: 'SpotifyApi', cois: list[str], category_df: pd.DataFrame, cache=False) -> pd.DataFrame:
    all_playlists = []
    for _, row in category_df.iterrows():
        if row['name'] in cois:
            print(f'Fetching playlists for {row["name"]}')
            (_, _, data) = await spotify.fetch_all_playlists_in_category(session, row['id'], limit=50)
            if data is None:
                print(f'No playlists for {row["name"]}')
                continue

            for playlist in data:
                all_playlists.append(playlist)
    
    if cache:
        spotify.save_cache()

    playlists_df = pd.DataFrame(data={
        'id': [playlist.id for playlist in all_playlists],
        'name': [playlist.name for playlist in all_playlists],
    })
    playlists_df.drop_duplicates(subset=['id'], inplace=True)
    return playlists_df

async def get_all_tracks_in_playlists(session: aiohttp.ClientSession, spotify: 'SpotifyApi', playlists_df: pd.DataFrame, cache=False) -> pd.DataFrame:
    all_tracks = []
    for _, row in playlists_df.iterrows():
        print(f'Fetching tracks for {row["name"]}')
        (_, _, data) = await spotify.fetch_all_tracks_in_playlist(session, row['id'], limit=100)

        if data is None:
            print(f'No tracks for {row["name"]}')
            continue

        for track in data:
            all_tracks.append(track)

    if cache:
        spotify.save_cache()

    tracks_df = track_list_to_dataframe(all_tracks)
    tracks_df.drop_duplicates(subset=['id'], inplace=True)
    return playlists_df

async def get_all_artists(session: aiohttp.ClientSession, spotify: 'SpotifyApi', tracks_df: pd.DataFrame, cache=False) -> pd.DataFrame:
    all_artists = []
    artist_ids = tracks_df['artists_ids'].str.split('/').explode().unique().tolist()
    for i in range(0, len(tracks_df), 50):
        print(f'Fetching features for tracks {i} to {i+50}')
        (_, _, data) = await spotify.fetch_many_artists(session, artist_ids[i:i+50])

        if data is None:
            print(f'No features for tracks {i} to {i+50}')
            continue

        for track in data:
            all_artists.append(track)

    if cache:
        spotify.save_cache()

    artists_df = artists_list_to_dataframe(all_artists)
    artists_df.drop_duplicates(subset=['artist_id'], inplace=True)
    return artists_df

async def get_all_audio_features(session: aiohttp.ClientSession, spotify: 'SpotifyApi', tracks_df: pd.DataFrame, cache=False) -> pd.DataFrame:
    all_features = []
    for i in range(0, len(tracks_df), 100):
        print(f'Fetching features for tracks {i} to {i+100}')
        (_, _, data) = await spotify.fetch_audio_features_for_tracks(session, tracks_df.iloc[i:i+100]['id'].to_list())
        if data is None:
            print(f'No features for tracks {i} to {i+100}')
            continue

        for feature in data:
            all_features.append(feature)

    if cache:
        spotify.save_cache()

    features_df = features_list_to_dataframe(all_features)
    return features_df

async def main():
    demo_track_id = '11dFghVXANMlKmJXsNCbNl'

    cois = read_text_file('categories_of_interest.txt')
    cois = cois.split('\n')

    async with aiohttp.ClientSession() as session:
        async with SpotifyApi(client_id=spotify_client_id, client_secret=spotify_client_secret, session=session) as spotify:
            category_df = await get_all_category_dataframe(session, spotify, cache=True)
            print(f'Had {spotify.cache_hits} cache hits')
            playlists_df = await get_all_playlists_for_category_dataframe(session, spotify, cois, category_df, cache=True)
            print(f'Had {spotify.cache_hits} cache hits')
            tracks_df = await get_all_tracks_in_playlists(session, spotify, playlists_df, cache=True)
            print(f'Had {spotify.cache_hits} cache hits')
            artists_df = await get_all_artists(session, spotify, tracks_df, cache=True)
            print(f'Had {spotify.cache_hits} cache hits')
            features_df = await get_all_audio_features(session, spotify, tracks_df, cache=True)
            print(f'Had {spotify.cache_hits} cache hits')

            # # iterate through all tracks
            # for _, row in tracks_df.iterrows():
            #     # get artists for track
            #     artists = artists_df[artists_df['artist_id'].isin(row['artist_id'].split('/'))]
            #     # set artist names in artist_names column
            #     tracks_df.at[row.name, 'artist_names'] = artists['name'].str.cat(sep='/')
            #     # set combined artist genres in artist_genres column
            #     tracks_df.at[row.name, 'artist_genres'] = artists['genres'].str.cat(sep='/')
            
            # write the above loop in a more efficient way
            tracks_df['artist_names'] = tracks_df['artists_ids'].apply(lambda x: artists_df[artists_df['artists_ids'].isin(x.split('/'))]['name'].str.cat(sep='/'))
            tracks_df['artist_genres'] = tracks_df['artists_ids'].apply(lambda x: artists_df[artists_df['artists_ids'].isin(x.split('/'))]['genres'].str.cat(sep='/'))


            tracks_with_features_df = pd.merge(
                tracks_df, features_df, left_on='id', right_on='track_id').drop('track_id', axis=1)
            print(tracks_with_features_df)

            # write to csv
            tracks_with_features_df.to_csv(
                'tracks_with_features_demo.csv', index=False, sep=',')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
