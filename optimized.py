import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as urllib


client_id = "0c25fe414ae54465adc3de1384b17b42"
client_secret = "2de2cbd2c63546b5bdcf62ecf888fe70"

client_credentials_manager = SpotifyClientCredentials(client_id = client_id, client_secret = client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


class Spotify:
    def get_data(self, uniqname_dictionary, username_dictionary):
        fname = input("Enter .csv filename: ")
        try:
            fhand = pd.read_csv("./google_forms/" + fname)

        except:
            print("Cannot open file.")
            exit()

        for i in range(len(fhand)):
            uniqname_dictionary[fhand["Username of Playlist Creator"][i]] = fhand["Uniqname"][i]

            # splits the playlist link into a useable id
            a = fhand["Spotify Playlist Link"][i].split("playlist/")
            playlistid = a[1]

            # inserts id to dictionary of spotify usernames
            username_dictionary[fhand["Username of Playlist Creator"][i]] = playlistid



    def call_playlist(self, username, playlist_id):
        # this is what each track holds
        playlist_features_list = ["popularity_index", "album_release_date", "artist", "album","track_name",  "track_id", "danceability",
                                  "energy","key","loudness","mode", "speechiness","instrumentalness",
                                  "liveness","valence","tempo", "duration_ms","time_signature"]

        # begins to create the data table
        playlist_df = pd.DataFrame(columns = playlist_features_list)

        # searches the playlist
        print(username)
        print(playlist_id + '\n')

        # makes it so returns more than limit = 100
        tracks = sp.user_playlist_tracks(user = username, playlist_id = playlist_id)["tracks"]
        playlist = tracks["items"]
        while (tracks["next"]):
            tracks = sp.next(tracks)
            playlist.extend(tracks["items"])

    
        for track in playlist:
            # get playlist features
            playlist_features = {}
            
            if (track["track"] == None):
                continue

            print(track["track"]["popularity"])
            playlist_features["popularity_index"] = track["track"]["popularity"]
            playlist_features["album_release_date"] = track["track"]["album"]["release_date"]
            playlist_features["artist"] = track["track"]["artists"][0]["name"]
            playlist_features["album"] = track["track"]["album"]["name"]
            playlist_features["track_name"] = track["track"]["name"]
            playlist_features["track_id"] = track["track"]["id"]

            # audio features
            audio_features = sp.audio_features(playlist_features["track_id"])[0]

            for feature in playlist_features_list[6:]:
                playlist_features[feature] = audio_features[feature]


            track_df = pd.DataFrame(playlist_features, index = [0])
            playlist_df = pd.concat([playlist_df, track_df], ignore_index = True)

        return playlist_df



    def new_release_album(self):
        # data chart columns
        playlist_features_list = ["cover_image", "album_release_date", "artist", "album", "album_id", "total_tracks"]

        # begins to create the data table
        playlist_df = pd.DataFrame(columns = playlist_features_list)

        # uses the spotify api
        tracks = sp.new_releases(limit = 50)["albums"]
        playlist = tracks["items"]

        for track in playlist:
            # get playlist features
            playlist_features = {}

            playlist_features["cover_image"] = "=IMAGE(\"" + track["images"][1]["url"] + "\")"
            playlist_features["album_release_date"] = track["release_date"]
            playlist_features["artist"] = track["artists"][0]["name"]
            playlist_features["album"] = track["name"]
            playlist_features["album_id"] = track["id"]
            playlist_features["total_tracks"] = track["total_tracks"]

            track_df = pd.DataFrame(playlist_features, index = [0])
            playlist_df = pd.concat([playlist_df, track_df], ignore_index = True)

        return playlist_df


    
    # function for getting soup of url
    def fresh_soup(self, url):
        # when making requests identify as browser
        hdr = {'User-Agent': 'Mozilla/5.0'}

        # make url request using specified browser
        req = urllib.Request(url, headers=hdr)

        # retrieve page source
        source = urllib.urlopen(req, timeout=10).read()
        soup = BeautifulSoup(source, "lxml", from_encoding = "utf-8")

        return soup

    # get all releases for specified genre (from everynoise)
    def get_genre(self, url, genrename):
        # list features for .csv
        list_features = ["artist_name", "album_name"]
        album_df = pd.DataFrame(columns = list_features)

        # create a genre dictionary (genre, new song count)
        genre = {}

        # goes to the dedicated webpage and gets formatted page source
        soup = self.fresh_soup(url)

        # get genre name
        gname = soup.find(id=genrename)
        genre = gname.a.get_text

        # get the count of songs in genre list
        glist = gname.text.split(" ")
        gcount = glist[-2]

        # retrieve albumbox album and albumbox album  extended
        artists = soup.find_all('b')
        albums = soup.find_all("a", {"onclick": "this.setAttribute('visited', true);"})
        
        # adds all artist and album name into list
        for i in range(int(gcount)):
            artistname = artists[i].get_text()
            albumname = albums[i].get_text()

            # create new dictionary
            releases = {}

            releases["artist_name"] = artistname
            releases["album_name"] = albumname

            track_df = pd.DataFrame(releases, index = [0])
            album_df = pd.concat([album_df, track_df], ignore_index = True)

        # return pandas dataframe of all artist name and album name for releases of that genre
        return album_df
            

# executing functions
a = Spotify()
uniqname_dictionary = dict()
username_dictionary = dict()

a.get_data(uniqname_dictionary, username_dictionary)

'''
# function for reading through all individual playlists
for i in range(len(username_dictionary)):
    # get key and playlist id from list
    key = list(username_dictionary.keys())[i]
    id = list(username_dictionary.values())[i]

    # exports tracks to .csv file w/ uniqname as filename
    folder_to_export_path = "./individual_csv/"
    a.call_playlist(key, id).to_csv(folder_to_export_path+ uniqname_dictionary.get(key)+".csv", encoding = "utf-8-sig")


# new releases program
newfolder_to_export_path = "./new_releases/"
a.call_playlist("spotify", "37i9dQZF1DX4JAvHpjipBk?si=8d88036169ed40c3").to_csv(newfolder_to_export_path+ "newreleases.csv", encoding = "utf-8-sig")


# top hits program
new2folder_to_export_path = "./top_hits/"
a.call_playlist("spotify", "37i9dQZF1DXcBWIGoYBM5M?si=67999d41839a48a9").to_csv(new2folder_to_export_path+ "tophits.csv", encoding = "utf-8-sig")


# get new album releases
a.new_release_album().to_csv(newfolder_to_export_path+ "new_album_release.csv", encoding = "utf-8-sig")
'''



'''
################################################
               EveryNoise Scraper
################################################
'''

# scrape everynoise webpage (indie pop)
genrename = "indiepop"
print("indiepop")
print(a.get_genre('https://everynoise.com/new_releases_by_genre.cgi?genre=%2Aindie&region=US', genrename))


# scrape (pop)
genrename2 = "pop"
print("pop")
print(a.get_genre('https://everynoise.com/new_releases_by_genre.cgi?genre=%2Apop&region=US', genrename2))


# scrape (k-pop)
genrename3 = "kpop"
print("kpop")
print(a.get_genre('https://everynoise.com/new_releases_by_genre.cgi?genre=k-pop&region=US', genrename3))

# scrape (k-r&b)
genrename4 = "koreanrb"
print("koreanrb")
print(a.get_genre('https://everynoise.com/new_releases_by_genre.cgi?genre=korean%20r%26b&region=US', genrename4))

# scrape (k-indie)
genrename5 = "kindie"
print("kindie")
print(a.get_genre('https://everynoise.com/new_releases_by_genre.cgi?genre=k-indie&region=US', genrename5))

# scrape (k-rap)
genrename6 = "krap"
print("krap")
print(a.get_genre('https://everynoise.com/new_releases_by_genre.cgi?genre=k-rap&region=US', genrename6))