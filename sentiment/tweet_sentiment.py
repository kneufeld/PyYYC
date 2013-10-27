import sys
import json

def main():
    AFINN_file = open(sys.argv[1])
    tweetOut_file = open(sys.argv[2])
    sentDict = {}
    for line in AFINN_file:
        word, sentiment = line.split("\t")
        sentDict[word] = int(sentiment)
    for line in tweetOut_file:
        twit = json.loads(line)
        try:
            score = 0
            for word in twit['text'].split():
                if word in sentDict:
                    score += sentDict[word]
            print score
        except KeyError:
            print 0

if __name__ == '__main__':
    main()
