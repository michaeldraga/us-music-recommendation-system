# Unternehmenssoftware music recommendation system

Hello and welcome to the Unternehemenssoftware project repository of group Spotify (formerly group soundcloud)! Below you will find some basic instructions that should get you started in no time. In case of any questions please do not hesitate to contact any of us using the email addresses below. Cheers!

## The Team

- Eyad Wahdan
- Kourosh Maleki
- Michael Draga

## Setup

```bash
chmod +x setup.sh
# the first . in the line below is important because it allows the script to change
# the conda environment of your current shell!
. ./setup.sh
```

## Structure

### data-collection

This folder contains all files used to generate the dataset used for modelling. While [script.py](./data-collection/script.py) contains the business logic used to query the tracks, [SpotifyApi.py](./data-collection/script.py) contains a home-grown client for the Spotify API.

Additionally, there are several csv files in this folder: one for every "entity" (artists, features, tracks), one containing tracks with artists and the full dataset, which is called [tracks_with_features_demo.csv](./data-collection/tracks_with_artists.csv).

You can find additional information in the [README](./data-collection/README.md) contained within the folder.

### data-analysis

This folder contains the notebook used for analysing the dataset. All required dependencies should be installed after executing [setup.sh](./setup.sh).

### model

This folder contains all code and miscellanious files needed for training and evaluating the model, as well as the notebook used in the presentation. Furthermore, it contains the images used in the presentation, a utility script to fill missing score values in one of the text files and an additional [README](./model/README.md).

Please refer to aforementioned [README](./model/README.md) for important information regarding the execution of the modelling notebook.

### soundcloud-data-collection (deprecated)

This folder contains the code used to query the SoundCloud API for track information. Since we decided to go with Spotify instead of SoundCloud, this code was never finished and has only been kept in this repository for the sake of completeness.

## Environment variables

Environment variables are expected to be stored in `.env` files in the root folder of the package that uses them. Please find the keys of the expected environment variables for the existing packages below. If you have your own client credentials for any of these, feel free to use them. If not, please request them from us via email.

### data-collection

```env
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
```

### soundcloud-data-collection (deprecated)

```env
SOUNDCLOUD_CLIENT_ID=
SOUNDCLOUD_CLIENT_SECRET=
```

## Running the code (data-collection / soundcloud-data-collection)

Once the dependency script has been run and environment variables have been set up, feel free to run any of the packages as follows:

```bash
cd package # data-collection, soundcloud-data-collection
python ./script.py
```

You will find additional README files in the roots of the respective packages in case addtional setup work should be required.
