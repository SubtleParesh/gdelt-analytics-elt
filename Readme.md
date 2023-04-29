# Technologies Used
* Cloud: Azure - Azure is another option to AWS and its Visual Studio Benefits is one of the reason to choose this
* Infrastructure as code (IaC): Terraform - A very mature IaC tool. And it supports lot of providers
* Workflow orchestration: Prefect - Its easy and natural to setup the workflows
* Data Lake - For Data Lake using Minio - An Alternative to S3- This is one of the best opensource tools. And this also makes the most of latency and scale
* Data Warehouse: Clickhouse is used as a Data Warehouse. its an OLAP Database and extermely space efficienct and performant

# Problem Statement
- To Analyze the Global Event Database for analysis of events for Countries and the Sentiments the events cause to Humans. Analyze the Data available and Insights it provides. Use ELT to pull raw data from gdelt source and analyze it after 
- transformations and uploading the Data

# Dashboard
- ![Event Summary Based Upon Actor Countries](./data_visualization/Events%20Summary%20Based%20Upon%20Country%20-%20Count%2C%20Map%20.png)
-  ![Show Occurances of Events based upon Location](./data_visualization/Show%20Occurances%20of%20Events%20based%20upon%20Location.png)
-  Other Dashboard Artifacts are available in data_visualization

# Running Locally
## Must have tools
- Docker
- Python (Conda can also be used)
- Terraform

### Running Perfect Workflows
- Install Prefect - pip install prefect 
- (Please install all dependencies in enviroment using requirements.txt - `pip install -r requirements.txt`)
- `docker compose up` to start CLickhouse, Minio, Metabase Locally
- Update ip address in `workflows/common.py` `ip_address` - On Linux you can check using `ifconfg` command
- Run Prefect flow - `python workflows/main.py`

## Running DBT Transformation
- `dbt run` Will run the Dbt transformations


## To setup Infrastructure with Azure with Virtual Machine
- `cd infra`
- Install Azure Cli - https://learn.microsoft.com/en-us/cli/azure/
- Login - `az login` - Note the `id` which is tenant id and `subscription_id`
- Update variables in `infra/terraform.tfvars.json`
- `tf init`
- `tf plan`
- `tf apply`
- This should take about 30mins max for all dependencies to be resolved on VM
- You can then use IP over Docker compose


REFERENCES:
GDELT Home Page - https://www.gdeltproject.org/
Clickhouse + Metabse - https://clickhouse.com/docs/en/integrations/metabase
Clickhouse + DBT - https://clickhouse.com/docs/en/integrations/dbt#concepts
Metabase Clickhouse driver - https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.1.3/clickhouse.metabase-driver.jar


FAQS 
- If you run into error related to access on linux for docker compose, metabase directory access- `sudo chmod 777 -R ./metabase-data-plugin`
