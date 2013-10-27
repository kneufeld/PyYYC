import sys
import json

def main():
    sentiment_file = open(sys.argv[1])
    tweets_file = open(sys.argv[2])
    sentiments = {}
    missing = {}
    
    for line in sentiment_file:
        term, score = line.split("\t")
        sentiments[term] = float(score)
    
    for tweet in tweets_file:
        tw = json.loads(tweet)
        try:
            score = 0.0
            tw_missing = []
            for word in tw['text'].split():
                if word in sentiments:
                    score += sentiments[word]
                else:
                    tw_missing.append(word)
            for word in tw_missing:
                if word in missing:
                    missing[word]['sum'] += score/len(tw['text'].split())
                    missing[word]['number'] += 1.0
                else:
                    missing[word] = {'sum': score/len(tw['text'].split()), 'number': 1.0}
        except KeyError:
            pass
    
    for word, scores in missing.iteritems():
        print "%s %s" % (word, scores['sum']/scores['number'])

if __name__ == '__main__':
    main()
