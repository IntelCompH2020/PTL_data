# Imports
import io
import json
import os
import re
import zipfile
from configparser import ConfigParser
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
#import py7zr
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col
from pyspark.sql.types import StringType

# Auxiliary Functions
#
# These functions are used to load, read, identify or save files.

## File processing


def get_only_letter(s):
    res = re.sub(r"[^a-zA-Z]", "", s)
    return res


def get_file_extension(f: Path):
    output = os.popen(f"file -b {f.as_posix()}")
    return output.read().split()[0]


def read_excel(f: Path):
    fname = None
    df = None
    try:
        fname = f.stem
        df = pd.read_excel(f, index_col=False)
        df.columns = df.columns.str.strip()

    except Exception as e:
        print("-- ERROR: file could not be processed")
        print("\t", e)
    return fname, df


def extract_file_info(f: Path):
    """
    Read a file and extract all its content into a pd.DataFrame()

    As a zip file can contain multiple inner files, we need to iterate
    over this function when calling it
    """
    fname = None
    df = None

    # Get type of file
    extension = get_file_extension(f)
    print(f"-- {extension}")

    if extension not in ["Zip", "7-zip"]:
        # Excel files (hopefully)
        fname, df = read_excel(f)
        yield fname, df
    else:
        # Compressed files
        if extension == "Zip":
            archive = zipfile.ZipFile(f.as_posix(), "r")
            content = {name: archive.read(name) for name in archive.namelist()}
        elif extension == "7-zip":
            with py7zr.SevenZipFile(f, "r") as archive:
                content = archive.readall()
        print("-- Files:")
        keys = [get_only_letter(k) for k in content.keys()]
        key_0 = keys[0]

        # Check if all elements are of the same table:
        all_equal = True if all(key_0 == x for x in keys) else False

        # Return info
        df_sub = []
        for k, v in content.items():
            print(f"-- -- {k}")
            df = pd.read_excel(v, engine="openpyxl")
            if all_equal:
                df_sub.append(df)
                continue
            else:
                fname = f.stem + "-" + re.sub("xlsx", "", get_only_letter(k))
                yield fname, df

        # Merge all into one dataframe if necessary
        if all_equal:
            fname = key_0
            df = pd.concat(df_sub, ignore_index=True)
            yield fname, df


## Spark conversion


def convert_spark(df: pd.DataFrame):
    """
    Transforms input pandas DataFrame into spark DataFrame
    """
    sparkDF = None

    # Clean DF
    # Strip column names
    df.columns = df.columns.str.strip()

    # Filter languages
    if "language" in df.columns.str.lower():
        df = df[(df.loc[:, df.columns.str.lower() == "language"] == "en").iloc[:, 0]]

    # Remove empty columns
    df = df.drop([c for c in df.columns if c.startswith("Unnamed:")], axis=1)

    # Replace NaN
    df = df.replace({np.nan: None})
    df.loc[:, df.isnull().all()] = ""

    # Format dates
    # date_cols = ["date" in i for i in df.columns.str.lower()]
    # df.loc[:, date_cols] = df.loc[:, date_cols].apply(pd.to_datetime, errors="coerce")
    date_cols = [c for c in df.columns if "date" in c.lower()]
    df[date_cols] = df[date_cols].apply(pd.to_datetime, errors="coerce")

    # Convert
    try:
        sparkDF = spark.createDataFrame(df)
        sparkDF = sparkDF.replace("", None)
        print("-- Conversion OK")

    except (TypeError, ValueError):
        print("-- -- Transform")
        df = pd.read_csv(io.StringIO(df.to_csv(index=False)))
        # Replace NaN
        df = df.replace({np.nan: None})
        df.loc[:, df.isnull().all()] = ""

        sparkDF = spark.createDataFrame(df)
        sparkDF = sparkDF.replace("", None)
        print("-- Conversion OK")

    except Exception as e:
        print("-- Exception")
        print("\t", e.__class__.__name__, "\n\t", e)

    return sparkDF


def save_parquet(sparkDF, fname):
    # Save original dataframe
    print(f'-- Saving in {dir_parquet.joinpath(f"{fname}.parquet")}')
    sparkDF.write.parquet(
        dir_parquet.joinpath(f"{fname}.parquet").as_posix(),
        mode="overwrite",
    )
    print("SAVE SUCCESS")


def load_parquet(fname):
    # Load dataframe
    print(f'-- Loading {dir_parquet.joinpath(f"{fname}.parquet")}')
    sparkDF = spark.read.parquet(dir_parquet.joinpath(f"{fname}.parquet").as_posix())
    return sparkDF


def cleanDOI(doi):
    if not isinstance(doi, str):
        doi = f"{doi}".lower()
    doi = re.sub(r"^https://doi.org/", "", doi.lower())
    doi = "".join(doi.split())
    return doi


cleanDOI_udf = F.udf(cleanDOI, StringType())


def process_publications(publications: List[Path], merge=False, ss_join=False):
    """
    Processes a list of Path, where each element is a file path with publications.\\
    (Optional) Concatenate all publications in one dataframe and join with SemanticScholar.\\
    Then, save it to parquet.

    If `merge`=`True` merge all dataframes into one
    
    If `ss_join`=`True` includes the IDs of Semantic Scholar publications in dataframe
    """

    pubs = []

    print("Processing...\n")
    for f in publications:
        for fname, df in extract_file_info(f):
            print(f"-- {fname}")

            if fname is None or df is None:
                continue

            # Unify format
            df.columns = df.columns.str.lower()
            if "horizon" in f.name.lower():
                df["frameworkProgramme"] = "HORIZON"
                df = df.rename(
                    columns={
                        "id": "id",
                        "title": "title",
                        "ispublishedas": "isPublishedAs",
                        "authors": "authors",
                        "journaltitle": "journalTitle",
                        "journalnumber": "journalNumber",
                        "publishedyear": "publishedYear",
                        "publishedpages": "publishedPages",
                        "issn": "issn",
                        "isbn": "isbn",
                        "doi": "doi",
                        "projectid": "projectID",
                        "projectacronym": "projectAcronym",
                        "collection": "collection",
                        "contentupdatedate": "contentUpdateDate",
                        "rcn": "rcn",
                    }
                )
            elif "h2020" in f.name.lower():
                df["frameworkProgramme"] = "H2020"
                df = df.rename(
                    columns={
                        "id": "id",
                        "title": "title",
                        "ispublishedas": "isPublishedAs",
                        "authors": "authors",
                        "journaltitle": "journalTitle",
                        "journalnumber": "journalNumber",
                        "publishedyear": "publishedYear",
                        "publishedpages": "publishedPages",
                        "issn": "issn",
                        "isbn": "isbn",
                        "doi": "doi",
                        "projectid": "projectID",
                        "projectacronym": "projectAcronym",
                        "collection": "collection",
                        "contentupdatedate": "contentUpdateDate",
                        "rcn": "rcn",
                    }
                )
            else:
                df["frameworkProgramme"] = "FP7"
                df = df.drop(columns="doi").rename(columns={"qa_processed_doi": "doi"})
                df = df.rename(
                    columns={
                        "project_id": "projectID",
                        "title": "title",
                        "author": "authors",
                        # "doi": "",
                        "publication_type": "isPublishedAs",
                        "repository_url": "repositoryUrl",
                        "journal_title": "journalTitle",
                        "publisher": "publisher",
                        "volume": "journalNumber",
                        "pages": "publishedPages",
                        "qa_processed_doi": "doi",
                        "record_id": "id",
                    }
                )
            if merge:
                pubs.append(df)
            else:
                df["doi"] = df["doi"].apply(cleanDOI)
                # Transform to spark
                sparkDF = convert_spark(df)

                # Join with SemanticScholar
                if ss_join:
                    joint_pub = (
                        sparkDF.withColumn(
                            "doi",
                            F.when(col("doi").isNotNull(), cleanDOI_udf(col("doi"))).otherwise(None),
                        )
                        .join(
                            ss.select(
                                col("id").alias("SSID"),
                                F.when(col("doi").isNotNull(), cleanDOI_udf(col("doi")))
                                .otherwise(None)
                                .alias("doi"),
                            ),
                            on="doi",
                            how="left",
                        )
                        .select(df.columns.tolist() + ["SSID"])
                    )
                else:
                    joint_pub = sparkDF

                save_parquet(joint_pub, fname)

        print("\n", "-" * 80, "\n")

    if merge:
        pub_df = pd.concat(pubs)

        # Transform to spark
        sparkDF = convert_spark(pub_df)

        # Join with SemanticScholar
        if ss_join:
            joint_pub = (
                sparkDF.withColumn(
                    "doi",
                    F.when(col("doi").isNotNull(), cleanDOI_udf(col("doi"))).otherwise(None),
                )
                .join(
                    ss.select(
                        col("id").alias("SSID"),
                        F.when(col("doi").isNotNull(), cleanDOI_udf(col("doi")))
                        .otherwise(None)
                        .alias("doi"),
                    ),
                    on="doi",
                    how="left",
                )
                .select(pub_df.columns.tolist() + ["SSID"])
            )
        else:
            joint_pub = sparkDF

        save_parquet(joint_pub, "publications")


def process_patents(patents: List[Path], merge=False, pt_join=False):
    """
    Processes a list of Path, where each element is a file path with patents.\\
    (Optional) Concatenate all patents in one dataframe and join with PATSTAT.\\
    Then, save it to parquet.

    If `merge`=`True` merge all dataframes into one
    
    If `pt_join`=`True` includes the IDs of PATSTAT in dataframe
    """

    pubs = []

    print("Processing...\n")
    for f in patents:
        for fname, df in extract_file_info(f):
            print(f"-- {fname}")

            if fname is None or df is None:
                continue

            if merge:
                if "horizon" in f.name.lower():
                    df["frameworkProgramme"] = "HORIZON"
                elif "h2020" in f.name.lower():
                    df["frameworkProgramme"] = "H2020"
                elif "fp7" in f.name.lower():
                    df["frameworkProgramme"] = "FP7"
                pubs.append(df)
            else:
                # Transform to spark
                sparkDF = convert_spark(df)

                # Join with PATSTAT
                if pt_join:
                    joint_pat = sparkDF.join(
                        pt.select(col("appln_nr").alias("applicationIdentifier"), "appln_id"),
                        on="applicationIdentifier",
                        how="left",
                    ).select(df.columns.tolist() + ["appln_id"])
                else:
                    joint_pat = sparkDF

                save_parquet(joint_pat, fname)

        print("\n", "-" * 80, "\n")

    if merge:
        pat_df = pd.concat(pubs)
        # Transform to spark
        sparkDF = convert_spark(pat_df)

        # Join with PATSTAT
        if pt_join:
            joint_pat = sparkDF.join(
                pt.select(col("appln_nr").alias("applicationIdentifier"), "appln_id"),
                on="applicationIdentifier",
                how="left",
            ).select(pat_df.columns.tolist() + ["appln_id"])
        else:
            joint_pat = sparkDF

        save_parquet(joint_pat, "patents")


def process_reports(reports: List[Path], merge=False):
    """
    Processes a list of Path, where each element is a file path with report summaries.\\
    (Optional) Concatenate all patents in one dataframe.\\
    Then, save it to parquet.


    If `merge`=`True` merge all dataframes into one
    """

    reps = []

    print("Processing...\n")
    for f in reports:
        for fname, df in extract_file_info(f):
            print(f"-- {fname}")

            if fname is None or df is None:
                continue

            if merge:
                if "horizon" in f.name.lower():
                    df["frameworkProgramme"] = "HORIZON"
                elif "h2020" in f.name.lower():
                    df["frameworkProgramme"] = "H2020"
                elif "fp7" in f.name.lower():
                    df["frameworkProgramme"] = "FP7"
                reps.append(df)
            else:
                # Transform to spark
                sparkDF = convert_spark(df)

                save_parquet(sparkDF, fname)

        print("\n", "-" * 80, "\n")

    if merge:
        reps_df = pd.concat(reps)
        # Transform to spark
        sparkDF = convert_spark(reps_df)

        save_parquet(sparkDF, "reports")


def process_projects(projects: List[Path]):
    """
    Processall files given a list of Paths
    Joins original project with topics, organizations, SciVoc, publications and patents
    """

    projs = []

    # Load SciVoc dictionary
    _, scivoccodes = next(extract_file_info(Path("data/SciVocCodes.xlsx")))
    title2code = scivoccodes[["title", "code"]].dropna()
    title2code["code"] = title2code["code"].astype(int)
    title2code = dict(title2code.values)

    print("Processing...\n")
    for f in projects:

        df_proj = None
        tops = None
        orgs = None
        svcs = None

        for fname, df in extract_file_info(f):
            print(f"-- {fname}")

            if fname is None or df is None:
                continue

            sfname = fname.split("-")[-1]

            # Drop:
            if sfname in ["legalBasis", "webItem", "webLink"]:
                continue

            # Save
            elif sfname == "topics":
                # Merge entire dataframe with projects, as in this case each row is has unique (proj_id, topic, topic_title)
                tops = (
                    df[["topic", "projectID", "title"]]
                    .groupby("projectID")[["topic", "title"]]
                    .apply(
                        lambda x: pd.Series(
                            {
                                "topic": x["topic"].values[0],
                                "topic_title": x["title"].values[0],
                            }
                        )
                    )
                )
            elif sfname == "organization":
                # Get information that is going to be added to projects
                orgs = df[
                    ["projectID", "organisationID", "country", "role", "ecContribution"]
                ]
                orgs.loc[:, "ecContribution"] = orgs.loc[:, "ecContribution"].apply(
                    pd.to_numeric, errors="coerce"
                )
                orgs.loc[pd.isna(orgs["ecContribution"]), "ecContribution"] = 0.0
                orgs = pd.DataFrame(
                    orgs.groupby(["projectID"]).apply(
                        lambda x: pd.Series(
                            {
                                "countryContr": " ".join(
                                    [
                                        f"{k}|{v}"
                                        for k, v in x.groupby("country")[
                                            "ecContribution"
                                        ]
                                        .apply(sum)
                                        .items()
                                    ]
                                ),
                                "orgContr": " ".join(
                                    [
                                        f"{i}|{c}"
                                        for i, c in zip(
                                            x["organisationID"].values,
                                            x["ecContribution"].values,
                                        )
                                    ]
                                ),
                                "coordinatorCountry": x.loc[
                                    x["role"] == "coordinator", "country"
                                ].values[0],
                                "coordinatorOrg": x.loc[
                                    x["role"] == "coordinator", "organisationID"
                                ].values[0],
                            }
                        )
                    )
                )

            elif sfname == "euroSciVoc":
                svcs = (
                    df[["euroSciVocTitle", "projectID"]]
                    .groupby("projectID")["euroSciVocTitle"]
                    .apply(lambda x: [title2code[i.strip()] for i in x.values])
                    .rename("euroSciVocCode")
                )
            elif sfname == "project":
                df_proj = df.copy()
            else:
                continue

        print("\n", "-" * 80, "\n")

        # Save enriched project
        additions = pd.concat([tops, orgs, svcs], axis=1).reset_index(drop=False)
        enrich_proj = (
            df_proj.drop(["legalBasis", "topics"], axis=1)
            .merge(additions, left_on="id", right_on="projectID", how="left")
            .drop("projectID", axis=1)
            .rename(columns={"id": "projectID"})
        )
        projs.append(enrich_proj)

    # Conver to spark
    projs_df = pd.concat(projs)
    sparkDF = convert_spark(projs_df)

    # Load publications
    pubs = (
        load_parquet("publications")
        .select("projectID", "id")
        .groupBy("projectID")
        .agg(F.collect_list("id").alias("publicationID"))
    )
    print("LOADED publications")

    # Load patents
    pats = (
        load_parquet("patents")
        .select("projectID", "appln_id")
        .groupBy("projectID")
        .agg(F.collect_list("appln_id").alias("patentID"))
    )
    print("LOADED patents")

    sparkProjects = sparkDF.join(pubs, on="projectID", how="left").join(
        pats, on="projectID", how="left"
    )

    save_parquet(sparkProjects, "projects")


# Statistics functions
def publications_statistics(ss_join=False):
    """
    Some publications statistics:
        - Percentage of projects with publications
        - Number of publications with DOI
        - Number of publications with reference in SemanticScholar
    """
    pubs = load_parquet("publications")
    if ss_join:
        df = pubs.select("frameworkProgramme", "doi", "SSID").toPandas()
    else:
        df = pubs.select("frameworkProgramme", "doi").toPandas()
                
    total = len(df)
    print(f"Number of total publications: {total}")

    # Publications with DOI
    pub_doi = df[["frameworkProgramme", "doi"]].dropna(subset=["doi"])
    num_pubs = pub_doi["doi"].count()
    print(f"Number of publications with DOI: {num_pubs} ({num_pubs/total*100:.2f}%)")
    for k, v in pub_doi.groupby("frameworkProgramme")["doi"].count().items():
        print(f"\t-- {k}: {v} ({v/total*100:.2f}%)")

    # Publications with ref in SS
    if ss_join:
        pub_SS = df[["doi", "SSID"]].dropna(subset=["SSID"])
        pub_withSS = len(pub_SS)
        print(f"Number of publications with SSID: {pub_withSS} ({pub_withSS/total*100:.2f}%)")
        print(f"Number of publications with DOI that don't have SS reference: {num_pubs-pub_withSS}")

def patents_statistics(pt_join=False):
    """
    Some patents statistics:
        - Number of patents with reference in PATSTAT
    """
    pats = load_parquet("patents")
    if pt_join:
        df = pats.select("frameworkProgramme", "appln_id").toPandas()
    else:
        df = pats.select("frameworkProgramme").toPandas()

    total = len(df)
    print(f"Number of total patents: {total}")

    for k, v in df.groupby("frameworkProgramme")["frameworkProgramme"].count().items():
        print(f"\t-- {k}: {v} ({v/total*100:.2f}%)")

    # Patents in PATSTAT
    if pt_join:
        pat_PATS = df[["frameworkProgramme", "appln_id"]].dropna(subset=["appln_id"])
        num_pats = pat_PATS["appln_id"].count()
        print(f"Number of patents in PATSTAT: {num_pats} ({num_pats/total*100:.2f}%)")
        for k, v in pat_PATS.groupby("frameworkProgramme")["appln_id"].count().items():
            print(f"\t-- {k}: {v} ({v/total*100:.2f}%)")
            

def projects_statistics():
    """
    Some projects statistics:
        - Percentage of projects with publications
        - Percentage of projects with patents
    """
    projs = load_parquet("projects")
    df = projs.toPandas()

    total = len(df)
    print(f"Number of total publications: {total}")

    # Projects with publications
    proj_pubs = df[["frameworkProgramme", "publicationID"]].dropna(
        subset=["publicationID"]
    )
    num_pubs = proj_pubs["publicationID"].count()
    print(
        f"Number of projects with publications: {num_pubs} ({num_pubs/total*100:.2f}%)"
    )
    for k, v in (
        proj_pubs.groupby("frameworkProgramme")["publicationID"].count().items()
    ):
        print(f"\t-- {k}: {v} ({v/total*100:.2f}%)")

    # Projects with patents
    proj_pats = df[["frameworkProgramme", "patentID"]].dropna(subset=["patentID"])
    num_pats = proj_pats["patentID"].count()
    print(f"Number of projects with patents: {num_pats} ({num_pats/total*100:.2f}%)")
    for k, v in proj_pats.groupby("frameworkProgramme")["patentID"].count().items():
        print(f"\t-- {k}: {v} ({v/total*100:.2f}%)")


# Get all available titles from SciVoc
def process_keys(obj):
    """
    Process json object to obtain all titles
    """
    structure = []

    def get_keys(obj):
        keys = []
        if isinstance(obj, list):
            for el in obj:
                keys.append(get_keys(el))
        elif isinstance(obj, dict):
            if obj.get("subtitles"):
                for el in obj["subtitles"]:
                    keys.extend([f"{obj['title']}/{s.strip()}" for s in get_keys(el)])
            keys.append(obj["title"])
        return keys

    # Convert obj to list
    if not isinstance(obj, list):
        obj = [obj]
    for el in obj:
        structure.extend(get_keys(el))
    return structure


if __name__ == "__main__":
    spark = SparkSession.builder.appName("test").getOrCreate()
    sc = spark.sparkContext
    spark.conf.set("spark.sql.legacy.parquet.int96RebaseModeInWrite", "CORRECTED")
    print(sc.version)
    
    # Define directories
    cf = ConfigParser()
    cf.read("config.cf")

    # Data sources
    dir_raw = Path(cf.get("cordis", "dir_raw"))
    dir_raw_h2020 = dir_raw.joinpath("H2020")
    dir_raw_fp7 = dir_raw.joinpath("FP7")
    dir_raw_ref = dir_raw.joinpath("cordis-ref")
    # Auxiliary datasets
    dir_ss = Path(cf.get("aux", "dir_ss"))
    dir_patstat = Path(cf.get("aux", "dir_patstat"))
    # Target directory
    dir_parquet = Path(cf.get("cordis", "dir_parquet"))

    # Configuration hdfs
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(
        spark._jsc.hadoopConfiguration()
    )
    hdfs_dir_parquet = spark._jvm.org.apache.hadoop.fs.Path(dir_parquet.as_posix())
    # hdfs_dir_raw = spark._jvm.org.apache.hadoop.fs.Path(dir_raw.as_posix())

    # Create output directories if they do not exist
    if not fs.exists(hdfs_dir_parquet):
        fs.mkdirs(hdfs_dir_parquet)

    ## Read SemanticScholar
    #
    # Load SemanticScholar information. It will be joint with Publications
    ss = spark.read.parquet(dir_ss.joinpath("papers.parquet").as_posix())

    ## Read PATSTAT
    #
    # Load PATSTAT information. It will be joint with Patents
    pt = spark.read.parquet(dir_patstat.joinpath("patstat_appln.parquet").as_posix())

    ## File list

    # Files in LOCAL:
    # Read fp7 files
    fp7_file_list = [el for el in dir_raw_fp7.iterdir()]

    # Read h2020 files
    h2020_file_list = [el for el in dir_raw_h2020.iterdir()]

    file_list = [
        el
        for el in (fp7_file_list + h2020_file_list)
        if (
            el.name.endswith("xlsx.zip")
            or el.name.endswith("xlsx.7z")
            or el.name.endswith(".xls")
            or el.name.endswith(".xlsx")
        )
    ]

    publications = [x for x in file_list if "publications" in x.name.lower()]
    reports = [x for x in file_list if "reports" in x.name.lower()]
    projects = [x for x in file_list if "projects" in x.name.lower()]
    irps = [x for x in file_list if "irps" in x.name.lower()]

    ### Process EuroSciVoc Codes
    #
    # This part has been processed manually (at least partially) to get all the possible paths and codes,
    # as no official reference has been found that includes all of them.
    #
    # **NOTE:**
    # Some additional files not included in GitHub are required
    with open("SciVoc-data/transform.json", "r") as f:
        taxonomies = json.load(f)

    all_keys = process_keys(taxonomies)
    all_keys = [f"/{k}" for k in all_keys]
    # Save
    with open("SciVoc-data/ScienceVocabulary.txt", "w") as f:
        [f.write(f"{el}\n") for el in all_keys]

    # Load all EuroSciVoc
    dfs = []
    for f in projects:
        print(f)
        with py7zr.SevenZipFile(f, "r") as archive:
            dfs.append(
                pd.read_excel(
                    archive.read("xlsx/euroSciVoc.xlsx")["xlsx/euroSciVoc.xlsx"],
                    engine="openpyxl",
                )
            )
    # Concatenate both
    df = pd.concat(dfs)

    # Split codes to get only the code values
    df["euroSciVocCode"] = df["euroSciVocCode"].apply(
        lambda x: [el.strip() for el in x.split("/") if len(el) > 0]
    )
    df["euroSciVocPath"] = df["euroSciVocPath"].apply(
        lambda x: [el.strip() for el in x.split("/") if len(el) > 0]
    )
    df["euroSciVocTitle"] = df["euroSciVocTitle"].apply(str.strip)
    # Get length on the resulting lists
    df["length"] = df["euroSciVocCode"].apply(len)

    # Now we only want unique titles with longest codes (as this will be the entire path)
    euroSciVoc = (
        df[["euroSciVocCode", "euroSciVocPath", "euroSciVocTitle", "length"]]
        .sort_values(by="length")
        .drop_duplicates(subset="euroSciVocTitle", keep="last")
    )

    # Also, as some elements are only found in the full path but don't have the code-title
    #  directly assigned we can obtain it from that path.
    aux = dict(
        df.loc[
            df.apply(
                lambda x: len(x["euroSciVocCode"]) == len(x["euroSciVocPath"]), axis=1
            )
        ]
        .apply(lambda x: list(zip(x["euroSciVocPath"], x["euroSciVocCode"])), axis=1)
        .explode()
        .drop_duplicates()
        .tolist()
    )

    # Finally we get the title - code relationship
    title2code = dict(
        euroSciVoc[["euroSciVocCode", "euroSciVocTitle"]]
        .apply(lambda x: (x["euroSciVocTitle"], x["euroSciVocCode"][-1]), axis=1)
        .tolist()
    )
    title2code.update(aux)

    # Save all SciVoc information
    rows = []
    for k in all_keys:
        this_row = []
        spl_path = k.split("/")
        # Full path
        this_row.append(k)
        # Title
        title = spl_path[-1]
        this_row.append(title)
        # Code
        code = title2code.get(title, None)
        this_row.append(code)
        # Full code
        full_code = "/".join([title2code.get(t, "") for t in spl_path])
        this_row.append(full_code)
        rows.append((this_row))
    scivoccodes = pd.DataFrame(
        rows, columns=["full_path", "title", "code", "full_code"]
    )
    scivoccodes.to_excel("SciVoc-data/SciVocCodes.xlsx", index=None)

    ### Organisations
    # Load all organizations
    dfs = []
    for f in projects:
    print(f)
    # Get type of file
    extension = get_file_extension(f)
    print(f"-- {extension}")

    if extension == "Zip":
        archive = zipfile.ZipFile(f.as_posix(), "r")
        dfs.append(
            pd.read_excel(
                archive.read("xlsx/organization.xlsx"),
                engine="openpyxl",
            )
        )
    elif extension == "7-zip":
        with py7zr.SevenZipFile(f, "r") as archive:
            dfs.append(
                pd.read_excel(
                    archive.read("xlsx/organization.xlsx")["xlsx/organization.xlsx"],
                    engine="openpyxl",
                )
            )    # Concatenate both
    df = pd.concat(dfs)
    orgs_info = (
        df[
            [
                "organisationID",
                "vatNumber",
                "name",
                "shortName",
                "SME",
                "activityType",
                "street",
                "postCode",
                "city",
                "country",
                "nutsCode",
                "geolocation",
                "organizationURL",
                "contentUpdateDate",
            ]
        ]
        .sort_values(by=["organisationID", "contentUpdateDate"])
        .drop_duplicates(subset="organisationID", keep="last")
        .join(
            df.groupby("organisationID")["projectID"].apply(list),
            on="organisationID",
        )
    )
    sparkDF = convert_spark(orgs_info)
    save_parquet(sparkDF, "organizations")

    # Process rest of files

    ### Publications
    process_publications(publications, merge=True, ss_join=False)
    publications_statistics(ss_join=False)

    ### Patents
    process_patents(irps, merge=True, pt_join=False)
    patents_statistics(pt_join=False)

    ### Summaries
    process_reports(reports, merge=True)

    ### Projects
    process_projects(projects)
    projects_statistics()

    sc.stop()
