from pyspark import SparkContext
from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType, IntegerType
from pyspark.sql import SparkSession

sc = SparkContext()
spark = SparkSession.builder.getOrCreate()
####
# 1. Setup : Write a function to load it in an RDD & DataFrame
####


# RDD API
# Columns:
# 0: word (string), 1: year (int), 2: frequency (int), 3: books (int)
def load_rdd_and_df(file: str):
    rdd = sc.textFile(file).map(
        lambda line: [int(word) if word.isdigit() else word for word in line.split()]
    )
    schema = StructType(
        [
            StructField("word", StringType(), nullable=True),
            StructField("year", IntegerType(), nullable=True),
            StructField("frequency", IntegerType(), nullable=True),
            StructField("books", IntegerType(), nullable=True),
        ]
    )
    df = spark.createDataFrame(rdd, schema)
    return rdd, df


# Spark SQL - DataFrame API


####
# 5. Joining : The following program construct a new dataframe out of 'df' with a much smaller size.
####
rdd, df = load_rdd_and_df("./gbooks")

df2 = df.select("word", "year").distinct().orderBy("year", "word").limit(100)
df2.createOrReplaceTempView("gbooks2")

# Now we are going to perform a JOIN operation on 'df2'. Do a self-join on 'df2' in lines with the same #'count1' values and see how many lines this JOIN could produce. Answer this question via Spark SQL API

# Spark SQL API
result = df2.join(df2, "year")
print(result.count())

# output: 310
