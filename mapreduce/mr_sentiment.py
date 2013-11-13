import MapReduce
import sys

"""
Twitter Sentiment Analysis in the Simple Python MapReduce Framework
"""

mr = MapReduce.MapReduce()

# =============================
# Do not modify above this line


def load_sentiments():
    '''Load the known sentiments into a dictionary keyed by word
    '''
    AFINN_file = open('../sentiment/AFINN-111.txt')
    sentDict = {}
    for line in AFINN_file:
        word, sentiment = line.split("\t")
        sentDict[word] = int(sentiment)
    return sentDict

sentiments = load_sentiments()

def mapper(tweet):
    #split the tweet into words and make them all lowercase
    words = [w.lower() for w in tweet['text'].split()]
    key = False
    #potential android keywords
    android_kws = ['android', '#android', 'android.', 'droid', 'nexus']
    #potential iphone keywords
    iphone_kws = ['iphone', '#iphone', 'ios', 'iphone5', 'iphone3', 'iphone3']
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
                if w in sentiments:
                    #if a tweet word has a known sentiment
                    score += sentiments[w]
            #send score along to reducers
            mr.emit_intermediate(key, score)  
        #this is just in case something weird happend with the dictionary - 
        #- with so many tweets we don't really care if a couple get missed
        except KeyError:
            #we want to know about it though
            print 'KeyError on tweet %s' % tweet['text']

def reducer(key, list_of_values):
    # key: word
    # value: list of sentiment scores
    total = 0
    for v in list_of_values:
        total += v
    mr.emit((key, float(total)/len(list_of_values)))

# Do not modify below this line
# =============================
if __name__ == '__main__':
    inputdata = open(sys.argv[1])
    mr.execute(inputdata, mapper, reducer)
