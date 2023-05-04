from prefect import flow
from prefect_dbt.cli.commands import DbtCoreOperation

@flow
def trigger_dbt_flow():
    result = DbtCoreOperation(
        commands=["ls", "dbt debug", "dbt run"],
        project_dir="./dbt_transformations",
        profiles_dir="./dbt_transformations"
    ).run()