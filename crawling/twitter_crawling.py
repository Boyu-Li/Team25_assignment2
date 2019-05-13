import sys
import json
import numpy as np
import re
from tensorflow import keras
import tweepy
from tweepy import OAuthHandler
from couchdb import Server
from couchdb.design import ViewDefinition
import util
import time
import datetime as dt
from datetime import date, timedelta


def get_twitter_id_from_couch(database):

    id_list = []

    view_result = database.view('_design/twitter/_view/byTwitterID')

    try:
        view_result.total_rows

    except:

        view = ViewDefinition('twitter', 'byTwitterID', '''function(doc) {
            if (doc.type === "sentiment"){
                emit(doc._id, doc.id);
            }
        }''')
        view.get_doc(database)
        view.sync(database)
        view_result = database.view('_design/twitter/_view/byTwitterID')

    for item in view_result:
        twitter_id = item.value
        if twitter_id not in id_list:
            id_list.append(twitter_id)

    return id_list


def create_json(twitter_id, city, created_at, text, sentiment, sentiment_percent):

    obj = {
        'type': 'sentiment',
        'id': twitter_id,
        'city': city,
        'created_at': created_at,
        'text': text,
        'sentiment': sentiment,
        'sentiment_percent': sentiment_percent
    }

    return obj


def get_word_index_dict():
    dict = {}
    with open(util.word_index_path, 'r') as f:
        for line in f:
            line = line.split(',')
            index = line[0]
            word = line[1]
            dict[word] = int(index)
    return dict


def create_sentence_index_list(sentence, word_index_dict):
    index_list = []
    word_list = re.sub("[^\w]", " ", sentence).split()
    for word in word_list:
        if word in word_index_dict:
            index_list.append(word_index_dict[word])

    index_list = np.array(index_list)
    index_list = np.array([index_list])
    test_data = keras.preprocessing.sequence.pad_sequences(index_list, padding='post', maxlen=60)
    return test_data


def generate_sentiment(percent):
    if percent > 0.6:
        return 'positive'
    elif percent < 0.4:
        return 'negative'
    else:
        return 'neutral'


server_name = sys.argv[1]
# server_name = 'master'

yesterday = str(date.today() - timedelta(days=1))
try_count = 0
model = keras.models.load_model(util.model_file_path)

if server_name == 'master':
    credential = util.twitter_credential[0]
    citys = util.city_list[:3]
    counts = util.twitter_count[:3]
elif server_name == 'slaver1':
    credential = util.twitter_credential[1]
    citys = util.city_list[3:6]
    counts = util.twitter_count[3:6]
elif server_name == 'slaver2':
    credential = util.twitter_credential[2]
    citys = util.city_list[6:]
    counts = util.twitter_count[6:]
else:
    print('Server name not found, exit')
    exit(1)

word_index_dict = get_word_index_dict()


# Couchdb setup ----------------------------------------------
url = 'http://user:pass@172.26.38.140:5984/'
db_name = 'twitter_sentiment'

server = Server(url)

if db_name in server:
    database = server[db_name]
    print('Login into couchdb database: ', db_name)
else:
    database = server.create(db_name)
    print('Create new couchdb database: ', db_name)


# ------------------------------------------------------------

# Twitter API setup ------------------------------------------
auth = OAuthHandler(credential[0], credential[1])
auth.set_access_token(credential[2], credential[3])
api = tweepy.API(auth)
# ------------------------------------------------------------

twitter_id_list = get_twitter_id_from_couch(database)

geo_locations = []

print('Find city id -------------------------------------')
for city in citys:
    places = api.geo_search(query=city, granularity="city")
    for place in places:
        if place.country_code == 'AU':
            geo_locations.append([place.name, place.id])
            print('Found city', place.name, 'with id:', place.id)
            break

for idx, geo_location in enumerate(geo_locations):

    while counts[idx] > 0:

        try:
            if not len(twitter_id_list):
                new_tweets = api.search(q="place:%s" % geo_location[1], count=100, lang='en')
            else:
                new_tweets = api.search(q="place:%s" % geo_location[1], count=100, max_id=twitter_id_list[-1], lang='en')

            if not new_tweets:
                print('No more tweets found in', geo_location[0])
                break
            print('Found', len(new_tweets), 'tweets in', geo_location[0])

            twitter_count = 0
            for tweet in new_tweets:

                if tweet.id not in twitter_id_list:

                    text = tweet.text
                    created_at = str(tweet.created_at)

                    test_data = create_sentence_index_list(text, word_index_dict)

                    sentiment_percent = float(model.predict(test_data)[0][0])

                    sentiment = generate_sentiment(sentiment_percent)

                    json_obj = create_json(tweet.id, geo_location[0], created_at, text, sentiment, sentiment_percent)

                    database.save(json_obj)

                    twitter_count += 1
                    twitter_id_list.append(tweet.id)

            counts[idx] -= twitter_count
            print(twitter_count, 'tweets added into database')

            if counts[idx] <= 0:
                break

        except tweepy.TweepError as e:
            print('Exception raised, waiting 15 minutes')
            print('(until:', dt.datetime.now() + dt.timedelta(minutes=15), ')')
            time.sleep(60*15)
            try_count += 1
            print('Wait 15 mins, restart')
            continue

