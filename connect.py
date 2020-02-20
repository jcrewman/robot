import os
import time
import random

# environmental variables
# Terminal: cd ~; nano .bash_profile; restart shell
os.environ
print(os.environ.get('TW_CONSUMER_KEY'))

import http.client
import mimetypes

def generate_timestamp():
    """Get seconds since epoch (UTC)."""
    return int(time.time())
        
        
def generate_nonce(length=8):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])        

# get user profile from Labs API met OAuth 2.0
conn = http.client.HTTPSConnection("api.twitter.com")
payload = ''
headers = {
  'Authorization': 'Bearer '+os.environ.get('TW_BEARER')
}
conn.request("GET", "/labs/1/users?usernames=TwitterDev&format=detailed", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

# sign-in 1/3 request token krijgen
headers = {
  'oauth_callback': '"https%3A%2F%2Fjamy.ca"',
  'Authorization': 'OAuth oauth_consumer_key= \"'+os.environ.get('TW_CONSUMER_KEY')+
  		'\",oauth_token=\"'+os.environ.get('TW_ACCESS_KEY')+
  		# replace these with functions todo
  		'\",oauth_signature_method="HMAC-SHA1",oauth_timestamp=\"'+'1582201477'+
  		'\",oauth_nonce=\"'+'1ixKPF5dxnh'+
  		'\",oauth_version="1.0",oauth_signature="pUhyKeAisAuaT4spVuylktnl9NQ%3D"'
    }
print('test\"'+str(generate_timestamp()))
conn.request("POST", "/oauth/request_token", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

# sign-in 2/3 
