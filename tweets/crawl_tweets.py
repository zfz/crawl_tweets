#!/usr/bin/python
import tweepy
import sys
import urllib2, urllib
from datetime import datetime
from time import sleep

url = "http://worldfun.sinaapp.com"
secret = "kmz4515jlm51"

def user_list(url, secret):
# Fetch the list of user to crawl.
    twitter_user = []
    user_list = eval(urllib2.urlopen(url+"/getUserList.php?secret="+secret).read())
    if user_list['status'] == 'ok':
        #print 'User list status ok!'
        for user in user_list['result']:
            if user['src'] == 'twitter':
                twitter_user.append(user)
    return twitter_user

def trans_datetime(str):
# Transform the string the datetime type.
    return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")

def check_new(last, name):
# Check new tweets posted.
    return True if trans_datetime(last) < trans_datetime(user_tweets(name,1)[0]['ptime'])  else False

def user_tweets(name, n):
# Fetch tweets of the specified user.
    tweets = []
    try:
        user = tweepy.api.get_user(name)
    except tweepy.TweepError as e:
        print 'Fail to identify the user %s! TweepError: %s.' % name, e
    try:
        timeline_entities =  user.timeline(count=n, include_entities=True, include_rts=True):
        for entity in timeline_entities:
            try:
                tweet = {}
                tweet['secret'] = secret
                tweet['name'] = name
                tweet['id'] = str(entity.id)
                tweet['ptime'] = entity.created_at.strftime("%Y-%m-%d %H:%M:%S")
                tweet['text'] = entity.text.encode('utf-8')
                if 'media' in entity.entities:
                    #if entity.entities['media'][0]['type'] == 'photo':
                    tweet['img'] = urllib2.urlopen(entity.entities['media'][0]['media_url']).read()
                    if 'url' in entity.entities['media'][0]:
                        tweet['text'] = entity.text.replace(entity.entities['media'][0]['url'], entity.entities['media'][0]['expanded_url']).encode('utf-8')
                else:
                    tweet['img'] = ''
                if entity.entities['urls']:
                    for i in range(len(entity.entities['urls'])):
                        tweet['text'] = entity.text.replace(entity.entities['urls'][i]['url'], entity.entities['urls'][i]['expanded_url']).encode('utf-8')
                    #tweet['img'] = ''
                #else:
                #    tweet['img'] = ''
                tweet['src'] = 'twitter'
                tweet['type'] = str(int(entity.retweeted))
                tweets.append(tweet)
            except:
                print 'A bad tweet to fetch.'
    except tweepy.TweepError as e:
        print "Fails to fetch %s's timeline. TweepError is %s." % name, e
        
    return tweets

def post_tweets(tweets, last):
# Send user tweets through HTTP post method.
    post_status = []
    post_url = url+"/postMsg.php?"
    for tweet in tweets:
        if trans_datetime(tweet['ptime']) > trans_datetime(last):
            req = urllib2.Request(post_url, urllib.urlencode(tweet))
            post_status.append(urllib2.urlopen(req).read()) 
    return post_status

def crawl_tweets():
# Crawl tweets of users in the user lists
    results = user_list(url, secret)
    print 'Twitter user list:'
    print results
    post_statuses = []
    if results:
        for result in results:
            if check_new(result['last'], result['name']):
                print '%s has NEW tweets posted!' % result['name']
                post_status = post_tweets(user_tweets(result['name'], 20), result['last'])
                print post_status
                post_statuses.append(post_status)
            else:
                print '%s has no tweets posted...' % result['name']
            sleep(15)
    return post_statuses
    

def print_tweets(s,n):
#Print tweets of the specified user.
    tweets = user_tweets(s,n)
    for tweet in tweets:
        print tweet['text']

if __name__=="__main__":
    try:
        i = 0
        while 1:
            i += 1
            print datetime.now()
            print "Crawl tweets %d time!" % i
            crawl_tweets()
            print 'Crawl sleeping...'
            sleep(60*30)
    except:
        print "Crawl stops!"
