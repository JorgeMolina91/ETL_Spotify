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
TOKEN = "BQCRYsZmrTSwmZdVVZqxUK43Js8kcoypE0B9DeGkOyYSByoZG9SezV65MAhPsTdiljnmMFMdvHG4k8o66j6JK7bjPdapsJKd2yzfmLeo6am0LUqL3-k5NZiOKdVQzEH4PaR5eNL4ttPX2SdmTYIp377XT6z-jYJ0_DqMSpDk7GQd_lCEcviAcNX3wWbv"

# To get the token -> https://developer.spotify.com/console/get-recently-played/
# Note: You gotta have a Spotify account

# Check validations steps:
def checking_if_valid_data(df: pd.DataFrame) -> bool:
    # Is data empty
    if df.empty:
        print('No songs downloaded. Finishing execution')
        return False
    # Checking for duplicated item with the Primary Key
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception('Primary key is duplicated.')
    # Checking for Null
    if df.isnull().values.any():
        raise Exception('Null valued found.')
    # Checking the information is coming from yesterday (last 24 hours)
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    timestamps = df['timestamp'].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, '%Y-%m-%d') != yesterday:
            raise Exception('At least one of the returned songs are not from the last 24 hours')
    return True


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
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][:10])
    
    song_dict = {
        "song_name": song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps 
    }

    song_df = pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])
    print(song_df)

    # Validate
    if checking_if_valid_data(song_df):
        print('Data Valid, proceed to load stage')

    # if check_if_valid_data

