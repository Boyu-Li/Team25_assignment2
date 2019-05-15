import sys
import json
from textblob import TextBlob
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


def get_tweet_ids(database):

    id_list = []

    view_result = database.view('_design/twitter/_view/tweetId')

    try:
        view_result.total_rows

    except:

        view = ViewDefinition('twitter', 'tweetId', '''function(doc) {
            if (doc.type === "tweet"){
                emit(doc._id, doc.id);
            }
        }''')
        view.get_doc(database)
        view.sync(database)
        view_result = database.view('_design/twitter/_view/tweetId')

    for item in view_result:
        tweet_id = item.value
        if tweet_id not in id_list:
            id_list.append(tweet_id)

    return id_list


def get_tweet_ids_by_city(database, city):

    id_list = []

    view_result = database.view('_design/twitter/_view/tweetIdByCity?key="' + city + '"')

    try:
        view_result.total_rows

    except:

        view = ViewDefinition('twitter', 'tweetIdByCity', '''function(doc) {
            if (doc.type === "tweet"){
                emit(doc.city, doc.id);
            }
        }''')
        view.get_doc(database)
        view.sync(database)
        view_result = database.view('_design/twitter/_view/tweetIdByCity?key=\"' + city + '\"')

    if not view_result.total_rows:
        return []
    for item in view_result:
        tweet_id = item.value
        if tweet_id not in id_list:
            id_list.append(tweet_id)
    return id_list


# def create_json(twitter_id, city, created_at, text, sentiment, sentiment_percent):
#
#     obj = {
#         'type': 'sentiment',
#         'id': twitter_id,
#         'city': city,
#         'created_at': created_at,
#         'text': text,
#         'sentiment': sentiment,
#         'sentiment_percent': sentiment_percent
#     }
#
#     return obj


def create_json(tweet_id, city, created_at, text, polarity, subjectivity, my_sentiment, my_sentiment_percent, media_urls):

    obj = {
        'type': 'analysis',
        'id': tweet_id,
        'city': city,
        'created_at': created_at,
        'text': text,
        'polarity': polarity,
        'subjectivity': subjectivity,
        'sentiment': my_sentiment,
        'sentiment_percent': my_sentiment_percent,
        'media_urls': media_urls
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
    if percent >= 0.5:
        return 'positive'
    else:
        return 'negative'

# server_name = sys.argv[1]
server_name = 'slaver2'

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
elif server_name == 'other':
    credential = util.twitter_credential[3]
    citys = util.city_list
    counts = util.twitter_count

else:
    print('Server name not found, exit')
    exit(1)

model = keras.models.load_model(util.model_file_path)
word_index_dict = get_word_index_dict()


# Couchdb setup ----------------------------------------------
user = 'user'
password = 'pass'
url = 'http://%s:%s@172.26.38.218:5984/'
db_name = 'twitter'

server = Server(url % (user, password))

if db_name in server:
    database = server[db_name]
    print('Login into couchdb database: ', db_name)
else:
    database = server.create(db_name)
    print('Create new couchdb database: ', db_name)
# ------------------------------------------------------------


# twitter_id_list = get_twitter_id_from_couch(database)


# Twitter API setup ------------------------------------------
auth = OAuthHandler(credential[0], credential[1])
auth.set_access_token(credential[2], credential[3])
api = tweepy.API(auth)
# ------------------------------------------------------------

city_infos = []

print('Find city id -------------------------------------')
for city in citys:
    places = api.geo_search(query=city, granularity="city")
    for place in places:
        if place.country_code == 'AU':
            city_infos.append([city, place.id])
            print('Found city', city, 'with id:', place.id)
            break


for idx, city_info in enumerate(city_infos):

    tweet_ids = get_tweet_ids(database)
    searched_ids = []
    duplicate_count = 0
    duplicate_try_count = 0

    while counts[idx] > 0:

        try:
            if not len(searched_ids):
                new_tweets = api.search(q="place:%s" % city_info[1], count=100, lang='en')
            else:
                new_tweets = api.search(q="place:%s" % city_info[1], count=100, max_id=tweet_ids[-1], lang='en')

            if not new_tweets:
                print('No more tweets found in', city_info[0])
                break
            print('Found', len(new_tweets), 'tweets in', city_info[0])

            tweet_count = 0

            for tweet in new_tweets:

                if tweet.id not in tweet_ids:

                    text = tweet.text

                    polarity, subjectivity = TextBlob(text).sentiment

                    created_at = str(tweet.created_at)

                    test_data = create_sentence_index_list(text, word_index_dict)
                    my_sentiment_percent = float(model.predict(test_data)[0][0])
                    my_sentiment = generate_sentiment(my_sentiment_percent)

                    media_files = set()
                    media = tweet.entities.get('media', [])
                    if len(media) > 0:
                        for ele in media:
                            media_files.add(ele['media_url'])

                    json_obj = create_json(tweet.id, city_info[0], created_at, text, polarity, subjectivity,
                                           my_sentiment, my_sentiment_percent, list(media_files))
                    database.save(json_obj)
                    tweet_json = tweet._json
                    tweet_json['type'] = "tweet"
                    database.save(tweet_json)

                    tweet_count += 1
                    tweet_ids.append(tweet.id)
                    searched_ids.append(tweet.id)

            if len(new_tweets) > 0 and tweet_count == 0:
                duplicate_count += 1
            else:
                duplicate_count = 0

            counts[idx] -= tweet_count
            print(tweet_count, 'tweets added into database')

            if counts[idx] <= 0:
                break
            if duplicate_count > 10:
                print("Received duplicate tweets successive 10 times, fetch next city")
                duplicate_try_count += 1

                if duplicate_try_count > 2:
                    break
                print('(until:', dt.datetime.now() + dt.timedelta(minutes=15), ')')
                time.sleep(60)
                print('Wait 15 mins, restart')
                continue

        except tweepy.TweepError as e:
            print('Exception raised, waiting 15 minutes')
            print('(until:', dt.datetime.now() + dt.timedelta(minutes=15), ')')
            time.sleep(60*15)
            print('Wait 15 mins, restart')
            continue

