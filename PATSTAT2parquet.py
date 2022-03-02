"""
Created on Mar 01 2021
@author: José Antonio Espinosa Melchor
         Jerónimo Arenas García

Import PATSTAT tables into parquet format
"""

from configparser import ConfigParser
from pathlib import Path
from pyspark.sql import SparkSession

if __name__ == "__main__":

    spark = SparkSession\
        .builder\
        .appName("PythonSort")\
        .getOrCreate()

    sc = spark.sparkContext

    print(sc.version)

    # Relevant directories are read from the config file:
    # dir_data:    full path to hdfs directory where the raw data .gz files are stored
    # dir_parquet: full path to hdfs directory where the parquet tables will be stored

    cf = ConfigParser()
    cf.read("config.cf")

    dir_data = Path(cf.get("spark", "dir_data"))
    dir_parquet = Path(cf.get("spark", "dir_parquet"))

    # Configuration hdfs
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
    hdfs_dir_parquet = spark._jvm.org.apache.hadoop.fs.Path(dir_parquet.as_posix())
    hdfs_dir_data = spark._jvm.org.apache.hadoop.fs.Path(dir_data.as_posix())

    # Create output directories for the parquet files if they do not exist
    if not fs.exists(hdfs_dir_parquet):
        fs.mkdirs(hdfs_dir_parquet)

    ####
    ## STEP 1: Save all PATSTAT tables to parquet
    ####
    tables = [el.getPath().getName() for el in fs.listStatus(hdfs_dir_data)]
    tables = list(set([el.split("_")[0] for el in tables if
                (el.endswith(".gz") or el.endswith(".csv"))]))

    for tbl in sorted(tables):
        # Read all gz or CSV of same table
        df = spark.read.csv(f"{dir_data.joinpath(tbl).as_posix()}*", header=True)
        # Save to parquet
        df.write.parquet(
            dir_parquet.joinpath(f"{tbl}.parquet").as_posix(),
            mode="overwrite"
        )
        print("Processed table", tbl, "- Rows:", df.count())

    ####
    ## STEP 2: Create a new table for Patent Applications
    ##         This is inefficient for Spark, so it is better to do it once
    ##         and keep the "JOIN" table as a separate parquet file
    ####

    df_201 = spark.read.parquet(dir_parquet.joinpath(f"tls201.parquet").as_posix())
    df_202 = spark.read.parquet(dir_parquet.joinpath(f"tls202.parquet").as_posix())
    df_203 = spark.read.parquet(dir_parquet.joinpath(f"tls203.parquet").as_posix())

    patstat_appln = (df_201.join(df_202, df_201.appln_id ==  df_202.appln_id, "left")
                        .drop(df_202.appln_id)
                        .join(df_203, df_201.appln_id ==  df_203.appln_id, "left")
                        .drop(df_203.appln_id)
                    )

    patstat_appln.write.parquet(
        dir_parquet.joinpath(f"patstat_appln.parquet").as_posix(),
        mode="overwrite",
    )

    print("Created table patstat_appln", "- Rows:", dpatstat_appln.count())

    """patstat_appln = spark.read.parquet(dir_parquet.joinpath(f"patstat_appln.parquet").as_posix())
    patstat_appln = patstat_appln.filter(patstat_appln.appln_abstract.isNotNull())
    patstat_appln.count()
    """



