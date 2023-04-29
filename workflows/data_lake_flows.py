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
from prefect_dask.task_runners import DaskTaskRunner
from prefect.task_runners import ConcurrentTaskRunner
import dask.dataframe as dd
from prefect_ray import RayTaskRunner



def create_bucket():
    client = Minio(
        f"{ip_address}:39191",
        access_key="admin",
        secret_key="admin_password",
        secure=False
    )
    found = client.bucket_exists("gdelt")
    if not found:
        client.make_bucket("gdelt")
    else:
        print("Bucket 'gdelt' already exists")

def get_minio_client():
    client = Minio(
        f"{ip_address}:39191",
        access_key="admin",
        secret_key="admin_password",
        secure=False
    )
    return client


def transform_events(df):
    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d")
    df["DATEADDED"] = pd.to_datetime(df["DATEADDED"], format="%Y%m%d%H%M%S")

def transform_mentions(df):
    df["EventTimeDate"] = pd.to_datetime(df["EventTimeDate"], format="%Y%m%d%H%M%S")
    df["MentionTimeDate"] = pd.to_datetime(df["MentionTimeDate"], format="%Y%m%d%H%M%S")

# def extract_events(url):
#     try:
#         df = pd.read_csv(url, sep="\t", names=list(dtypes_events.keys()),error_bad_lines=False, dtype = dtypes_events)
#         return df
#     except Exception as e:
#         print(f"Error on read_csv {url} error {str(e)}")
#         return None

# def extract_mentions(url):
#     try:
#         df = pd.read_csv(url, sep="\t", names=list(dtypes_mentions.keys()),error_bad_lines=False, dtype = dtypes_mentions)
#         return df
#     except Exception as e:
#         print(f"Error on read_csv {url} error {str(e)}")
#         return None

'An error occurred while calling the read_csv method registered to the pandas backend.\nOriginal Message: HTTPFileSystem requires "requests" and "aiohttp" to be installed'


def extract_events(urls):
    try:
        df = dd.read_csv(urls, sep="\t", names=list(dtypes_events.keys()),error_bad_lines=False, dtype = dtypes_events)
        return df.compute()
    except Exception as e:
        print(f"Error on read_csv error {str(e)}")
        return None

def extract_mentions(urls):
    try:
        df = dd.read_csv(urls, sep="\t", names=list(dtypes_mentions.keys()),error_bad_lines=False, dtype = dtypes_mentions)
        return df.compute()
    except Exception as e:
        print(f"Error on read_csv  error {str(e)}")
        return None

# def extract_csv_batch(grouped_csv_list, executor, csv_extractor_function):
#     futures = []
#     for idx, url_row in grouped_csv_list.iterrows():
#         future = executor.submit(csv_extractor_function, url_row["FileUrl"])
#         futures.append(future)

#     # Use as_completed() method of futures to get results as they complete
#     list_df_for_day = []
#     for future in concurrent.futures.as_completed(futures):
#         result = future.result()
#         if result is not None:
#             list_df_for_day.append(result)
#     df_all_csv_for_day = list_df_for_day[0]
#     for i in list_df_for_day[1:]:
#         df_all_csv_for_day.append(i)

#     return df_all_csv_for_day

def extract_csv_batch(grouped_csv_list, csv_extractor_function):
    urls = []
    for idx, url_row in grouped_csv_list.iterrows():
        urls.append(url_row["FileUrl"])
    
    return csv_extractor_function(urls)


# @flow(name="Subflow - Extract And Load CSV Raw Files")
# def subflow_to_load_csv_to_datalake(csv_full_list, csv_extractor_function, transform_function, table_name):
#     print(f"Extracting and Loading all CSV files For {table_name}")
#     executor = concurrent.futures.ThreadPoolExecutor(max_workers=40)
#     csv_list_grouped_by_date = csv_full_list.groupby(by="Date")

#     for date,grouped_csv_list in csv_list_grouped_by_date:
#         print(f"Downloading CSV's for Date-{date} No of Rows {len(grouped_csv_list)} For {table_name}")
#         extracted_df = extract_csv_batch(grouped_csv_list, executor, csv_extractor_function)
#         transform_function(extracted_df)
#         load_to_minio(df=extracted_df, path=table_name, filename=date)


@task(retries=2, retry_delay_seconds=1)
def load_csvs_by_data_to_minio(date, grouped_csv_list, table_name, csv_extractor_function, transform_function):
    # print(f"Downloading CSV's for Date-{date} No of Rows {len(grouped_csv_list)} For {table_name}")
    extracted_df = extract_csv_batch(grouped_csv_list, csv_extractor_function)
    if extracted_df is not None:
        transform_function(extracted_df)
        # ddf = dd.from_pandas(extracted_df, chunksize=1024*1024*1024)
        #ddf.to_parquet(f's3://{get_bucket_file_path(path=table_name, filename=date)}', compression='gzip', ignore_divisions=True)
        #                 #  , storage_options={'use_ssl': False})
        load_to_minio(df=extracted_df, path=table_name, filename=date)



# @task(
#     log_prints=True, tags=["load", "clickhouse"], retries=1
# )
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


def get_bucket_file_path(path:str, filename: str):
    path = path.replace("gdelt_", "")
    path = path.replace("_", "/")
    return f'gdelt/{path}/{filename}.parquet'

@task
def extract_load_cameo_type():
    print(f"Extracting and Loading Data for {cameo_type}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.type.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df=df, path=cameo_type, filename="data")

@task
def extract_load_cameo_religion():
    print(f"Extracting and Loading Data for {cameo_religion}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.religion.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_religion, filename="data")

@task
def extract_load_cameo_knowngroup():
    print(f"Extracting and Loading Data for {cameo_knowngroup}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.knowngroup.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_knowngroup, filename="data")

@task
def extract_load_cameo_goldsteinscale():
    print(f"Extracting and Loading Data for {cameo_goldsteinscale}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.goldsteinscale.txt"
    cameo_dtype = {"CameoEventCode": "string", "GoldsteinScale": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_goldsteinscale, filename="data")

@task
def extract_load_cameo_eventcodes():
    print(f"Extracting and Loading Data for {cameo_eventcodes}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.eventcodes.txt"
    cameo_dtype = {"CameoEventCode": "string", "EventDescription": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_eventcodes, filename="data")

@task
def extract_load_cameo_ethnic():
    print(f"Extracting and Loading Data for {cameo_ethnic}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.ethnic.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_ethnic, filename="data")

@task
def extract_load_cameo_country():
    print(f"Extracting and Loading Data for {cameo_country}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.country.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_country, filename="data")

@task
def extract_load_cameo_fipscountry():
    print(f"Extracting and Loading Data for {cameo_fipscountry}")
    url = "https://www.gdeltproject.org/data/lookups/FIPS.country.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(url, sep="\t", skiprows=0, names=list(cameo_dtype.keys()),error_bad_lines=False, dtype=cameo_dtype)
    load_to_minio(df, path=cameo_fipscountry, filename="data")


@flow(name="Subflow - Extract And Load Cameo Tables", task_runner=DaskTaskRunner(cluster_kwargs={"n_workers": 3, "threads_per_worker": 2, "memory_limit": "1GiB", "processes": True}))
def subflow_extract_load_cameo_tables():
    extract_load_cameo_type.submit()
    extract_load_cameo_religion.submit()
    extract_load_cameo_knowngroup.submit()
    extract_load_cameo_goldsteinscale.submit()
    extract_load_cameo_eventcodes.submit()
    extract_load_cameo_ethnic.submit()
    extract_load_cameo_country.submit()
    extract_load_cameo_fipscountry.submit()

# 4gb Memory Usage - workers-6 - th-2 
@flow(name="Subflow - Extract And Load CSV Raw Files", task_runner=DaskTaskRunner(cluster_kwargs={"n_workers": 10, "threads_per_worker": 2, "memory_limit": "1.3GiB", "processes": True}))
def subflow_to_load_csv_to_datalake(csv_full_list, csv_extractor_function, transform_function, table_name):
    print(f"Extracting and Loading all CSV files For {table_name}")
    csv_list_grouped_by_date = csv_full_list.groupby(by="Date")

    for date,grouped_csv_list in csv_list_grouped_by_date:
        load_csvs_by_data_to_minio.submit(date, grouped_csv_list, table_name, csv_extractor_function, transform_function)
