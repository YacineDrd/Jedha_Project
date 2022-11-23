# Code inspired from Confluent Cloud official examples library
# https://github.com/confluentinc/examples/blob/7.1.1-post/clients/cloud/python/producer.py

######Packages

from confluent_kafka import Producer
import json
import ccloud_lib # Library not installed with pip but imported from ccloud_lib.py
import numpy as np
import time
from datetime import datetime
import requests
import pandas as pd
import os
import random


####Function
def recommend(name_movie):
    '''
    prend en entree le titre d'un film et nous prpose une recommendation
    '''
    try:
        movieID_GR = movie_titles_df[movie_titles_df.Movie_Title == name_movie].index[0]
        movie_name_reco = movie_titles_df.loc[similar_movie_pickle[movieID_GR]][1]
        return movie_name_reco

    except:
        print("Pas de Reco")
    
#### Read

# tables des films
movie_titles_df = pd.read_csv("./data/movie_titles.csv",sep = ",", header = None,names=['Movie_ID', 'Year_of_Release', 'Movie_Title'], index_col = "Movie_ID",  encoding = "Latin1", error_bad_lines=False)

# table de correspondance des films
similar_movie_pickle = pd.read_pickle("./data/similar_movies_dict.pickle")



# Initialise la configuration Ã  partir du fichier --> "python.config"
CONF = ccloud_lib.read_ccloud_config("python.config")

#le nom du topic Confluent
TOPIC = "Netflix" 

# configuration du producer
producer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
producer = Producer(producer_conf)
ccloud_lib.create_topic(CONF, TOPIC)

# L'url de L'api jedha 
url = "https://jedha-netflix-real-time-api.herokuapp.com/users-currently-watching-movie"

try:
    # Starts an infinite while loop that produces random current temperatures
    while True:
        ####Connexion
        response = requests.get(url)

        ####Args
        record_key = "netflix"
        response = requests.get(url)
        res = response.json()
        data = json.loads(res)
        df_work = pd.DataFrame(data['data'], columns=data['columns'])
        df_work = df_work[["customerID","Name"]]
        df_work['Movie_recommended'] = df_work['Name'].apply(lambda x : recommend(x))

        ####Result
        record_value = json.dumps(df_work.to_dict())
        print("Producing record: {}/t{}".format(record_key, record_value))

        # This will actually send data to your topic
        producer.produce(
            TOPIC,
            key=record_key,
            value=record_value,
        )
        time.sleep(0.5)

 # Interrupt infinite loop when hitting CTRL+C
except KeyboardInterrupt:
    pass
finally:
    producer.flush() # Finish producing the latest event before stopping the whole script