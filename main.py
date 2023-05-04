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
from workflows.common import *
import workflows.sql.create_cameo_tables as create_cameo_tables
from workflows.data_lake_flows import subflow_extract_load_cameo_tables, subflow_to_load_csv_to_datalake, extract_events, extract_mentions, transform_events, transform_mentions, create_bucket
from workflows.datawarehouse_flows import subflow_datawarehouse
from workflows.gdelt_data_type import dtypes_events, dtypes_mentions, dtypes_gkg
from workflows.dbt_flow import trigger_dbt_flow

@task(log_prints=True, tags=["load"], retries=3)
def retrive_file_urls_from_csv(list_file_url) -> pd.DataFrame:
    df = pd.read_csv(
        list_file_url,
        delimiter=" ",
        dtype={"FileUrl": "string"},
        names=["Size", "Id", "FileUrl"],
    )
    df["DateTimeTemporary"] = df["FileUrl"].str.extract(r"(\d{14})")
    df["DateTime"] = pd.to_datetime(df["DateTimeTemporary"], format="%Y%m%d%H%M%S")
    df["Date"] = df["DateTime"].dt.date
    df["Size"] = pd.to_numeric(df["Size"], errors="coerce").fillna(0)
    df = df.drop("DateTimeTemporary", axis=1)
    print(df.head())
    print(df.info())
    return df

def log_master_list_info(master_list_export, master_list_mentions, master_list_gkg, logger):
    export_size_mb = master_list_export["Size"].sum() / (1024 * 1024)
    mentions_size_mb = master_list_mentions["Size"].sum() / (1024 * 1024)
    gkg_size_mb = master_list_gkg["Size"].sum() / (1024 * 1024)
    
    logger.info(f"Total size of export data in MB: {export_size_mb}")
    logger.info(f"Total size of mentions data in MB: {mentions_size_mb}")
    logger.info(f"Total size of GKG data in MB: {gkg_size_mb}")
    
    print(
        f"Export Number of Rows {str(master_list_export.shape[0])}, Size of all data in rows {str(export_size_mb)}"
    )
    print(
        f"Mentions - Number of Rows {str(master_list_mentions.shape[0])}, Size of all data in rows {str(mentions_size_mb)}"
    )
    print(
        f"GKG - Number of Rows {str(master_list_gkg.shape[0])}, Size of all data in rows {str(gkg_size_mb)}"
    )

@flow(name="GDELT ELT Main Pipeline")
def main_flow(master_csv_list_url, min_date:str, clean_start=False, max_datetime=None):
    min_datetime = datetime.strptime(min_date,"%d/%m/%Y")
    master_list = retrive_file_urls_from_csv(master_csv_list_url)
    master_list = master_list[master_list["DateTime"].dt.date >= min_datetime.date()]
    if(max_datetime is not None):
        master_list = master_list[master_list["DateTime"].dt.date < max_datetime.date()]
    
    master_list_events = master_list[master_list["FileUrl"].str.contains("export")]
    master_list_mentions = master_list[master_list["FileUrl"].str.contains("mentions")]
    master_list_gkg = master_list[master_list["FileUrl"].str.contains("gkg")]
    
    logger = get_run_logger()
    log_master_list_info(master_list_events, master_list_mentions, master_list_gkg, logger)
    create_bucket()
    
    subflow_extract_load_cameo_tables()
    subflow_to_load_csv_to_datalake(master_list_events, extract_events, transform_events, events_table_name)
    subflow_to_load_csv_to_datalake(master_list_mentions, extract_mentions, transform_mentions, mentions_table_name)
    subflow_datawarehouse(clean_start)
    trigger_dbt_flow()


if __name__ == "__main__":
    master_csv_list_url = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"
    last_15mins_csv_list_url = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

    # Change this value based upon your bandwidth and time. 
    # Prefer first run of year 2023 which should take around 15mins to 30mins based upon you bandwidth
    min_date = "1/05/2023"

    main_flow(
        master_csv_list_url=master_csv_list_url,
        min_date=min_date,
        clean_start = True
    )