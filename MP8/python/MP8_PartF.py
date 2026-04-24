from pyspark.sql.functions import col, lag
from pyspark import SparkContext
from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType, IntegerType
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import *

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


###
# 2. Frequency Increase : analyze the frequency increase of words starting from the year 1500 to the year 2000
###
# Spark SQL - DataFrame API
rdd, df = load_rdd_and_df("./gbooks")

window = Window.partitionBy("word").orderBy("year")

df2 = df.select("word", "year", "frequency").where(
    (col("year") >= 1500) & (col("year") <= 2000)
)

# Remove words that appear only once
df2 = (
    df2.groupBy("word")
    .agg(count("*").alias("cnt"))
    .filter(col("cnt") > 1)
    .join(df, "word")
    .select("word", "year", "frequency")
    .where((col("year") >= 1500) & (col("year") <= 2000))
)

df2 = df2.withColumn(
    "frequency_increase",
    lead("frequency", 1, 0).over(window),
)

result = (
    df2.groupBy("word")
    .agg(sum("frequency_increase").alias("total_increase"))
    .orderBy(col("total_increase").desc(), col("word").asc())
)

result.show(20)
