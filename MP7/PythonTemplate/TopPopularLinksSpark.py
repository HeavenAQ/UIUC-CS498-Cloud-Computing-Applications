#!/usr/bin/env python
# Use LF instead of CRLF for end-of-line in files for Windows compatibility.
# Do not change the existing code as it may lead to unexpected errors.

import sys
from pyspark import SparkConf, SparkContext

conf = SparkConf().setMaster("local").setAppName("TopPopularLinks")
conf.set("spark.driver.bindAddress", "127.0.0.1")
sc = SparkContext(conf=conf)

lines = sc.textFile(sys.argv[1], 1)
page_links = lines.map(lambda line: line.split(": "))
links = page_links.flatMap(lambda page_link: page_link[1].split())
link_counts = links.map(lambda link: (link, 1)).reduceByKey(lambda a, b: a + b)
top10 = link_counts.takeOrdered(10, key=lambda x: (-x[1], x[0]))

# TODO

output = open(sys.argv[2], "w")
for id, count in sorted(top10):
    output.write(f"{id}\t{count}\n")

# TODO
# write results to output file. Foramt for each line: (key + \t + value +"\n")

sc.stop()
