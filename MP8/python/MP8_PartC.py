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


# Spark SQL - DataFrame API
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


####
# 3. Filtering : Count the number of appearances of word 'ATTRIBUTE'
####
rdd, df = load_rdd_and_df("./gbooks")
print(df.where("word = 'ATTRIBUTE'").selectExpr("count(*)").show())

# Spark SQL

# +--------+
# |count(1)|
# +--------+
# |      11|
# +--------+
