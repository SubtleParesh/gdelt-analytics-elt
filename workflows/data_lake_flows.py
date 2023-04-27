from anyio import create_event
import pandas as pd
import datetime
from pathlib import Path
from datetime import timedelta, datetime
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from prefect.blocks.system import Secret
import clickhouse_connect
from pprint import pprint
import concurrent.futures
from gdelt_data_type import dtypes_events, dtypes_mentions, dtypes_gkg
import warnings
import sql.create_cameo_tables as create_cameo_tables
from enum import Enum
from minio import Minio
from io import BytesIO
from common import *


is_bucket_exists=False

def get_minio_client():
    client = Minio(
        f"{ip_address}:39191",
        access_key="admin",
        secret_key="admin_password",
        secure=False
    )
    global is_bucket_exists


    # Make 'gdelt' bucket if not exist.
    if is_bucket_exists:
        found = client.bucket_exists("gdelt")
        if not found and is_bucket_exists:
            client.make_bucket("gdelt")
            is_bucket_exists=True
        else:
            is_bucket_exists=True
            print("Bucket 'gdelt' already exists")
    return client


def transform_events(df):
    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d")
    df["DATEADDED"] = pd.to_datetime(df["DATEADDED"], format="%Y%m%d%H%M%S")

def transform_mentions(df):
    df["EventTimeDate"] = pd.to_datetime(df["EventTimeDate"], format="%Y%m%d%H%M%S")
    df["MentionTimeDate"] = pd.to_datetime(df["MentionTimeDate"], format="%Y%m%d%H%M%S")

def extract_events(url):
    try:
        df = pd.read_csv(url, sep="\t", names=list(dtypes_events.keys()),error_bad_lines=False, dtype = dtypes_events)
        return df
    except Exception as e:
        print(f"Error on read_csv {url} error {str(e)}")
        return None

def extract_mentions(url):
    try:
        df = pd.read_csv(url, sep="\t", names=list(dtypes_mentions.keys()),error_bad_lines=False, dtype = dtypes_mentions)
        return df
    except Exception as e:
        print(f"Error on read_csv {url} error {str(e)}")
        return None


def extract_csv_batch(grouped_csv_list, executor, csv_extractor_function):
    futures = []
    for idx, url_row in grouped_csv_list.iterrows():
        future = executor.submit(csv_extractor_function, url_row["FileUrl"])
        futures.append(future)

    # Use as_completed() method of futures to get results as they complete
    list_df_for_day = []
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result is not None:
            list_df_for_day.append(result)
    df_all_csv_for_day = list_df_for_day[0]
    for i in list_df_for_day[1:]:
        df_all_csv_for_day.append(i)

    return df_all_csv_for_day


@flow(name="Subflow - Extract And Load CSV Raw Files")
def subflow_to_load_csv_to_datalake(csv_full_list, csv_extractor_function, transform_function, table_name):
    print(f"Extracting and Loading all CSV files For {table_name}")
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=40)
    csv_list_grouped_by_date = csv_full_list.groupby(by="Date")

    for date,grouped_csv_list in csv_list_grouped_by_date:
        print(f"Downloading CSV's for Date-{date} No of Rows {len(grouped_csv_list)} For {table_name}")
        extracted_df = extract_csv_batch(grouped_csv_list, executor, csv_extractor_function)
        transform_function(extracted_df)
        load_to_minio(df=extracted_df, path=table_name, filename=date)


@task(
    log_prints=True, tags=["load", "clickhouse"], retries=1
)
def load_to_minio(df: pd.DataFrame, path: str, filename: str):
    minio_client = get_minio_client()
    df_parquet_data_buffer = BytesIO()
    df.to_parquet(df_parquet_data_buffer, compression="gzip")
    df_parquet_data_buffer.seek(0)
    path = path.replace("gdelt_", "")
    path = path.replace("_", "/")
    minio_client.put_object(
        "gdelt", f"{path}/{filename}.parquet", df_parquet_data_buffer , length=len(df_parquet_data_buffer.getvalue())
    )



def extract_load_cameo_type():
    print(f"Extracting and Loading Data for {cameo_type}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.type.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df=df, path=cameo_type, filename="data")


def extract_load_cameo_religion():
    print(f"Extracting and Loading Data for {cameo_religion}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.religion.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_religion, filename="data")


def extract_load_cameo_knowngroup():
    print(f"Extracting and Loading Data for {cameo_knowngroup}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.knowngroup.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_knowngroup, filename="data")


def extract_load_cameo_goldsteinscale():
    print(f"Extracting and Loading Data for {cameo_goldsteinscale}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.goldsteinscale.txt"
    cameo_dtype = {"CameoEventCode": "string", "GoldsteinScale": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_goldsteinscale, filename="data")


def extract_load_cameo_eventcodes():
    print(f"Extracting and Loading Data for {cameo_eventcodes}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.eventcodes.txt"
    cameo_dtype = {"CameoEventCode": "string", "EventDescription": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_eventcodes, filename="data")


def extract_load_cameo_ethnic():
    print(f"Extracting and Loading Data for {cameo_ethnic}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.ethnic.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_ethnic, filename="data")


def extract_load_cameo_country():
    print(f"Extracting and Loading Data for {cameo_country}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.country.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_country, filename="data")


def extract_load_cameo_fipscountry():
    print(f"Extracting and Loading Data for {cameo_fipscountry}")
    url = "https://www.gdeltproject.org/data/lookups/FIPS.country.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=0, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_fipscountry, filename="data")


@flow(name="Subflow - Extract And Load Cameo Tables")
def subflow_extract_load_cameo_tables():
    extract_load_cameo_type()
    extract_load_cameo_religion()
    extract_load_cameo_knowngroup()
    extract_load_cameo_goldsteinscale()
    extract_load_cameo_eventcodes()
    extract_load_cameo_ethnic()
    extract_load_cameo_country()
    extract_load_cameo_fipscountry()
