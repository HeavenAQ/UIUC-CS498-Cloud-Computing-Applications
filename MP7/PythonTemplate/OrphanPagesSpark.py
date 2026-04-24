#!/usr/bin/env python
# Use LF instead of CRLF for end-of-line in files for Windows compatibility.

import sys
from pyspark import SparkConf, SparkContext

conf = SparkConf().setMaster("local").setAppName("OrphanPages")
conf.set("spark.driver.bindAddress", "127.0.0.1")
sc = SparkContext(conf=conf)

lines = sc.textFile(sys.argv[1], 1)
page_links = lines.map(lambda line: line.split(": "))
pages = page_links.map(lambda page_link: page_link[0])
links = page_links.flatMap(lambda page_link: page_link[1].split())
distinct_links = links.distinct()
orphans = pages.subtract(distinct_links)
orphans = orphans.sortBy(lambda x: x)

# TODO
output = open(sys.argv[2], "w")
for orphan in orphans.collect():
    output.write(f"{orphan}\n")

# TODO
# write results to output file. Foramt for each line: (line + "\n")

sc.stop()
