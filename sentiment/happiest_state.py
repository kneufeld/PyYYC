import sys
import json
import re

def main():
    sentiment_file = open(sys.argv[1])
    tweets_file = open(sys.argv[2])
    sentiments = {}
    states = {}
    for line in sentiment_file:
        term, score = line.split("\t")
        sentiments[term] = int(score)
    for tweet in tweets_file:
        twit = json.loads(tweet)
        if not twit:
            continue 
        try:
            if not twit['place']:
                continue
            if twit['place']['country_code'] == 'US':
                if twit['place']['full_name']:
                    try:
                        state = twit['place']['full_name'].split(',')[1].strip()
                        if not re.match('^[A-Z]{2}$', state):
                            continue
                        if state == 'US':
                            continue
                        score = 0
                        for word in twit['text'].split():
                            if word in sentiments:
                                score += sentiments[word]
                        if not state in states:
                            states[state] = {'score': 0.0, 'num': 0.0}
                        states[state]['score'] += score
                        states[state]['num'] += 1.0
                    except IndexError:
                        pass
        except KeyError:
            pass
    avg_states = []
    for state, values in states.iteritems():
        avg_states.append((values['score']/values['num'], state))
    avg_states.sort(reverse=True)
    print avg_states[0][1]

if __name__ == '__main__':
    main()