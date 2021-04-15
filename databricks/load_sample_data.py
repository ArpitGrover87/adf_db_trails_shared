# Databricks notebook source
try:
  dbutils.fs.mount(
    source = "wasbs://source@"+storageName+".blob.core.windows.net",
    mount_point = "/mnt/source",
    extra_configs = {"fs.azure.account.key.tmpstoragedevrchd01.blob.core.windows.net":accessKey})
except Exception as e:
  if "Directory already mounted" in str(e):
    print("Directory already mounted")
    pass # Ignore error if already mounted.
  else:
    raise e
#"abfss://{container}@{storage_acct}.dfs.core.windows.net/".format(container=dbutils.secrets.get(scope="rchkeys",key="storage-container"), storage_acct= dbutils.secrets.get(scope="rchkeys",key="storage-name"

# COMMAND ----------

dbutils.fs.ls("/mnt/source")

# COMMAND ----------

df = spark.read.csv("dbfs:/databricks-datasets/COVID/covid-19-data/us.csv",header='true', inferSchema='true')

# COMMAND ----------

display(df)

# COMMAND ----------



# COMMAND ----------

df.coalesce(1).write.mode("overwrite").option("header", "true").format("com.databricks.spark.csv").csv("/mnt/source/input")

# COMMAND ----------

# dbutils.fs.ls("/mnt/source/input")

# COMMAND ----------

# df = spark.read.csv("/mnt/source/input/coviddata_us.csv", header='true', inferSchema='true')
# display(df)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- CREATE DATABASE if not exists coviddata
# MAGIC -- LOCATION "/mnt/source/input"

# COMMAND ----------

# df.write.mode("overwrite").saveAsTable("coviddata.coviddata_us")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- select * from coviddata.coviddata_us

# COMMAND ----------

dbutils.fs.refreshMounts()

# COMMAND ----------

dbutils.fs.unmount("/mnt/source")