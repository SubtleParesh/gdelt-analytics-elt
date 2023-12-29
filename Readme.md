# GDELT (Global Database of Events, Language, and Tone) ELT and Analytics

This project focuses on leveraging the Global Database of Events, Language, and Tone (GDELT) for in-depth analysis of events occurring in different countries and the corresponding sentiments these events evoke in humans. The primary objective is to extract valuable insights from the available data. The process involves Extract, Load, and Transform (ELT) operations, where raw data is pulled from the GDELT source, undergoes transformations, and is then uploaded for analysis.

- ![ELT](./diagrams/GDELT%20Analytics%20-%20ELT.png)
- ![Infrastructure](./diagrams/GDELT%20Cloud%20Infrastructure.png)

## Technologies Used

- Cloud: Azure - Chosen for its Visual Studio benefits as an alternative to AWS.
- Infrastructure as code (IaC): [Terraform](https://www.terraform.io/) - A mature IaC tool supporting various providers.
- Workflow orchestration: Prefect (Alternate to Airflow) - Selected for its simplicity and ease of setting up workflows.
- Data Lake - For Data Lake using [Minio](https://min.io/) - An open-source alternative to S3, known for its low latency and scalability.
- Data Warehouse: [Clickhouse](https://clickhouse.com/) - An OLAP Database with high space efficiency and performance.
- Batch Processing: [Dask](https://www.dask.org/) - A concurrent task scheduler integrated with Prefect, serving as an alternative to Spark.
- Infrastructure Orchestrator: [Nomad](https://www.nomadproject.io/) - As an container orchestrator an Kubernetes alternative
- Data Analytics Tool: [Metabase](https://www.metabase.com/) - An open-source tool for visualizing data.

## Documentations

#### [Infrastructure](./docs/Infrastructure.md)

#### [Database](./docs/Database.md)

#### [Running the Project](./docs/RunningTheProject.md)

## Dashboard Links

![Dashboard 1 - 1](./screenshots/Dashboard%201%20-%201.png)
![Dashboard 1 - 2](./screenshots/Dashboard%201%20-%202.png)
![Dashboard 2](./screenshots/Dashboard%202.png)

## Data Visualizations - Metabase

- [Metabase](https://www.metabase.com/) can be used from cloud or local machine at port `3000`
- PLEASE CHECK `screenshots` for idea on how different tools are working together

## REFERENCES:

- GDELT Home Page - https://www.gdeltproject.org/
- Clickhouse + Metabse - https://clickhouse.com/docs/en/integrations/metabase
- Clickhouse + DBT - https://clickhouse.com/docs/en/integrations/dbt#concepts
- Metabase Clickhouse driver - https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.1.3/clickhouse.metabase-driver.jar

## FAQS

- If you run into error related to access on linux for docker compose, metabase directory access- `sudo chmod 777 -R ./metabase-data-plugin`
- In case of Run time error or high CPU or Memory Utilization Please check configs at `data_lake_flows.py/subflow_to_load_csv_to_datalake`

## Running Precommit

pre-commit run --all-files
