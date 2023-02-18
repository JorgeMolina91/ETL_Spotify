import sqlalchemy 
from sqlalchemy import create_engine 
import pandas as pd
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import pytz
import sqlite3

# I'm going to create constants with my DB location, token and user_id. ¡COntants are always in CAPITAL LETERS!
DATABASE_LOCATION = sqlite3.connect("played_songs_list.db")
USER_ID = "jorgemolina2097"
TOKEN = "BQBB7KKj4T_mutLSIG1hKP1AHFNFNP0LHaFURQeYjgo5PpbuahBc1GAzQUqejhSqL4fHCk_j47-xm7ZrFcTIpEQ8q4jT9Dj31in78McdHqNj_zmx-BRf0wFn3M-bucxuamdXeH80GR8oBuaTJuk6C4kc9OpHJ0aAfIiPkQz3TkqXZjVevBXnC0yStIG_"

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
    yesterday = datetime.datetime.now(pytz.timezone('America/Bogota')) - datetime.timedelta(days=10) 
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
    today = datetime.datetime.now(pytz.timezone('America/Bogota')) # This provides the current time in UNIX Milliseconds
    yesterday = today - datetime.timedelta(days=2) 
    yesterday_unix_timestap = int(yesterday.timestamp())
    yesterday_unix_timestap_in_seconds = yesterday_unix_timestap // 1000 # Here we convert yesterday's date to seconds

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestap_in_seconds), headers=headers)

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
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps 
    }

    song_df = pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])
    print(song_df)

    # # Validate
    # if checking_if_valid_data(song_df):
    #     print('Data Valid, proceed to load stage')

    # # Load
    db = DATABASE_LOCATION
    c = db.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS my_played_list(
        song_name VARCHAR(200) NOT NULL,
        artist_name VARCHAR(200) NOT NULL,
        played_at VARCHAR(200) PRIMARY KEY NOT NULL,
        timestamp VARCHAR(200) NOT NULL
    )
    """

    c.execute(query)
    
    print("DB Opened Succefully")

    try:
        song_df.to_sql("my_played_list", db, if_exists='append', index=False)
        print("Data recorded in DB")
    except:
        print("Data already exists in the database")

    db.commit()
    db.close()