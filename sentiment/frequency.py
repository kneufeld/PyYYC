import sys
import json

def main():
    tweets_file = open(sys.argv[1])
    words = {}
    wc = 0
    for tweet in tweets_file:
        twit = json.loads(tweet)
        try:
            for word in twit['text'].split():
                wc += 1.0
                if word in words:
                    words[word] += 1.0
                else:
                    words[word] = 1.0
        except KeyError:
            pass
    for word, number in words.iteritems():
        print "%s %s" % (word, number/wc)

if __name__ == '__main__':
    main()
