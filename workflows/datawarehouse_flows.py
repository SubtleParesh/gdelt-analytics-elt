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
import sql.create_cameo_dictionary as create_cameo_dictionary
import sql.create_cameo_tables as create_cameo_tables
from enum import Enum
from minio import Minio
from io import BytesIO
from common import *

def get_clickhouse_client():
    username = "clickhouse"
    password = "clickhouse"
    hostname = "localhost"
    port = "38123"
    database = "gdelt"

    temp_client = clickhouse_connect.get_client(
        host=hostname, port=port, username=username, password=password
    )
    temp_client.command(f'CREATE DATABASE IF NOT EXISTS {database}')

    client = clickhouse_connect.get_client(
        host=hostname, port=port, username=username, password=password , database = database
    )
    return client

clickhouse_client = get_clickhouse_client()

def insert_data_cameo_tables_from_s3(table_name: str, cameo_name:str):
    insert_script = f"""INSERT INTO gdelt.{table_name} SELECT * FROM s3('http://10.49.0.2:39191/gdelt/cameo/{cameo_name}/data.parquet','admin','admin_password')"""
    print(insert_script)
    clickhouse_client.command(insert_script)

@task(
    log_prints=True, tags=["events", "populate"], retries=1
)
def populate_event_data_from_s3():
    insert_script = f"""INSERT INTO gdelt.events SELECT * FROM s3('http://10.49.0.2:39191/gdelt/events/*.parquet','admin','admin_password')"""
    print(insert_script)
    clickhouse_client.command(insert_script)

@task(
    log_prints=True, tags=["mentions", "populate"], retries=1
)
def populate_mentions_data_from_s3():
    insert_script = f"""INSERT INTO gdelt.mentions SELECT * FROM s3('http://10.49.0.2:39191/gdelt/mentions/*.parquet','admin','admin_password')"""
    print(insert_script)
    clickhouse_client.command(insert_script)



@task(
    log_prints=True, tags=["drop_table", "clickhouse"], retries=1
)
def drop_tables():
    clickhouse_client.command(f'DROP TABLE IF EXISTS {events_table_name}')

@task(
    log_prints=True, tags=["insert", "cameo", "clickhouse"], retries=2
)
def insert_data_for_cameo_tables_from_data_lake():
    insert_data_cameo_tables_from_s3(cameo_type, "type")
    insert_data_cameo_tables_from_s3(cameo_religion, "religion")
    insert_data_cameo_tables_from_s3(cameo_knowngroup, "knowngroup")
    insert_data_cameo_tables_from_s3(cameo_goldsteinscale, "goldsteinscale")
    insert_data_cameo_tables_from_s3(cameo_eventcodes, "eventcodes")
    insert_data_cameo_tables_from_s3(cameo_ethnic, "ethnic")
    insert_data_cameo_tables_from_s3(cameo_country, "country")
    insert_data_cameo_tables_from_s3(cameo_fipscountry, "fipscountry")


@task(
    log_prints=True, tags=["create_table", "clickhouse"], retries=2
)
def create_db_dictionaries():
    clickhouse_client.command(create_cameo_dictionary.create_cameo_type_script)
    clickhouse_client.command(create_cameo_dictionary.create_cameo_religion_script)
    clickhouse_client.command(create_cameo_dictionary.create_cameo_knowngroup_script)
    clickhouse_client.command(create_cameo_dictionary.create_cameo_goldsteinscale_script)
    clickhouse_client.command(create_cameo_dictionary.create_cameo_eventcodes_script)
    clickhouse_client.command(create_cameo_dictionary.create_cameo_ethnic_script)
    clickhouse_client.command(create_cameo_dictionary.create_cameo_country_script)
    clickhouse_client.command(create_cameo_dictionary.create_cameo_fipscountry_script)


@task(
    log_prints=True, tags=["create_table", "clickhouse"], retries=2
)
def create_tables():
    clickhouse_client.command(create_gdelt_events_table())
    clickhouse_client.command(create_gdelt_mentions_table())
    clickhouse_client.command(create_cameo_tables.create_cameo_type_script)
    clickhouse_client.command(create_cameo_tables.create_cameo_religion_script)
    clickhouse_client.command(create_cameo_tables.create_cameo_knowngroup_script)
    clickhouse_client.command(create_cameo_tables.create_cameo_goldsteinscale_script)
    clickhouse_client.command(create_cameo_tables.create_cameo_eventcodes_script)
    clickhouse_client.command(create_cameo_tables.create_cameo_ethnic_script)
    clickhouse_client.command(create_cameo_tables.create_cameo_country_script)
    clickhouse_client.command(create_cameo_tables.create_cameo_fipscountry_script)

@task(
    log_prints=True, tags=["drop_table", "clickhouse"], retries=1
)
def drop_tables():
    clickhouse_client.command(f'DROP TABLE IF EXISTS {events_table_name}')
    clickhouse_client.command(f'DROP TABLE IF EXISTS {mentions_table_name}')
    clickhouse_client.command(f'DROP TABLE IF EXISTS {cameo_type}')
    clickhouse_client.command(f'DROP TABLE IF EXISTS {cameo_religion}')
    clickhouse_client.command(f'DROP TABLE IF EXISTS {cameo_knowngroup}')
    clickhouse_client.command(f'DROP TABLE IF EXISTS {cameo_goldsteinscale}')
    clickhouse_client.command(f'DROP TABLE IF EXISTS {cameo_eventcodes}')
    clickhouse_client.command(f'DROP TABLE IF EXISTS {cameo_ethnic}')
    clickhouse_client.command(f'DROP TABLE IF EXISTS {cameo_country}')
    clickhouse_client.command(f'DROP TABLE IF EXISTS {cameo_fipscountry}')



@task(
    log_prints=True, tags=["drop_table", "clickhouse"], retries=1
)
def drop_db_dictionaries():
    clickhouse_client.command(f'DROP DICTIONARY IF EXISTS {cameo_type}_dict')
    clickhouse_client.command(f'DROP DICTIONARY IF EXISTS {cameo_religion}_dict')
    clickhouse_client.command(f'DROP DICTIONARY IF EXISTS {cameo_knowngroup}_dict')
    clickhouse_client.command(f'DROP DICTIONARY IF EXISTS {cameo_goldsteinscale}_dict')
    clickhouse_client.command(f'DROP DICTIONARY IF EXISTS {cameo_eventcodes}_dict')
    clickhouse_client.command(f'DROP DICTIONARY IF EXISTS {cameo_ethnic}_dict')
    clickhouse_client.command(f'DROP DICTIONARY IF EXISTS {cameo_country}_dict')
    clickhouse_client.command(f'DROP DICTIONARY IF EXISTS {cameo_fipscountry}_dict')


@task(
    log_prints=True, tags=["load", "clickhouse"], retries=1
)
def load_to_clickhouse(df: pd.DataFrame, table_name: str):
    clickhouse_client.insert_df(table_name, df)


@flow(name="Perform Datawarehouse Actions")
def subflow_datawarehouse(clean_start=False):
    if(clean_start):
        drop_tables()
        drop_db_dictionaries()
    create_tables()
    insert_data_for_cameo_tables_from_data_lake()
    create_db_dictionaries()
    populate_event_data_from_s3()
    populate_mentions_data_from_s3()