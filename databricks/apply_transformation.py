# Databricks notebook source
# MAGIC %md
# MAGIC ##### Define Widgets/ Parameters
# MAGIC Creating widgets for leveraging parameters to be passed from Azure Data Factory

# COMMAND ----------

dbutils.widgets.text("targetContainer", "","") 
dbutils.widgets.get("targetContainer")

dbutils.widgets.text("input", "","") 
dbutils.widgets.get("input")

dbutils.widgets.text("output", "","") 
dbutils.widgets.get("output")

dbutils.widgets.text("filename", "","") 
dbutils.widgets.get("filename")

dbutils.widgets.text("pipelineRunId", "","") 
dbutils.widgets.get("pipelineRunId")



# COMMAND ----------

# MAGIC %md
# MAGIC ##### Mount Storage as DBFS
# MAGIC Assumptions:
# MAGIC - the target container **sinkdata** and folder '**staged_data**' exists. 
# MAGIC - If running through ADF the copy data will create the target resource

# COMMAND ----------

#Supply storageName and accessKey values

storageName = dbutils.secrets.get(scope="test",key="storageName")
accessKey = dbutils.secrets.get(scope="test",key="accesskey")

try:
  dbutils.fs.mount(
    source = "wasbs://"+getArgument("targetContainer")+"@"+storageName+".blob.core.windows.net/",
    mount_point = "/mnt/adfdata",
    extra_configs = {"fs.azure.account.key."+storageName+".blob.core.windows.net":
                     accessKey})
except Exception as e:
  if "Directory already mounted" in str(e):
    print("Directory already mounted")
    pass # Ignore error if already mounted.
  else:
    raise e

# COMMAND ----------

# MAGIC %md
# MAGIC check to see what's in the mount by using `dbutils.fs.ls`

# COMMAND ----------

dbutils.fs.ls("/mnt/adfdata/staged_data")

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC **Read raw files**

# COMMAND ----------

# read raw data
from pyspark.sql.functions import desc

inputFile = "dbfs:/mnt/adfdata"+getArgument("input")+"/"+getArgument("filename")
rawDF = (spark.read           
  .option("header", "true")      
  .option("inferSchema", "true")  
  .csv(inputFile)                
)



# COMMAND ----------

#Removing Extension from filename
import os
file = os.path.splitext(getArgument("filename"))[0]
print(file)

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC **Write raw files**

# COMMAND ----------

rawDF.coalesce(1).write.mode("overwrite").option("header", "true").csv("dbfs:/mnt/adfdata"+getArgument("output")+"/"+file+"_raw_"+getArgument("pipelineRunId")+"/csv") 

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC **Read delta files**

# COMMAND ----------

from pyspark.sql.functions import to_date, col, expr

# COMMAND ----------

covidUSDailyDF = spark.read \
  .option("header", "true") \
  .option("inferSchema", "true") \
  .csv(inputFile)\
  .withColumn("date", to_date(col("date"), 'yyyy-MM-dd'))

# COMMAND ----------

covidUSDailyDF.write.format("delta")\
.mode("overwrite")\
.partitionBy("date")\
.save("dbfs:/mnt/adfdata"+getArgument("output")+"/"+file+"_delta_"+getArgument("pipelineRunId")+"/")

# COMMAND ----------

covidUSDailyDF_delta = spark.read.format("delta").load("dbfs:/mnt/adfdata"+getArgument("output")+"/"+file+"_delta_"+getArgument("pipelineRunId")+"/")

display(covidUSDailyDF_delta)

# COMMAND ----------

display(covidUSDailyDF)

# COMMAND ----------

spark.sql("DROP TABLE IF EXISTS delta_test")

spark.sql("CREATE TABLE delta_test USING DELTA LOCATION '{}'".format("/mnt/adfdata"+getArgument("output")+"/"+file+"_delta_"+getArgument("pipelineRunId")+"/"))

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from delta_test

# COMMAND ----------

