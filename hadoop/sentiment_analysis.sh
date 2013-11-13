hadoop jar /usr/lib/hadoop/contrib/streaming/hadoop-*streaming*.jar \
-D mapred.max.split.size=67108864 \
-D mapred.map.tasks=100 \
-D mapred.reduce.tasks=10 \
-input /user/hdfs/tweets/ \
-output testOutput \
-mapper /home/hdfs/sentiment_map.py \
-reducer /home/hdfs/sentiment_reduce.py \
-file /home/hdfs/sentiment_map.py \
-file /home/hdfs/sentiment_reduce.py