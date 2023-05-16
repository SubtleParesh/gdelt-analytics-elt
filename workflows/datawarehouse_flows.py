from datetime import datetime

import clickhouse_connect
import pandas as pd
from prefect import flow, task

import workflows.sql.cameo_tables as cameo_tables
from workflows.common import Configuration, Table


def get_clickhouse_client(configuration: Configuration):
    database = "gdelt"

    temp_client = clickhouse_connect.get_client(
        host=configuration.clickhouse.ip_address,
        port=configuration.clickhouse.port,
        username=configuration.clickhouse.username,
        password=configuration.clickhouse.password,
        send_receive_timeout=500,
    )
    temp_client.command(f"CREATE DATABASE IF NOT EXISTS {database}")

    client = clickhouse_connect.get_client(
        host=configuration.clickhouse.ip_address,
        port=configuration.clickhouse.port,
        username=configuration.clickhouse.username,
        password=configuration.clickhouse.password,
        database=database,
    )
    return client


def insert_data_cameo_tables_from_s3(
    table_name: str, cameo_name: str, config: Configuration
):
    clickhouse_client = get_clickhouse_client(config)
    insert_script = f"""INSERT INTO gdelt.{table_name} SELECT * FROM s3('http://{config.minio.ip_address}:{config.minio.port}/gdelt/cameo/{cameo_name}/data.parquet','{config.minio.username}','{config.minio.password}')"""
    print(insert_script)
    clickhouse_client.command(insert_script)


@task(log_prints=True, tags=["events", "populate"], retries=1)
def populate_event_data_from_s3(config: Configuration):
    clickhouse_client = get_clickhouse_client(config)
    for year in range(2015, datetime.now().year + 1):
        for month in range(1, 13):
            month_str = str(month)
            if month < 10:
                month_str = "0" + month_str
            insert_script = f"""INSERT INTO gdelt.events SELECT * FROM s3('http://{config.minio.ip_address}:{config.minio.port}/gdelt/events/{year}-{month_str}*.parquet','{config.minio.username}','{config.minio.password}')"""
            print(insert_script)
            try:
                clickhouse_client.command(insert_script)
            except clickhouse_connect.driver.exceptions.DatabaseError:
                print(f"Failed in {year}-{month_str}")


@task(log_prints=True, tags=["mentions", "populate"], retries=1)
def populate_mentions_data_from_s3(config: Configuration):
    clickhouse_client = get_clickhouse_client(config)
    for year in range(2015, datetime.now().year + 1):
        for month in range(1, 13):
            month_str = str(month)
            if month < 10:
                month_str = "0" + month_str
            insert_script = f"""INSERT INTO gdelt.mentions SELECT * FROM s3('http://{config.minio.ip_address}:{config.minio.port}/gdelt/mentions/{year}-{month_str}*.parquet','{config.minio.username}','{config.minio.password}')"""
            print(insert_script)
            try:
                clickhouse_client.command(insert_script)
            except clickhouse_connect.driver.exceptions.DatabaseError:
                print(f"Failed in {year}-{month_str}")


@task(log_prints=True, tags=["insert", "cameo", "clickhouse"], retries=2)
def insert_data_for_cameo_tables_from_data_lake(config: Configuration):
    table = Table()
    insert_data_cameo_tables_from_s3(table.cameo_type, "type", config=config)
    insert_data_cameo_tables_from_s3(table.cameo_religion, "religion", config=config)
    insert_data_cameo_tables_from_s3(
        table.cameo_knowngroup, "knowngroup", config=config
    )
    insert_data_cameo_tables_from_s3(
        table.cameo_goldsteinscale, "goldsteinscale", config=config
    )
    insert_data_cameo_tables_from_s3(
        table.cameo_eventcodes, "eventcodes", config=config
    )
    insert_data_cameo_tables_from_s3(table.cameo_ethnic, "ethnic", config=config)
    insert_data_cameo_tables_from_s3(table.cameo_country, "country", config=config)
    insert_data_cameo_tables_from_s3(
        table.cameo_fipscountry, "fipscountry", config=config
    )


@task(log_prints=True, tags=["create_table", "clickhouse"], retries=2)
def create_tables(config: Configuration):
    table = Table()
    clickhouse_client = get_clickhouse_client(config)
    clickhouse_client.command(table.create_gdelt_events_table())
    clickhouse_client.command(table.create_gdelt_mentions_table())
    clickhouse_client.command(cameo_tables.create_cameo_type_script)
    clickhouse_client.command(cameo_tables.create_cameo_religion_script)
    clickhouse_client.command(cameo_tables.create_cameo_knowngroup_script)
    clickhouse_client.command(cameo_tables.create_cameo_goldsteinscale_script)
    clickhouse_client.command(cameo_tables.create_cameo_eventcodes_script)
    clickhouse_client.command(cameo_tables.create_cameo_ethnic_script)
    clickhouse_client.command(cameo_tables.create_cameo_country_script)
    clickhouse_client.command(cameo_tables.create_cameo_fipscountry_script)


@task(log_prints=True, tags=["drop_table", "clickhouse"], retries=1)
def drop_tables(config: Configuration):
    table = Table()
    clickhouse_client = get_clickhouse_client(config)
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.events}")
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.mentions}")
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.cameo_type}")
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.cameo_religion}")
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.cameo_knowngroup}")
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.cameo_goldsteinscale}")
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.cameo_eventcodes}")
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.cameo_ethnic}")
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.cameo_country}")
    clickhouse_client.command(f"DROP TABLE IF EXISTS {table.cameo_fipscountry}")


@task(log_prints=True, tags=["load", "clickhouse"], retries=1)
def load_to_clickhouse(df: pd.DataFrame, table_name: str, config: Configuration):
    clickhouse_client = get_clickhouse_client(config)
    clickhouse_client.insert_df(table_name, df)


@flow(name="GDELT ELT - Datawarehouse Sub Workflow")
def subflow_datawarehouse(configuration, clean_start=False):
    if clean_start:
        drop_tables(configuration)
    create_tables(configuration)
    insert_data_for_cameo_tables_from_data_lake(configuration)
    populate_event_data_from_s3(configuration)
    populate_mentions_data_from_s3(configuration)
