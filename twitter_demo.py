#!/usr/bin/python

'''
API keys stored in dat.txt file after user authenticates for the first time
(can manually edit this)
written in Python3 by Jamy Li, @jamyjli based on original template
by Judith van Stegeren, @jd7h
audio.wav produced by M Meijer, A Sadananda Bhat, M. Dokter en C. Boersma
'''

'''
before running the script, do this:
0. environment variables to store developer keys (do NOT place string of any key in any file on github)
0b. obtain API keys from twitter
0c. fill them in the bash_profile above
$ nano ~/.bash_profile  (for mac, or) ~/.bashrc (for Raspberry Pi)
$ nano .gitignore (add dat.txt)
1. create a virtual environment
$ python -m venv venv
$ source venv/bin/activate
2. install the dependencies
(venv)$ pip install python-twitter
3. To re-run the virtual environment, do step 1b above
4. test speech recognition within venv
(venv)$ python3.8 -m speech_recognition
5. Install dependencies, e.g.
PyAudio python package required for speech_recognition
(venv)$ pip install PyAudio
6. Run: python twitter_demo.py (if fails, install dependency in step 5)

not needed:
4. Install ffmpeg program outside venv (use $ deactivate), it may install lots
$ brew install ffmpeg
5. Install portaudio program outside venv
$ brew install portaudio
5a. If there's a Permission denied @apply2files, check https://github.com/Homebrew/homebrew-core/issues/45009
$ touch /usr/local/lib/node_modules/node-red/node_modules/@node-red/nodes/.DS_Store

7. On RPi4, use alsamixer and F6, then F5, to configure USB microphone

'''

import time
import twitter #for docs, see https://python-twitter.readthedocs.io/en/latest/twitter.html
import os
import tweepy
import re
import sys

import speech_recognition as sr

from gtts import gTTS
#from pydub import AudioSegment
#from pydub.playback import play
#import pyaudio

# global variables
api = tweepy.API()
lastcodes = {}
text = ''
tweets = []
sayprompts = True
mic_device_index = 0

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
    got_token = False
    
    while not got_token:
        # authenticate with tweepy -> http://docs.tweepy.org/en/latest/auth_tutorial.html
        consumer_key = os.environ.get('TW_CONSUMER_KEY')
        consumer_secret = os.environ.get('TW_CONSUMER_SECRET')
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    
        try:
            redirect_url = auth.get_authorization_url()
            print(redirect_url)
        except tweepy.TweepError:
            print('Error! Failed to get request token.')
            # raise error.with_traceback(sys.exc_info()[2])
    
        # manually go to the url, then input 8-digit code
        verifier = input('Verifier:')    
        
        try:
            auth.get_access_token(verifier)
            got_token = True
        except tweepy.TweepError:
            print('Error! Failed to get access token.')
            # raise error.with_traceback(sys.exc_info()[2])

        # keep these in file as they never expire
        if got_token == True:
            access_token = auth.access_token
            access_secret = auth.access_token_secret
            with open("dat.txt", "w") as text_file:
                print(f"access_token: {access_token}\naccess_secret: {access_secret}", file=text_file)
            # construct the API instance
            api = tweepy.API(auth)
            print(api)

        if got_token == False:
            print('Please try again')
            # raise ValueError('request or access token bad')
    
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
        
    key = lastcodes['access_token']
    secret = lastcodes['access_secret']
    consumer_key = os.environ.get('TW_CONSUMER_KEY')
    consumer_secret = os.environ.get('TW_CONSUMER_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)
    # for some reason, this call doesn't throw an error if the key and secret are set to 'None'

# Handle rate limit error that comes up with twitter's cursors (i.e. pages)
# In this example, the handler is time.sleep(15 * 60),
# but you can of course handle it in any way you want.
def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)
            
# got_text and asr implementations based on https://stackoverflow.com/questions/38127563/handle-an-exception-in-a-while-loop
def got_text():
    global text
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source) # listen to the source
        try:
            text = r.recognize_google(audio, language="nl-NL") # use recognizer to convert speech to text
            #text = r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY", language="nl-NL") # key not working, maybe try the service account Key instead?
            return True # could try returning text instead of True
        except sr.UnknownValueError:
            print("Could not understand audio")
            return False
        except sr.RequestError as e:
            print("Could not request results from Google; {0}".format(e))
            return False
        #except: #don't use this I guess
        
def asr():
    # see 'Speech Recognition Using Python | Edureka' https://www.youtube.com/watch?v=sHeJgKBaiAI
    # and https://pythonprogramminglanguage.com/speech-recognition/    
    while(True):
        if got_text():
            break
        else:
            continue
    # text will be gotten

def main_menu():
    global api
    global text
    
    # menu and submenu --> https://stackoverflow.com/questions/42015741/creating-menu-and-submenu-display
    # could try to do it in a while loop and separate function as above
    # while(True), if function_check_asr_text_is_valid_menu_option(): break  else: continue
    command = ''
    while command == '':
        say("Zeg maar een bevel en een voorwerp", extraprint = "(bv. 'nieuws Floortje Dessing')")
        asr()
        print('ASR heard: ' + text)
        # will return some text, but need to validate
        if 'doei' in text:
            say('fijne dag')
            sys.exit()
        elif 'lezen' in text:
            command = 'lezen'
            say('lezen')
            # do something: voice latest tweet from timeline
            timeline_tweets = api.home_timeline(tweet_mode = "extended")
            username = next(iter(timeline_tweets), None).user.name
            text = next(iter(timeline_tweets), None).full_text
            print(text)
            say(readable_feed(text, username))
            #author = next(iter(timeline_tweets), None).author # same as user
            #user = public_tweets[0].user
            #text = public_tweets[0].full_text
            #date = tweet[0].created_at
        elif 'nieuws' in text:
            command = 'nieuws'
            say('nieuws')
            subcommand = nieuws_menu()
        else:
            say('ongeldige keuze!')
    # command is gotten
    return command

def got_user_timeline(target):
    global tweets
    global api
    target = target.replace(" ", "")
    try:
        tweets = api.user_timeline(screen_name = target, count = 1, tweet_mode = "extended")
        # id is numeric, user_id is @handle, screen name is profile name
        if len(tweets) > 0:
            return True
        else:
            # test: try 'flitsen'
            say("geen publiek tweets voor dat naam")
            return False
    except tweepy.TweepError as e:
        say("voor dat naam, {0}".format(e))
        return False

def nieuws_menu():
    global text
    global tweets
    
    # could try to process the 'leftover' string in text after nieuws is removed, so user can say news + username in one go
    subcommand = ''
    while subcommand == '':
        say('nieuws over welke @naam ?')
        asr()
        print('ASR heard submenu input: ' + text)
        # will return some text, but need to validate
        if 'doei' in text:
            return
        elif got_user_timeline(text):
            subcommand = 'atnaamtweet'
            # do something: voice latest tweet from @naam
            tweet = next(iter(tweets), None).full_text
            date = next(iter(tweets), None).created_at
            # tweet = tweets[0].text also works
            say(readable_feed(tweet, username = text))
        else:
            # got_user_timeline unsuccessful
            pass

def readable_feed(text, username = None):
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'\w+…', '', text)
    # remove links -> http://www.urlregex.com and truncated text (if it's a retweet, the last words/characters may get truncated)
    if username == None:
        saytweet = text
    else:
        username = username.replace('_', '')
        saytweet = '@' + username + ' zegt ' + text
    return saytweet

def say(text, extraprint=''):
    global sayprompts

    print('ROBOT says: ' + text + "   " + extraprint)    
    if sayprompts:
        # note: instead use ttsWatson if want to use curl to directly fetch from Watson API (i.e., cloud computing)
        tts = gTTS(text, lang='nl', slow=False)
        # language codes: https://gist.github.com/traysr/2001377
        tts.save('bijvorbeeld.mp3')

        # alternatively, use mixer in case AudioSegment is too buggy or slow    
        # play sound
        # mixer.init()
        # mixer.music.load('bijvorbeeld.mp3')
        # mixer.music.play()

	# uses mpg321
        os.system("mpg321 -q bijvorbeeld.mp3")

	# uses pydub
        #song = AudioSegment.from_wav('audio.wav')
        #play(song)
        #song = AudioSegment.from_mp3('bijvorbeeld.mp3')
        #play(song) # sometimes this takes a long time
    
def process_timeline():
    # '''
    # to process multiple tweets from authenticated user's timeline
    # can use pagination -> http://docs.tweepy.org/en/latest/cursor_tutorial.html
    # cursor method can raise Rate Limits
    tweepy.Cursor(api.user_timeline, id = "twitter", tweet_mode = "extended")
    for status in tweepy.Cursor(api.home_timeline).items(22):  # adding limit_handled doesn't seem to work here
         # process status here
         print(status.text)
    # '''
    # or do below without pagination
    #    for tweet in public_tweets:
    #        print(tweet.text)
         
    # to pick a specific user -> http://docs.tweepy.org/en/latest/cursor_tutorial.html

def update_status(msg):
    global api
    api.update_status(msg)

def main(): 
    global lastcodes
    gotlastcodes = False

    # try to read file first, else authenticate; then try to build handler, else authenticate
    try:
        filename = 'dat.txt'
        with open(filename) as f:
            content = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
            content = [x.strip() for x in content]
        for line in content:
            k, v = line.strip().split(': ')
            lastcodes[k.strip()] = v.strip()
            # https://stackoverflow.com/questions/4803999/how-to-convert-a-file-into-a-dictionary
        print('building OAuth from past access tokens in dat.txt')
        gotlastcodes = True
    except:
        twitter_authenticate()
        
    if gotlastcodes == True:
        try:
            twitter_buildOAuthHandler()
        except:
            twitter_authenticate()
    # user authetication codes good at this point

    # RPi4: configure pyaudio to use the correct number of channels
    # and correct sound card index for mic (see alsamixer)
    #pa = pyaudio.PyAudio()
    #for x in range(0,pa.get_device_count()):
    #    print(pa.get_device_info_by_index(x))

    #pyaudio.PyAudio().open(format=pyaudio.paInt16,
    #                    rate=44100,
    #                    channels=1, #change this to what your sound card supports
    #                    input_device_index=mic_device_index, #change this your input sound card index
    #                    input=True,
    #                    output=False,
    #                    frames_per_buffer=1024)

    # commands
    while(True):
        main_menu()
    
    
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

main()
