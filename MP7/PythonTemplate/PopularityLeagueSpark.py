#!/usr/bin/env python
# Use LF instead of CRLF for end-of-line in files for Windows compatibility.
# Do not change the existing code as it may lead to unexpected errors.

# Execution Command: spark-submit PopularityLeagueSpark.py dataset/links/ dataset/league.txt
import sys
from pyspark import SparkConf, SparkContext

conf = SparkConf().setMaster("local").setAppName("PopularityLeague")
conf.set("spark.driver.bindAddress", "127.0.0.1")
sc = SparkContext(conf=conf)

lines = sc.textFile(sys.argv[1], 1)
page_links = lines.map(
    lambda line: line.split(": "),
).map(
    lambda line: (line[0], line[1].split()),
)
links = page_links.flatMap(lambda page_link: page_link[1])
link_counts = (
    links.map(lambda link: (link, 1)).reduceByKey(lambda a, b: a + b).collectAsMap()
)


# TODO

leagueIds = sc.textFile(sys.argv[2], 1)
leagueIds = leagueIds.collect()

league_pop = []
for id in leagueIds:
    popularity = link_counts.get(id)
    if popularity is None:
        continue
    league_pop.append((id, popularity))

results = []
for id, pop in league_pop:
    rank = sum(1 for _, p in league_pop if p < pop)
    results.append((id, rank))

# TODO

output = open(sys.argv[3], "w")
for id, rank in sorted(results, key=lambda x: x[0]):
    output.write(f"{id}\t{rank}\n")

# TODO
# write results to output file. Foramt for each line: (key + \t + value +"\n")

sc.stop()
