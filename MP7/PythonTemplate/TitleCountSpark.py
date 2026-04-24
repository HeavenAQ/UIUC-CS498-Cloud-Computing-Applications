#!/usr/bin/env python

# Use LF instead of CRLF for end-of-line in files for Windows compatibility.
# Do not change the existing code as it may lead to unexpected errors.
"""Exectuion Command: spark-submit TitleCountSpark.py stopwords.txt delimiters.txt dataset/titles/ dataset/output"""

import sys
from pyspark import SparkConf, SparkContext

stopWordsPath = sys.argv[1]
delimitersPath = sys.argv[2]

with open(stopWordsPath) as f:
    stop_words = set(f.read().splitlines())

with open(delimitersPath) as f:
    delimiters = f.readline()

conf = SparkConf().setMaster("local").setAppName("TitleCount")
conf.set("spark.driver.bindAddress", "127.0.0.1")
sc = SparkContext(conf=conf)

lines = sc.textFile(sys.argv[3], 1)

# TODO
table = str.maketrans(delimiters, "," * len(delimiters))
words = lines.flatMap(
    lambda line: line.translate(table).casefold().split(","),
)
filtered = words.filter(
    lambda word: word != "" and word not in stop_words,
)
counts = filtered.map(lambda w: (w, 1)).reduceByKey(lambda a, b: a + b)


top10 = counts.takeOrdered(10, key=lambda x: (-x[1], x[0]))

outputFile = open(sys.argv[4], "w")

# TODO
# write results to output file. Foramt for each line: (line +"\n")
for word, count in sorted(top10):
    outputFile.write("%s\t%s\n" % (word, count))

sc.stop()
