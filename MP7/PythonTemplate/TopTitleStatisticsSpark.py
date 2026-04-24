#!/usr/bin/env python
# Use LF instead of CRLF for end-of-line in files for Windows compatibility.
# Do not change the existing code as it may lead to unexpected errors.

import sys
from pyspark import SparkConf, SparkContext

conf = SparkConf().setMaster("local").setAppName("TopTitleStatistics")
conf.set("spark.driver.bindAddress", "127.0.0.1")
sc = SparkContext(conf=conf)

lines = sc.textFile(sys.argv[1], 1)

numbers = lines.map(lambda line: int(line.split("\t", 1)[1]))
total = numbers.sum()
mean = total // numbers.count()
smallest = numbers.min()
largest = numbers.max()
var = numbers.map(lambda x: (x - mean) ** 2).sum() // numbers.count()


# TODO

outputFile = open(sys.argv[2], "w")
"""
TODO write your output here
write results to output file. Format
outputFile.write('Mean\t%s\n' % ans1)
outputFile.write('Sum\t%s\n' % ans2)
outputFile.write('Min\t%s\n' % ans3)
outputFile.write('Max\t%s\n' % ans4)
outputFile.write('Var\t%s\n' % ans5)
"""
outputFile.write("Mean\t%s\n" % mean)
outputFile.write("Sum\t%s\n" % total)
outputFile.write("Min\t%s\n" % smallest)
outputFile.write("Max\t%s\n" % largest)
outputFile.write("Var\t%s\n" % var)

sc.stop()
