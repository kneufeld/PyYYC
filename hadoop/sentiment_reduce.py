#!/usr/bin/env python

import sys

(last_key, score, num_tweets) = (None, 0, 0) 
for line in sys.stdin:
	(key, val) = line.strip().split("\t") 
	val = int(val)
	if last_key and last_key != key:
		print "%s\t%s" % (last_key, float(score)/num_tweets)
		(last_key, score, num_tweets) = (key, val, 1) 
	else:
		(last_key, score, num_tweets) = (key, score + val, num_tweets + 1)

if last_key:
	print "%s\t%s" % (last_key, float(score)/num_tweets)
