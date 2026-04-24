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
# 2. Counting : How many lines does the file contains? Answer this question via both RDD api & #Spark SQL
####
rdd, df = load_rdd_and_df("./gbooks")
print(df.selectExpr("count(*)").show())

# Spark SQL

# sqlContext.sql(query).show() or df.show()
# +--------+
# |count(1)|
# +--------+
# |   50013|
# +--------+
