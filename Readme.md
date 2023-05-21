# Problem Statement

- To Analyze the Global Event Database for analysis of events for Countries and the Sentiments the events cause to Humans. Analyze the Data available and Insights it provides. Use ELT to pull raw data from gdelt source and analyze it after transformations and uploading the Data

- ![ELT](./diagrams/GDELT%20Analytics%20-%20ELT.png)

## Technologies Used

- Cloud: Azure - Azure is another option to AWS and its Visual Studio Benefits is one of the reason to choose this
- Infrastructure as code (IaC): [Terraform](https://www.terraform.io/) - A very mature IaC tool. And it supports lot of providers
- Workflow orchestration: Prefect - Its easy and natural to setup the workflows
- Data Lake - For Data Lake using [Minio](https://min.io/) - An Alternative to S3- This is one of the best opensource tools. And this also makes the most of latency and scale
- Data Warehouse: [Clickhouse](https://clickhouse.com/) is used as a Data Warehouse. its an OLAP Database and extermely space efficienct and performant
- Batch Processing: [Dask](https://www.dask.org/) - Its a concurrent task scheduler where well Integrated with Prefect. This is alternate to Spark
- Infrastructure Orchestrator: [Nomad](https://www.nomadproject.io/) a Kubernetes alternative
- Data Analytics Tool: [Metabase](https://www.metabase.com/) Its another Opensource tool to visualize the Data

## Dashboard Links

https://metabase.kritrim.space/public/dashboard/3fa3c05d-d3e5-4547-9f25-c4910d211e52?month_and_year=2023-01
![Dashboard 1 - 1](./screenshots/Dashboard%201%20-%201.png)
![Dashboard 1 - 2](./screenshots/Dashboard%201%20-%202.png)
![Dashboard 2](./screenshots/Dashboard%202.png)

https://metabase.kritrim.space/public/dashboard/608cfec5-16ba-4058-84f0-d756e839e502

## Data Visualizations - Metabase

- [Metabase](https://www.metabase.com/) can be used from cloud or local machine at port `3000`

- PLEASE CHECK `screenshots` for idea on how different tools are working together

### REFERENCES:

- GDELT Home Page - https://www.gdeltproject.org/
- Clickhouse + Metabse - https://clickhouse.com/docs/en/integrations/metabase
- Clickhouse + DBT - https://clickhouse.com/docs/en/integrations/dbt#concepts
- Metabase Clickhouse driver - https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.1.3/clickhouse.metabase-driver.jar

### FAQS

- If you run into error related to access on linux for docker compose, metabase directory access- `sudo chmod 777 -R ./metabase-data-plugin`
- In case of Run time error or high CPU or Memory Utilization Please check configs at `data_lake_flows.py/subflow_to_load_csv_to_datalake`

### Precommit -

pre-commit run --all-files

### Todo

- Pre Commit Hooks - Done -
- CI with Github Workflow
  - Dbt debug
  - pythong static analysis
  - python black analysis or similar
  - nomad job check
  - tf check
- Lock main branch only allow with pr - Done
- VM always on + VM for batch Processing = 1 main (all + dask scheduler + 1 worker) + 1 worker (Evictable) Config complete
- Create schedule for 15mins updates, Create Run
- Incremental table view with dbt - only one events summary table
- One Events dashboard
- One Comparison Dashboard between countries
- Events table with s3 function - Done
- Update Events materialized tables with updated data types (compare size after materialization)
- Enviornment variables everywhere # Done, chages to add env variable to nomad file

First Deployed run on aws azure and then dashboards
