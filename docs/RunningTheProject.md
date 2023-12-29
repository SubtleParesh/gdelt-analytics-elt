# Running the Code

## Must have tools

- [Docker](https://docs.docker.com/engine/install/)
- Python (Conda can also be used)
- Terraform (For Cloud Deployment)- [Install from here](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform)

## Running Locally

- Install all dependencies in enviroment using requirements.txt -
  - `pip install -r requirements.txt`)
- Start **CLickhouse**, **Minio**, **Metabase**, **Prefect**, **Postgress**(For Prefect), **Prefect Agent** with Docker Compose
  - `docker compose up` or in old versions `docker-compose up`
- Update **ip_address** in `workflows/common.py` `ip_address` _Do not use 127.0.0.1 or localhost_
  - On Linux you can check using `ifconfg` command
  - On Windows, Check in Settings/Network
- Note - Before running locally please use `min_date` value to last month as test run, located in `main.py` and `run.py`
- **Running will Extract from source -> Load to Data lake (Minio)-> Populate in Database (CLickhouse) -> Transform (DBT)**

### Run On Machine Directly

- Update the main.py settings and run - `python main.py`

### Run On Prefect agent running on Docker with Deployment

- First Create deployment - `python deployment.py`
- Then Run Deployment - `python run.py`

### Running only DBT Transformation

- `dbt run` Will run the Dbt transformations

### Cloud - To setup Infrastructure with Azure with Virtual Machine

- `cd infra`
- Install Azure Cli - https://learn.microsoft.com/en-us/cli/azure/
- Login - `az login` - Note the `id` which is tenant id and `subscription_id`
- Update variables in `infra/terraform.tfvars.json`
- `tf init`
- `tf plan`
- `tf apply`
- This should take about 30mins max for all dependencies to be resolved on VM
- This will deploy Consul, [Nomad](https://www.nomadproject.io/), Traefik
- [Nomad](https://www.nomadproject.io/) will run
  - [Clickhouse](https://clickhouse.com/)
  - [Minio](https://min.io/)
  - [Metabase](https://www.metabase.com/)
  - [Prefect](https://www.prefect.io/) Server (With Postgress),
  - Prefect Agent
- Then you can update the ip address in code (Note the data source for deployment is github, update the configurations accordingly)
- Update Prefect config on local machine
  - `prefect config set PREFECT_API_URL=http://{ip_address}:4200/api`
- Run Deployment and then Prefer running deployment using Prefect UI
