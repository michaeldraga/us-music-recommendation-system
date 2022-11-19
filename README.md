# Unternehmenssoftware music recommendation system

Hello and welcome to the Unternehemenssoftware project repository of group Spotify (formerly group soundcloud)! Below you will find some basic instructions that should get you started in no time. In case of any questions please do not hesitate to contact any of us using the email addresses below. Cheers!

## Setup

```bash
chmod +x setup.sh
# the first . in the line below is important because it allows the script to change 
# the conda environment of your current shell!
. ./setup.sh
```

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

## Running the code

Once the dependency script has been run and environment variables have been set up, feel free to run any of the packages as follows:

```bash
cd package # data-collection, soundcloud-data-collection
python ./script.py
```

You will find additional README files in the roots of the respective packages in case addtional setup work should be required.