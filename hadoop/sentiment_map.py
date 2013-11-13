#!/usr/bin/env python

import json 
import sys
import subprocess

AFINN_file = subprocess.Popen(['hadoop', 'fs', '-cat', '/user/hdfs/tweets/AFINN-111.txt'], stdout=subprocess.PIPE)
sentDict = {}
for line in AFINN_file.stdout:
    word, sentiment = line.split("\t")
    sentDict[word] = int(sentiment)

for line in sys.stdin:
    try:
        tweet = json.loads(line)
    	words = [w.lower() for w in tweet['text'].split()]
    	key = False
    	#potential android keywords
    	android_kws = ['android', '#android', 'android.', 'droid', 'nexus']
    	#potential iphone keywords
    	iphone_kws = ['iphone', '#iphone', 'ios', 'iphone5', 'iphone4', 'iphone3']
    	#determine if the tweet contains keywords
    	has_android = [w for w in words if w in android_kws]
    	has_iphone = [w for w in words if w in iphone_kws]
    	#only take tweets that have android or iphone in them, not both
    	if has_android and not has_iphone:
    	    key = 'android'
    	elif has_iphone and not has_android:
    	    key = 'iphone'
    	#if it is classified
    	if key:
    	    try:
    	        score = 0
    	        for w in words:
    	            if w in sentDict:
    	                #if a tweet word has a known sentiment
    	                score += sentDict[w]
    	        #send score along to reducers
    	        print "%s\t%s" % (key, score)
    	    #this is just in case something weird happend with the dictionary - 
    	    #- with so many tweets we don't really care if a couple get missed
    	    except KeyError:
    	        pass
    except:
        pass
