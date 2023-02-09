import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import sqlite3

# I'm going to create constants with my DB location, token and user_id. ¡COntants are always in CAPITAL LETERS!
DATABASE_LOCATION = "sqlite:///my_played_tracks.squlite"
USER_ID = "jorgemolina2097"
TOKEN = "BQAWZO6r5OXU_nBTn8G9985LeiPpzULKoIyJ4dtiyK1jpehGXe4Qa_uVKKor8s_2te1-G7fQDCF9vBwNfn8GIjLvr23lSy3xHx8mHf3lHPPzSafK2_wp91C2YPyZrsyGaxLpXdX-Lo8akR5wY719pJgeWKdls3xJ6jg_hsk9hOJV9C3i1CRVSiR-ZU7A"

if __name__ == "__main__":
    headers = { # We need to send some information in the header with our request
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=TOKEN)
    }


    # We need to create some variables to check the songs we've played in the last 24 hrs
    today = datetime.datetime.now() # This provides the current time in UNIX Milliseconds
    yesterday = today - datetime.timedelta(days=1) 
    yesterday_unix_timestap = int(yesterday.timestamp()) * 1000 # Here we convert yesterday's date to milliseconds

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestap), headers=headers)

    data = r.json() # Converting the information gotted to json

    # Since we're only interested in some information, we will create some lists to place that information

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = [] # The 24 hra period we're looking at


    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][:10])
    
    song_dict = {
        "song_name": song_names,
        "artist_names": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps 
    }

    song_df = pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])
    print(song_df)

