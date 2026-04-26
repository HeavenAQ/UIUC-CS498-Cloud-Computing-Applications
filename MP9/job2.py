import sys
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from pyspark.sql.functions import col, floor
from pyspark.sql.types import IntegerType

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
# Get Spark context
sc = SparkContext()
# From spark context get glue context and spark session
glueContext = GlueContext(sc)
# Create and init job
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Begin TODOs - add your code starting from here. Comments
# are provided for each statement that you may need to add.

# 1. Create a Glue client to access the Data Catalog API
glue = boto3.client("glue", region_name="us-east-1")

# 2. Create a dynamic frame from AWS Glue catalog table. In the following lines
# use the create_dynamic_frame.from_catalog() API of the GlueContext class. Use
# the Glue catalog database and table name (output of job 1) as arguments.
dyf = glueContext.create_dynamic_frame.from_catalog(
    database="hw9-crawler-db",
    table_name="flights",
    transformation_ctx="dyf",
)


# 3. Get Spark dataframe from the Glue dynamic frame created above
df = dyf.toDF()

# 4. Create a new time_zone_difference column and add it to the Spark data frame.
# See the MP description on how to calculate the value of the time zone
# difference between the arrival and departure airports. You may need to check the
# data type when doing the time zone difference calculations to get the correct values.
df = df.withColumn(
    "time_zone_difference",
    (
        (floor(col("scheduled_arrival") / 100) * 60 + (col("scheduled_arrival") % 100))
        - (
            floor(col("scheduled_departure") / 100) * 60
            + (col("scheduled_departure") % 100)
            + col("scheduled_time")
        )
    )
    % (24 * 60),
)

# 5. Convert Spark data frame back to Glue dynamic frame
# Note - you can do step 4 using AWS Glue dynamic frame APIs also if you want
# to avoid steps 3 and 5. However, it maybe easier to do the transformations
# in step 4 using Spark data frame.
dynamic_frame = DynamicFrame.fromDF(df, glueContext, "dyf")

# 6. Get the existing Glue catalog table schema. You can use the glue client
# created in step 1 and use its get_table() API to get the table schema which
# will be a python dictionary. You can see the response of get_table() here:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue/client/get_table.html
response = glue.get_table(DatabaseName="hw9-crawler-db", Name="flights")
table = response["Table"]

table_input = {
    "Name": table["Name"],
    "StorageDescriptor": {
        "Columns": table["StorageDescriptor"]["Columns"],
        "Location": table["StorageDescriptor"]["Location"],
        "InputFormat": table["StorageDescriptor"]["InputFormat"],
        "OutputFormat": table["StorageDescriptor"]["OutputFormat"],
        "SerdeInfo": {
            "SerializationLibrary": table["StorageDescriptor"]["SerdeInfo"][
                "SerializationLibrary"
            ],
        },
    },
    "PartitionKeys": table.get("PartitionKeys", []),
    "TableType": table.get("TableType", "EXTERNAL_TABLE"),
}

# 7. Delete the following fields in the table schema dictionary as
# the update_table API gives ParamValidationError when these fields are present:
# 'UpdateTime', 'IsRegisteredWithLakeFormation', 'CreatedBy', 'DatabaseName',
# 'CreateTime', 'CatalogId'. If there is an error related to 'VersionId', that
# field also needs to be deleted.

# 8. Define the new column 'time_zone_difference' to be added to the table schema
# 9. Append the new column info to the table dictionary (obtained in step 6) columns list
columns = table_input["StorageDescriptor"]["Columns"]
if not any(c["Name"] == "time_zone_difference" for c in columns):
    columns.append({"Name": "time_zone_difference", "Type": "int"})


# 10. Update the table with the new schema. Use the update_table() API of glue client:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue/client/update_table.html
glue.update_table(
    DatabaseName="hw9-crawler-db",
    TableInput=table_input,
    SkipArchive=True,
)

# 11. Get the output S3 bucket in which the transformed table data will be
# stored. Use the getSink() API of the GlueContext class.
sink = glueContext.getSink(
    path="s3://mp9-job1-transformed-data/job2-output/",
    connection_type="s3",
    enableUpdateCatalog=True,
    updateBehavior="UPDATE_IN_DATABASE",
)

# 12. Set the catalog database and table using the setCatalogInfo() API on
# the object obtained in step 11.
s3 = boto3.resource("s3")
bucket = s3.Bucket("mp9-job1-transformed-data")
bucket.objects.filter(Prefix="job2-output/").delete()
sink.setCatalogInfo(
    catalogDatabase="hw9-crawler-db",
    catalogTableName="flights_transformed",
)


# 13. Set the format to 'json' using setFormat() API
sink.setFormat("json")

# 14. Write data into S3 bucket using writeFrame()
sink.writeFrame(dynamic_frame)

# End TODOs

# Commit job
job.commit()
