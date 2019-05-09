# Cluster and Cloud Computing Assignment 2
# Team 33
# Chenyang Gao, Chenyang Wang, Naijun Wang, Xiaoming Zhang, Yangyang Luo

# This file is for streaming crawling of some major cities in Australia

import sys
import time
from tweepy import API
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

# this class is use for crawling Streaming data from twitter.
class MyListener(StreamListener):
    #connect to twitter.
    def get_twitter_auth(self):
        '''setup Twitter anthentication.

        return twitter.OAuthHandler object
        '''
        try:
            consumer_key = "Kpyssg6TFroQBUFnOXypEfe42"
            consumer_secret = "Tc4yDwFuLsgmbLzpZLwlMEIUiUDG5N1onXOJAEQiTxXbG670iL"
            access_token = "1404414595-tAxzSebx6HLTGj59RBlJISAh5VqOx6BZWv7pCk0"
            access_secret = "z0VO09ArtRqRi1G0eEwOJWKPwHdThbJ6Py60x033cNpQr"
        except KeyError:
            sys.stderr.write("TWITTER_* environment variables not set\n")
            sys.exit(1)
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth

    def get_twitter_client(self):
        '''Setup Twitter API client

        return: tweepy.API object
        '''

        auth = self.get_twitter_auth()
        client_api = API(auth)
        return client_api

    # write data into a json file.
    def on_data(self, data):
        try:
            with open('Adelaide_twitter.json', 'a') as f:
                f.write(data)
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
            time.sleep(5)
        return True

    def on_error(self, status):
        print(status)
        return True

# geo info for every cities in Australia.
Melbourne = [144.67,-38.16,145.39,-37.58]
auth = MyListener().get_twitter_auth()
twitter_stream = Stream(auth, MyListener())
Brisbane = [152.65,-27.75,153.44,-27.05]
Canberra = [149.10, -35.30,149.16, -35.25]
Perth = [115.80, -31.94,115.86, -31.90]
Adelaide = [138.58, -34.94,138.62, -34.90]
Hobart = [147.30, -42.90,147.32, -42.86]
Darwin = [130.82, -12.48,130.86, -12.44]
AU = [115.86,-34.74,152.51,-14.35]

# start crawling, begin with Melbourne.
twitter_stream.filter(locations=Adelaide)