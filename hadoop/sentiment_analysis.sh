hadoop jar /usr/lib/hadoop/contrib/streaming/hadoop-*streaming*.jar \
-input /user/hdfs/tweets/mobileWar.json \
-output testOutput \
-mapper /home/hdfs/sentiment_map.py \
-reducer /home/hdfs/sentiment_reduce.py \
-file /home/hdfs/sentiment_map.py \
-file /home/hdfs/sentiment_reduce.py