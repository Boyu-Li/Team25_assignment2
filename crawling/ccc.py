import sys
import json
import time
import couchdb
from tweepy import API
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener



# this class is use for crawling Streaming data from twitter.
class MyListener(StreamListener):
    def __init__(self):
        self.count = 0
        self.oldDataId =[]
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

    def function(doc):
        emit(doc.id)

            
    # write data into a json file.
    def on_data(self, data):
        try:
            with open('Melbourne_twitter.json','a') as f:
                f.write(data)
                #print(data)
                user = "admin"
                password = "admin"
                couchserver = couchdb.Server("http://%s:%s@172.26.38.84:5984/" % (user, password))
                #db = couchserver.create('hello')
                dbname = "hello"
                if dbname in couchserver:
                    db = couchserver[dbname]
                else:
                    db = couchserver.create(dbname)
                self.count = self.count + 1
                print(self.count)
                temp_vari = json.loads(data)
                temp_id = temp_vari["id"]
                for item in db.view('_design/twitter/_view/byTwitterID'):
                    #print(item)
                    self.oldDataId.append(item.value)

                
                #print(temp_vari)
                temp_vari['type'] = "twitter"
                #temp_vari['_id'] = str(self.count)
                if(temp_id not in self.oldDataId):
                    docId,revID = db.save(temp_vari)
                    self.oldDataId.append(temp_id)
                    print(self.oldDataId)
                    #db.update([temp_vari],'_id' = str(self.count))
                else:
                    print("not accept same data!!!!")
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
twitter_stream.filter(locations=Melbourne)






