"""
Created on Mar 01 2021
@author: José Antonio Espinosa Melchor
         Jerónimo Arenas García

Import PATSTAT tables into parquet format
"""

from configparser import ConfigParser
from pathlib import Path
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

if __name__ == "__main__":

    spark = SparkSession.builder.appName("PythonSort").getOrCreate()

    sc = spark.sparkContext

    print(sc.version)

    # Relevant directories are read from the config file:
    # dir_raw:     full path to hdfs directory where the raw data .gz files are stored
    # dir_parquet: full path to hdfs directory where the parquet tables will be stored

    cf = ConfigParser()
    cf.read("config.cf")

    dir_raw = Path(cf.get("patstat", "dir_raw"))
    dir_parquet = Path(cf.get("patstat", "dir_parquet"))

    # Configuration hdfs
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
    hdfs_dir_parquet = spark._jvm.org.apache.hadoop.fs.Path(dir_parquet.as_posix())
    hdfs_dir_raw = spark._jvm.org.apache.hadoop.fs.Path(dir_raw.as_posix())

    # Create output directories for the parquet files if they do not exist
    if not fs.exists(hdfs_dir_parquet):
        fs.mkdirs(hdfs_dir_parquet)

    ####
    ## STEP 1: Save all PATSTAT tables to parquet
    ####
    tables = [el.getPath().getName() for el in fs.listStatus(hdfs_dir_raw)]
    tables = list(set([el.split("_")[0] for el in tables if (el.endswith(".gz") or el.endswith(".csv"))]))

    for tbl in sorted(tables):
        # Read all gz or CSV of same table
        df = spark.read.csv(f"{dir_raw.joinpath(tbl).as_posix()}*", header=True)
        # Save to parquet
        df.write.parquet(
            dir_parquet.joinpath(f"{tbl}.parquet").as_posix(),
            mode="overwrite",
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

    patstat_appln = (
        df_201.join(df_202, df_201.appln_id == df_202.appln_id, "left")
        .drop(df_202.appln_id)
        .join(df_203, df_201.appln_id == df_203.appln_id, "left")
        .drop(df_203.appln_id)
    )

    patstat_appln.write.parquet(
        dir_parquet.joinpath(f"patstat_appln.parquet").as_posix(),
        mode="overwrite",
    )

    print("Created table patstat_appln")
    print("- Rows:", patstat_appln.count())

    ####
    ## STEP 3: Do the same for citations
    ####

    # Key bibliographical data elements relevant to identify patent publications
    pub = spark.read.parquet(dir_parquet.joinpath("tls211.parquet").as_posix()).select(
        "pat_publn_id", "publn_kind", "appln_id"
    )

    # NPL publications
    npl = spark.read.parquet(dir_parquet.joinpath("tls214.parquet").as_posix()).select("npl_publn_id", "npl_doi")

    # Links between publications, applications and non-patent literature documents with regards to citations.
    cit = spark.read.parquet(dir_parquet.joinpath("tls212.parquet").as_posix()).select(
        "pat_publn_id",
        "cited_pat_publn_id",
        "cited_appln_id",
        "cited_npl_publn_id",
    )
    cit_appln = cit.select("pat_publn_id", "cited_appln_id").where(
        (F.col("cited_appln_id").isNotNull()) & (F.col("cited_appln_id") != "0")
    )
    cit_publn = cit.select("pat_publn_id", "cited_pat_publn_id").where(
        (F.col("cited_pat_publn_id").isNotNull()) & (F.col("cited_pat_publn_id") != "0")
    )
    # Non patent literature publication
    cit_npl = cit.select("pat_publn_id", "cited_npl_publn_id").where(
        (F.col("cited_npl_publn_id").isNotNull()) & (F.col("cited_npl_publn_id") != "0")
    )

    # First, join appln_ids with docdb_family_id in publications
    fam = patstat_appln.select(F.col("appln_id").alias("appln_id_f"), "docdb_family_id")
    pub_fam = pub.join(fam, pub.appln_id == fam.appln_id_f, "left").drop("appln_id_f")
    # Get source and destination families
    pbf_src = pub_fam.select(*(F.col(el).alias(el + "_src") for el in pub_fam.columns))
    pbf_dst = pub_fam.select(*(F.col(el).alias(el + "_dst") for el in pub_fam.columns))

    # Then, convert citations through appln_ids to citations using docdb_family_id
    # This one joins pat_publn-pat_publn
    cit_fam_publn = (
        cit_publn.join(
            pbf_src,
            cit_publn.pat_publn_id == pbf_src.pat_publn_id_src,
            "left",
        )
        .join(
            pbf_dst,
            cit_publn.cited_pat_publn_id == pbf_dst.pat_publn_id_dst,
            "left",
        )
        .drop("pat_publn_id", "cited_pat_publn_id")
        .select(
            "appln_id_src",
            "pat_publn_id_src",
            "publn_kind_src",
            "docdb_family_id_src",
            "appln_id_dst",
            "pat_publn_id_dst",
            "publn_kind_dst",
            "docdb_family_id_dst",
        )
    )
    # and this one is pat_publn-appln_id
    cit_fam_appln = (
        cit_appln.join(
            pbf_src,
            cit_appln.pat_publn_id == pbf_src.pat_publn_id_src,
            "left",
        )
        .join(
            pbf_dst,
            cit_appln.cited_appln_id == pbf_dst.appln_id_dst,
            "left",
        )
        .drop("pat_publn_id", "cited_appln_id")
        .select(
            "appln_id_src",
            "pat_publn_id_src",
            "publn_kind_src",
            "docdb_family_id_src",
            "appln_id_dst",
            "pat_publn_id_dst",
            "publn_kind_dst",
            "docdb_family_id_dst",
        )
    )

    npl = npl.select(*(F.col(c).alias(f"{c}_dst") for c in npl.columns))
    cit_fam_npl = (
        cit_npl.join(
            pbf_src,
            cit_npl.pat_publn_id == pbf_src.pat_publn_id_src,
            "left",
        )
        .join(
            npl,
            cit_npl.cited_npl_publn_id == npl.npl_publn_id_dst,
            "left",
        )
        .drop("pat_publn_id", "cited_npl_publn_id")
        .select(
            "appln_id_src",
            "pat_publn_id_src",
            "publn_kind_src",
            "docdb_family_id_src",
            "npl_publn_id_dst",
            "npl_doi_dst",
        )
    )

    # Merge them into a big dataframe where all publications/appln_ids/docdb families are combined
    cit_fam = (
        cit_fam_publn.unionByName(cit_fam_appln)
        # .unionByName(cit_fam_npl)
        .withColumn(
            "autoCit",
            F.col("docdb_family_id_src") == F.col("docdb_family_id_dst"),
        )
    )

    # Save
    cit_fam.write.parquet(
        dir_parquet.joinpath(f"fam_citations.parquet").as_posix(),
        mode="overwrite",
    )

    cit_fam_npl.write.parquet(
        dir_parquet.joinpath(f"npl_citations.parquet").as_posix(),
        mode="overwrite",
    )

    """patstat_appln = spark.read.parquet(dir_parquet.joinpath(f"patstat_appln.parquet").as_posix())
    patstat_appln = patstat_appln.filter(patstat_appln.appln_abstract.isNotNull())
    patstat_appln.count()
    """
