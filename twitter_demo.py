#!/usr/bin/python

'''
USE AT YOUR OWN PERIL <3
fill in your API keys before running the script
written in Python3 by Judith van Stegeren, @jd7h
modified by Jamy Li, @jamyjli
'''

'''
before running the script, do this:
1. create a virtual environment
$ python -m venv venv
$ source venv/bin/activate
2. install the dependencies
$ pip install python-twitter
3. obtain API keys from twitter
4. fill them in in the script below

To re-run the virtual environment, do step 2 above

'''

import time
import twitter #for docs, see https://python-twitter.readthedocs.io/en/latest/twitter.html
import os
import tweepy

from gtts import gTTS

# global variables
api = tweepy.API()
lastcodes = {}

# used only if will use web app
class Session(object):
    def __init__(self):
    	self.dict = {}
        
    def get(self, key):
    	if key in self.dict:
    		return self.dict[key]
    	else:
    		print('Error! No key with that name')
    
    def set(self, key, token):
    	self.dict.update({key:token})
    	
    def delete(self, key):
    	del self.dict[key]

def twitter_authenticate():
    global api
    
    # authenticate with tweepy -> http://docs.tweepy.org/en/latest/auth_tutorial.html
    consumer_key = os.environ.get('TW_CONSUMER_KEY')
    consumer_secret = os.environ.get('TW_CONSUMER_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print('Error! Failed to get request token.')
    
    # manually go to the url 
    print(redirect_url)
    
    verifier = input('Verifier:')    
        
    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')

    # keep these in fiile as they never expire
    access_token = auth.access_token
    access_secret = auth.access_token_secret    
    with open("dat.txt", "w") as text_file:
        print(f"access_token: {access_token}\naccess_secret: {access_secret}", file=text_file)
    
    api = tweepy.API(auth)
    print(api)
    
    '''
    # if using web app, need callback  -> http://docs.tweepy.org/en/latest/auth_tutorial.html
    session = Session()
    session.set('request_token', auth.request_token['oauth_token'])
    # we will need request token inside the callback URL request
    verifier = request.GET.get('oauth_verifier')
    # try to get the verification i guess using a browser from python
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    token = session.get('request_token')
    session.delete('request_token')
    auth.request_token = { 'oauth_token' : token,
                             'oauth_token_secret' : verifier }    
    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'
    '''

# read user's stored keys and re-build OAuthHandler
def twitter_buildOAuthHandler():
    global api
    global lastcodes
    
    filename = 'dat.txt'
    with open(filename) as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content]
    for line in content:
        k, v = line.strip().split(': ')
        lastcodes[k.strip()] = v.strip()
    
    key = lastcodes['access_token']
    secret = lastcodes['access_secret']
    
    consumer_key = os.environ.get('TW_CONSUMER_KEY')
    consumer_secret = os.environ.get('TW_CONSUMER_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)


def read_feed():
    global api
    public_tweets = api.home_timeline()
    print(api)
#    for tweet in public_tweets:
#        print(tweet.text)
    
    # saytweet = public_tweets[0].text
    saytweet = next(iter(public_tweets), None).text
    print(saytweet)
    # print one tweet
    
    # note: instead use ttsWatson if want to use curl to directly fetch from Watson API (i.e., cloud computing)
    tts = gTTS(saytweet, lang='nl', slow=True)
    # language codes: https://gist.github.com/traysr/2001377
    tts.save('bijvorbeeld.mp3')

# next: make a function that grabs the 20 recent feed items (see above) and display them, maybe process them to summarize them

twitter_buildOAuthHandler()

#twitter_authenticate()
read_feed()

# get 20 most recent tweets
# this doesn't work yet since need to create a global variable that carries between functions, which is the api


# api.update_status('tweepy + oauth!')


# could do something like read file first, then check if the auth works, then if it doesn't, then call authenticate
def main(): 



    ''' 
    # Example of using twitter API (base)
    # connect to api with apikeys
    # if you don't have apikeys, go to apps.twitter.com
    api = twitter.Api(consumer_key=os.environ.get('TW_CONSUMER_KEY'),
                      consumer_secret=os.environ.get('TW_CONSUMER_SECRET'),
                      access_token_key=access_token,
                      access_token_secret=access_token_secret)

    # get followers
    print("Getting a list of accounts I follow on Twitter...")
    friends = api.GetFriends()
    friend_ids = [friend.id for friend in friends]
    for friend in friends:
        print("Friend: ", friend.name, friend.screen_name, friend.id)    
    # get a list of accounts that are following me
    print("Getting a list of followers from Twitter...")
    followers = api.GetFollowers()
    followers_ids = [user.id for user in followers]
    for follower in followers:
        print("Follower: ", follower.name, follower.screen_name, follower.id)

    # look up the user_id of a single user
    print("Looking up the details of screenname @jd7h...")
    print(api.UsersLookup(screen_name=["jd7h"]))

    print("Looking up the details of screenname @jd7h...")
    print(api.UsersLookup(screen_name=["jd7h"]))
    # this should output: [User(ID=222060384, ScreenName=jd7h)]

    #tweeting
    body = "This is a tweet. Chirp chirp. Hello world!"
    print("Posting tweet...")
    #result = api.PostUpdate(body)    

    # mentions:
    body = "@jd7h My Twitter bot is working!"
    print("Posting tweet with mention...")
    #result = api.PostUpdate(body) # including the screenname (prepended by a '@') in the tweet-body is enough to create a mention.

    # replying to a tweet:
    itech_tweet_id = 1178660081648492545 # tweet id of the tweet https://twitter.com/jd7h/status/1178660081648492545
    body = "I ran your script without changing some of the input strings!"
    print("Posting reply...")
    #result = api.PostUpdate(body, in_reply_to_status_id=itech_tweet_id)

    # other useful stuff:
    # creating a private list
    print("Creating a private list...")
    mylist = api.CreateList(name="My beautiful list",mode="private",description=("A secret list I created on " + time.strftime("%Y-%m-%d")))

    # Add all users from 'Following' to the new list
    print("Adding friends to the newly created list...")
    for friend_id in friend_ids:
      print("Adding ", friend_id)
      result = api.CreateListsMember(list_id=mylist.id,user_id=friend_id)
    '''
