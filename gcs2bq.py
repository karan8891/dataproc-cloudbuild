# Import required modules and packages
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.functions import sum


# Create Spark session
spark = SparkSession \
  .builder \
  .master('yarn') \
  .appName('spark-bigquery') \
  .getOrCreate()

# Define temporary GCS bucket for Dataproc to write it's process data
bucket='bucket_ncpl'
spark.conf.set('temporaryGcsBucket', bucket)

# Read data into Spark dataframe from CSV file available in GCS bucket
df=spark.read.option("header",True).csv('gs://bucket_ncpl/greenhouse-gas-emissions-industry-and-household-year-ended-2020.csv')

# Select limited columns and cast string type column to double
req_df=df.select(col('year'),col('anzsic_descriptor'),col('variable'),col('source'),col('data_value').cast('double'))

# Group by list of columns and SUM data_value 
req_df=req_df.groupBy('year','anzsic_descriptor','source').agg(sum('data_value').alias('sum_qty')).sort('year')

# Writing the data to BigQuery
req_df.write.format('bigquery').option('table', 'dataset_demo.agg_output').option('createDisposition','CREATE_IF_NEEDED').save()
spark.stop()