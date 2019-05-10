import sys
import json
import couchdb
import key
import numpy as np
import re
from tensorflow import keras
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from datetime import datetime

word_index_path = './dataset/word_index.csv'
model_file_path = './keras_model/model.h5'

def get_twitter_auth(account):
    '''
    get twitter auth.
    :param consumer_key:
    :param consumer_secret:
    :param access_token:
    :param access_secret:
    :return:
    '''

    access_token = account[0]["access_token"]
    access_secret = account[0]["access_secret"]
    consumer_key = account[0]["consumer_key"]
    consumer_secret = account[0]["consumer_secret"]
    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth
    except:
        sys.stderr.write("TWITTER_* environment variables not set\n")
        sys.exit(1)







class MyListener(StreamListener):

    def __init__(self):
        self.count = 0

        self.couchdb_user = 'admin'
        self.couchdb_password = 'admin'
        self.couchdb_url = 'http://%s:%s@172.26.38.84:5984/'
        self.db_name = 'hello'
        self.db = self.get_couchdb_db()
        self.id_list = self.get_exist_twitter_id()
        self.word_index_dict = self.get_word_index_dict()
        self.model = keras.models.load_model(model_file_path)
        self.now = datetime.now()


    def get_word_index_dict(self):
        dict = {}
        with open(word_index_path, 'r') as f:
            for line in f:
                line = line.split(',')
                index = line[0]
                word = line[1]
                dict[word] = int(index)
        return dict


    def create_sentence_index_list(self, sentence):
        index_list = []
        word_list = re.sub("[^\w]", " ", sentence).split()
        for word in word_list:
            if word in self.word_index_dict:
                index_list.append(self.word_index_dict[word])

        index_list = np.array(index_list)
        index_list = np.array([index_list])
        test_data = keras.preprocessing.sequence.pad_sequences(index_list, padding='post', maxlen=60)
        return test_data


    def print_time_diff(self, pre_time, msg):
        print(msg, datetime.now() - pre_time)

    def get_couchdb_db(self):
        print('Login Couchdb ----------------------')
        try:
            couch_server = couchdb.Server(self.couchdb_url % (self.couchdb_user, self.couchdb_password))

            if self.db_name in couch_server:
                db = couch_server[self.db_name]
                print('Find database in the couchdb')
            else:
                db = couchdb.create(self.db_name)
                print('Didnt find database and create one')
            print('Load db successfully')
            return db

        except:
            print('Fail to connect couchdb')

    def get_exist_twitter_id(self):

        id_list = []
        for item in self.db.view('_design/twitter/_view/byTwitterID'):
            twitter_id = item.value
            if twitter_id not in id_list:
                id_list.append(twitter_id)
                print('Current twitter id not found in the database')
        return id_list;

    def create_json(self, sentiment, twitter_id, city, coordinates, twitter_text):
        obj = {
            'type': 'sentiment',
            'sentiment': sentiment,
            'twitter_id': twitter_id,
            'city': city,
            'coordinates': coordinates,
            'twitter_text': twitter_text
        }
        json_obj = json.dumps(obj)
        return json_obj

    def cal_sentiment(self, val):
        if val > 0.6:
            return 'positive'
        elif val < 0.4:
            return 'negative'
        else:
            return 'neutral'

    def on_data(self, data):
        '''

        :param self:
        :param data:
        :return:
        '''
        print('Get one twitter --------------------------------')

        pre_time = datetime.now()
        twitter_json = json.loads(data)
        self.print_time_diff(pre_time, 'Duration of converting to JSON')

        twitter_id = twitter_json['id']


        if twitter_id not in self.id_list:
            twitter_json['type'] = 'twitter'

            try:
                self.id_list.append(twitter_id)

                self.count += 1
                print('Twitter Added: ', self.count)

                twitter_text = twitter_json['text']

                test_data = self.create_sentence_index_list(twitter_text)
                sentiment_percentage = self.model.predict(test_data)[0][0]
                print(sentiment_percentage)
                sentiment = self.cal_sentiment(sentiment_percentage)
                twitter_json['sentiment'] = sentiment
                twitter_json['sentiment_percent'] = float(sentiment_percentage)

                pre_time = datetime.now()
                self.db.save(twitter_json)
                self.print_time_diff(pre_time, 'Duration of Twitter save to db:')

                self.print_time_diff(self.now, 'Duration of whole task: ')
                self.now = datetime.now()

                print('----------------------------------------------')
                return True
            except:
                print('Fail to write to db')
                return True

    def on_error(self, status):
        print(status)

    def on_status(self, status):
        print(status.text)


# geo info for every cities in Australia.
Melbourne = [144.67, -38.16, 145.39, -37.58]
Brisbane = [152.65, -27.75, 153.44, -27.05]
Canberra = [149.10, -35.30, 149.16, -35.25]
Perth = [115.80, -31.94, 115.86, -31.90]
Adelaide = [138.58, -34.94, 138.62, -34.90]
Hobart = [147.30, -42.90, 147.32, -42.86]
Darwin = [130.82, -12.48, 130.86, -12.44]
AU = [115.86, -34.74, 152.51, -14.35]
Sydney = [150.92,-34.19, 151.49, -33.53]


account = key.myaccount2()
print(account)
auth = get_twitter_auth(account)
twitter_stream = Stream(auth, MyListener())

try:
    location_index = int(sys.argv[1])

    if location_index == 0:
        location = Melbourne
    elif location_index == 1:
        location = Brisbane
    elif location_index == 2:
        location = Canberra
    elif location_index == 3:
        location = Perth
    elif location_index == 4:
        location = Adelaide
    elif location_index == 5:
        location = Hobart
    elif location_index == 6:
        location = Darwin
    elif location_index == 7:
        location = Sydney
    else:
        print('Location index error')
        sys.exit(1)

    # start crawling, begin with Melbourne.
    twitter_stream.filter(locations=location)
except:
    print('argv should be integer')