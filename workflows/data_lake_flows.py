from io import BytesIO

import dask.dataframe as dd
import pandas as pd
from minio import Minio
from prefect import flow, task
from prefect_dask.task_runners import DaskTaskRunner

import workflows.common as common
from workflows.common import Configuration, Table
from workflows.gdelt_data_type import dtypes_events, dtypes_mentions

table = Table()


def create_bucket(config: Configuration):
    print("Create Bucket")
    client = Minio(
        f"{config.minio.ip_address}:{config.minio.port}",
        access_key=config.minio.username,
        secret_key=config.minio.password,
        secure=False,
    )
    found = client.bucket_exists("gdelt")
    if not found:
        client.make_bucket("gdelt")
    else:
        print("Bucket 'gdelt' already exists")


def get_minio_client(config: Configuration):
    print(f"{config.ip_address}:{config.minio.port}")
    client = Minio(
        f"{config.ip_address}:{config.minio.port}",
        access_key=config.minio.username,
        secret_key=config.minio.password,
        secure=False,
    )
    return client


def transform_events(df):
    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d")
    df["DATEADDED"] = pd.to_datetime(df["DATEADDED"], format="%Y%m%d%H%M%S")


def transform_mentions(df):
    df["EventTimeDate"] = pd.to_datetime(df["EventTimeDate"], format="%Y%m%d%H%M%S")
    df["MentionTimeDate"] = pd.to_datetime(df["MentionTimeDate"], format="%Y%m%d%H%M%S")


def extract_events(urls):
    try:
        df = dd.read_csv(
            urls, sep="\t", names=list(dtypes_events.keys()), dtype=dtypes_events
        )
        return df.compute()
    except Exception as e:
        print(f"Error on read_csv error {str(e)}")
        return None


def extract_mentions(urls):
    try:
        df = dd.read_csv(
            urls, sep="\t", names=list(dtypes_mentions.keys()), dtype=dtypes_mentions
        )
        return df.compute()
    except Exception as e:
        print(f"Error on read_csv  error {str(e)}")
        return None


def extract_csv_batch(grouped_csv_list, csv_extractor_function):
    urls = []
    for idx, url_row in grouped_csv_list.iterrows():
        urls.append(url_row["FileUrl"])

    return csv_extractor_function(urls)


@task(retries=2, retry_delay_seconds=1)
def load_csvs_by_data_to_minio(
    config: Configuration,
    date,
    grouped_csv_list,
    table_name,
    csv_extractor_function,
    transform_function,
):
    extracted_df = extract_csv_batch(grouped_csv_list, csv_extractor_function)
    if extracted_df is not None:
        transform_function(extracted_df)
        load_to_minio(config, df=extracted_df, path=table_name, filename=date)


def load_to_minio(config: Configuration, df: pd.DataFrame, path: str, filename: str):
    minio_client = get_minio_client(config)
    df_parquet_data_buffer = BytesIO()
    df.to_parquet(df_parquet_data_buffer)
    df_parquet_data_buffer.seek(0)
    path = path.replace("gdelt_", "")
    path = path.replace("_", "/")
    minio_client.put_object(
        "gdelt",
        f"{path}/{filename}.parquet",
        df_parquet_data_buffer,
        length=len(df_parquet_data_buffer.getvalue()),
    )


def get_bucket_file_path(path: str, filename: str):
    path = path.replace("gdelt_", "")
    path = path.replace("_", "/")
    return f"gdelt/{path}/{filename}.parquet"


@task(retries=2)
def extract_load_cameo_type(config: Configuration):
    print(f"Extracting and Loading Data for {table.cameo_type}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.type.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(
        url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()), dtype=cameo_dtype
    )
    load_to_minio(config, df=df, path=table.cameo_type, filename="data")


@task(retries=2)
def extract_load_cameo_religion(config: Configuration):
    print(f"Extracting and Loading Data for {table.cameo_religion}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.religion.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(
        url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()), dtype=cameo_dtype
    )
    load_to_minio(config, df, path=table.cameo_religion, filename="data")


@task(retries=2)
def extract_load_cameo_knowngroup(config: Configuration):
    print(f"Extracting and Loading Data for {table.cameo_knowngroup}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.knowngroup.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(
        url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()), dtype=cameo_dtype
    )
    load_to_minio(config, df, path=table.cameo_knowngroup, filename="data")


@task(retries=2)
def extract_load_cameo_goldsteinscale(config: Configuration):
    print(f"Extracting and Loading Data for {table.cameo_goldsteinscale}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.goldsteinscale.txt"
    cameo_dtype = {"CameoEventCode": "string", "GoldsteinScale": "string"}
    df = pd.read_csv(
        url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()), dtype=cameo_dtype
    )
    load_to_minio(config, df, path=table.cameo_goldsteinscale, filename="data")


@task(retries=2)
def extract_load_cameo_eventcodes(config: Configuration):
    print(f"Extracting and Loading Data for {table.cameo_eventcodes}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.eventcodes.txt"
    cameo_dtype = {"CameoEventCode": "string", "EventDescription": "string"}
    df = pd.read_csv(
        url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()), dtype=cameo_dtype
    )
    load_to_minio(config, df, path=table.cameo_eventcodes, filename="data")


@task(retries=2)
def extract_load_cameo_ethnic(config: Configuration):
    print(f"Extracting and Loading Data for {table.cameo_ethnic}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.ethnic.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(
        url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()), dtype=cameo_dtype
    )
    load_to_minio(config, df, path=table.cameo_ethnic, filename="data")


@task(retries=2)
def extract_load_cameo_country(config: Configuration):
    print(f"Extracting and Loading Data for {table.cameo_country}")
    url = "https://www.gdeltproject.org/data/lookups/CAMEO.country.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(
        url, sep="\t", skiprows=1, names=list(cameo_dtype.keys()), dtype=cameo_dtype
    )
    load_to_minio(config, df, path=table.cameo_country, filename="data")


@task(retries=2)
def extract_load_cameo_fipscountry(config: Configuration):
    print(f"Extracting and Loading Data for {table.cameo_fipscountry}")
    url = "https://www.gdeltproject.org/data/lookups/FIPS.country.txt"
    cameo_dtype = {"Code": "string", "Label": "string"}
    df = pd.read_csv(
        url, sep="\t", skiprows=0, names=list(cameo_dtype.keys()), dtype=cameo_dtype
    )
    load_to_minio(config, df, path=table.cameo_fipscountry, filename="data")


@flow(
    name="Subflow - Extract And Load Cameo Tables",
    task_runner=DaskTaskRunner(cluster_kwargs=common.config.dask),
)
def subflow_extract_load_cameo_tables(config):
    extract_load_cameo_type(config)
    extract_load_cameo_religion(config)
    extract_load_cameo_knowngroup(config)
    extract_load_cameo_goldsteinscale(config)
    extract_load_cameo_eventcodes(config)
    extract_load_cameo_ethnic(config)
    extract_load_cameo_country(config)
    extract_load_cameo_fipscountry(config)


@flow(
    name="GDELT ELT - Extract and Load Data Lake Sub Workflow",
    task_runner=DaskTaskRunner(cluster_kwargs=common.config.dask),
)
def subflow_to_load_csv_to_datalake(
    config, csv_full_list, csv_extractor_function, transform_function, table_name
):
    print(f"Extracting and Loading all CSV files For {table_name}")
    csv_list_grouped_by_date = csv_full_list.groupby(by="Date")
    for date, grouped_csv_list in csv_list_grouped_by_date:
        load_csvs_by_data_to_minio.submit(
            config,
            date,
            grouped_csv_list,
            table_name,
            csv_extractor_function,
            transform_function,
        )
