import sys
import json
import time
import couchdb
import key
# import numpy as np
# import re
# from tensorflow import keras
from tweepy import API
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener


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
        print(self.id_list)

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
            item = json.loads(item.value)
            twitter_id = item['value']
            if twitter_id not in id_list:
                id_list.append(twitter_id)
                print('Current twitter id not found in the database')
        return id_list;

    def on_data(self, data):
        '''

        :param self:
        :param data:
        :return:
        '''

        twitter_json = json.loads(data)
        twitter_id = twitter_json['id']

        if twitter_id not in self.id_list:

            twitter_json['type'] = 'twitter'

            try:
                self.db.save(twitter_json)
                self.id_list.append(twitter_id)

                self.count += 1
                print('Twitter Added: ', self.count)

                return True
            except:
                'Fail to write to db'
                time.sleep(0.5)
                return True

    def on_error(self, status):
        print(status)

    def on_status(self, status):
        print(status.text)


# geo info for every cities in Australia.
Melbourne = [144.67, -38.16, 145.39, -37.58]

account = key.myaccount2()
print(account)
auth = get_twitter_auth(account)
twitter_stream = Stream(auth, MyListener())

Brisbane = [152.65, -27.75, 153.44, -27.05]
Canberra = [149.10, -35.30, 149.16, -35.25]
Perth = [115.80, -31.94, 115.86, -31.90]
Adelaide = [138.58, -34.94, 138.62, -34.90]
Hobart = [147.30, -42.90, 147.32, -42.86]
Darwin = [130.82, -12.48, 130.86, -12.44]
AU = [115.86, -34.74, 152.51, -14.35]

# start crawling, begin with Melbourne.
twitter_stream.filter(locations=Melbourne)
