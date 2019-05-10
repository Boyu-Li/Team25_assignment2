import sys
import json
import time
import couchdb
# import numpy as np
# import re
# from tensorflow import keras
from tweepy import API
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener


def get_twitter_auth(consumer_key, consumer_secret, access_token, access_secret):
    '''
    get twitter auth.
    :param consumer_key:
    :param consumer_secret:
    :param access_token:
    :param access_secret:
    :return:
    '''

    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth
    except:
        sys.stderr.write("TWITTER_* environment variables not set\n")
        sys.exit(1)

class MyListener(StreamListener):
    def __init__(self, auth):
        self.count = 0
        self.oldDataId =[]

        self.auth = auth
        self.db = self.get_couchdb_db()
        self.client = self.get_twitter_client()

        self.id_list = []
        self.couchdb_user = 'admin'
        self.couchdb_password = 'admin'
        self.couchdb_url = 'http://%s:%s@172.26.38.84:5984/'
        self.db_name = 'hello'


    def get_twitter_client(self, auth):
        '''

        :param auth:
        :return:
        '''

        client_api = API(auth)
        return client_api

    def get_couchdb_db(self):

        try:
            couch_server = couchdb.Server(self.couchdb_url % (self.couchdb_user, self.couchdb_password))

            if self.db_name in couch_server:
                db = couch_server[self.db_name]
            else:
                db = couchdb.create(self.db_name)
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
        return id_list;

    def on_data(self, data):
        '''

        :param self:
        :param data:
        :return:
        '''

        twitter_json = json.loads(data)
        twitter_id = twitter_json[id]

        if twitter_id not in self.id_list:

            twitter_json['type'] = 'twitter'

            try:
                self.db.save(twitter_json)
                self.id_list.append(twitter_id)

                return True
            except:
                'Fail to write to db'
                time.sleep(1)

                return True


    def on_error(self, status):
        print(status)
        time.sleep(1)
        return True

# geo info for every cities in Australia.
Melbourne = [144.67, -38.16, 145.39, -37.58]

auth = MyListener().get_twitter_auth()
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






