#!/usr/bin/python
import facebook
import urllib2,urllib
from datetime import datetime
from time import sleep

url = "http://worldfun.sinaapp.com"
secret = "kmz4515jlm51"

access_token = "AAAEA5JDKlT0BAL6KQcdpNm8byB64kBpr5iZCnpcmZCcSEt6uCOm6Xbrri4PqUFBz5QS2iI2erkmn1PlvdZBCqnoKPO5s2dPZCuXbN0ABNQZDZD"
# The Facebook access_token expires after 60 days.

def user_list(url, secret):
    facebook_user = []
    user_list = eval(urllib2.urlopen(url+"/getUserList.php?secret="+secret).read())
    if user_list['status'] == 'ok':
        print 'User list status ok!'
        #print user_list
        for user in user_list['result']:
            if user['src'] == 'facebook':
                facebook_user.append(user)
    return facebook_user

def trans_datetime(str):
# Transform the string to datetime type.
    return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")

def check_new(last, name):
    return True if trans_datetime(last) < trans_datetime(user_facebook(name,1)[0]['ptime']) else False


def user_facebook(name, n):
# Fetch facebook updates of the specifies user.
    posts = []
    try:
        graph = facebook.GraphAPI(access_token)
        print 'Valid access_token.'
    except:
        print 'Invalid access_token.'
    try:
        feed = graph.get_object(name+'/posts', limit=n)
        if len(feed['data']) > 1:
            print len(feed['data'])
    except facebook.GraphAPIError as e:
        print 'Fail to fetch facebook posts. The GraphAPIError is %s.' % e
    for entity in feed['data']:
        try:
            post = {}
            post['secret'] = secret
            post['name'] = name
            if 'object_id' in entity:
                post['id'] = entity['object_id']
            else:
                post['id'] = entity['id'].split('_').pop()
            post['ptime'] = datetime.strptime(entity['created_time'], "%Y-%m-%dT%H:%M:%S+0000").strftime("%Y-%m-%d %H:%M:%S")
            if 'message' in entity:
                post['text'] = entity['message'].encode('utf-8')
            if 'picture' in entity:
                post['img'] = urllib2.urlopen(entity['picture']).read()
            else:
                post['img'] = ''
            post['src'] = 'facebook'
            if entity['status_type'].split('_')[0] == 'shared':
                post['type'] = '1'
            else:
                post['type'] = '0' 
            posts.append(post)
        except:
            print "A bad post to fetch!" 
    return posts

def post_posts(posts, last):
# Sent user posts through HTTP post method.
    post_status = []
    post_url = url+"/postMsg.php?" 
    for post in posts:
        if trans_datetime(post['ptime']) > trans_datetime(last):
            req = urllib2.Request(post_url, urllib.urlencode(post))
            post_status.append(urllib2.urlopen(req).read())
    return post_status

def crawl_facebook():
# Crawl posts of facebook account in user list.
    results = user_list(url, secret)
    if results:
        print 'Facebook user list:'
        print results
    else:
        print 'No facebook account to crawl.'
    post_statuses = []
    if results:
        for result in results:
            if check_new(result['last'], result['name']):
                print '%s has NEW facebook posts!' % result['name']
                post_status = post_posts(user_facebook(result['name'], 20), result['last'])
                print post_status
                post_statuses.append(post_status)
            else:
                print '%s has no facebook updates...' % result['name']
            sleep(15)
    return post_statuses


if __name__ == "__main__":
    try:
        i = 0
        while 1:
            i += 1
            print datetime.now()
            print "Crawl facebook %d time!" % i
            crawl_facebook()
            print 'Crawl sleeping...'
            sleep(60*30)
    except:
        print "Crawl stops!"
