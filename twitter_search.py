from pattern.web import Twitter, plaintext
import unicodedata

twitter = Twitter(language='en') 

for tweet in twitter.search('"mindmixer"', count = 25,  cached=False):
    #if(not str.__contains__(tweet.text.str(), 'RT')):
    if 'RT' not in tweet.text:
        print plaintext(tweet.text) 
