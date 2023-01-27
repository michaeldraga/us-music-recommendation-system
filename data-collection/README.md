# Data collection

## Strategy

To collect the data that we'll use for training and validating our model, we're taking the following approach:

First, we will get the categories listed below from the Spotify API (further just called "API"). For each of these categories, we will be requesting the playlists contained within them. Afterwards, our algorithm will fetch general information about the tracks in all of these playlists, as well as their audio-features. 

In case we need more data for improving our model in the future, we would take the following approach:

After fetching all tracks in the category playlists, the main crawling loop starts. At the beginning, we will fetch all albums of all artists that were listed in the previous tracks. We will then fetch the general information and audio-features of all of the tracks contained within these albums. At this point we restart the crawling loop by fetching all albums of all artists of the fetched tracks.

While doing all of this, we obviously make sure that no category, playlist, album, artist or track are fetched twice.

### Categories of interest

<table style="width: 100%">
    <tr>
        <td>new releases</td>
        <td>Focus</td>
        <td>TV & Movies</td>
    </tr>
    <tr>
        <td>hip-hop</td>
        <td>Decades</td>
        <td>Netflix</td>
    </tr>
    <tr>
        <td>pop</td>
        <td>Latin</td>
        <td>Instrumental</td>
    </tr>
    <tr>
        <td>mood</td>
        <td>R&B</td>
        <td>Wellness</td>
    </tr>
    <tr>
        <td>rock</td>
        <td>Romance</td>
        <td>Punk</td>
    </tr>
    <tr>
        <td>charts</td>
        <td>Kids & Family</td>
        <td>Ambient</td>
    </tr>
    <tr>
        <td>dance / electronic</td>
        <td>Metal</td>
        <td>Blues</td>
    </tr>
    <tr>
        <td>chill</td>
        <td>Jazz</td>
        <td>Cooking & Dining</td>
    </tr>
    <tr>
        <td>indie</td>
        <td>Trending</td>
        <td>Alternative</td>
    </tr>
    <tr>
        <td>fres finds</td>
        <td>In the car</td>
        <td>Travel</td>
    </tr>
    <tr>
        <td>equal</td>
        <td>Classical</td>
        <td>Reggae</td>
    </tr>
    <tr>
        <td>radar</td>
        <td>Folk & Acoustic</td>
        <td>Caribbean</td>
    </tr>
    <tr>
        <td>workout</td>
        <td>Country</td>
        <td>Afro</td>
    <tr>
        <td>k-pop</td>
        <td>Disney</td>
        <td>Songwriters</td>
    </tr>
    <tr>
        <td>sleep</td>
        <td>Soul</td>
        <td>Funk & Disco</td>
    </tr>
    <tr>
        <td>party</td>
        <td>Gaming</td>
        <td>Summer</td>
    </tr>
    <tr>
        <td>at home</td>
        <td>Pride</td>
        <td>Halloween</td>
    </tr>
    <tr>
        <td>Happy Holidays</td>
        <td></td>
        <td></td>
    </tr>
</table>
