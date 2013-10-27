import sys
import json

def main():
    tweets_file = open(sys.argv[1])
    hashtags = {}
    for tweet in tweets_file:
        twit = json.loads(tweet)
        if not twit:
            continue
        try:
            if 'entities' in twit:
                for tags in twit['entities']['hashtags']:
                    text = tags['text']
                    if not text in hashtags:
                        hashtags[text] = 1
                    else:
                        hashtags[text] += 1
        except KeyError:
            pass
    hashtag_list = []
    for hashtag, freq in hashtags.iteritems():
        hashtag_list.append((freq, hashtag))
    hashtag_list.sort(reverse=True)
    for i in range(0,10):
        print "%s %s" % (hashtag_list[i][1], hashtag_list[i][0])

if __name__ == '__main__':
    main()