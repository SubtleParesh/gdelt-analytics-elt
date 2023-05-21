from prefect import flow
from prefect_dbt.cli import DbtCliProfile
from prefect_dbt.cli.commands import DbtCoreOperation
from prefect_dbt.cli.configs import TargetConfigs

from workflows.common import Configuration


@flow(name="GDELT ELT - DBT Tranformation Sub Workflow", log_prints=True)
def trigger_dbt_flow(config: Configuration):
    target_configs_extras = dict(
        host=config.clickhouse.ip_address,
        user=config.clickhouse.username,
        password=config.clickhouse.password,
        port=config.clickhouse.port,
        secure=False,
    )
    target_configs = TargetConfigs(
        type="clickhouse", schema="gdelt", threads=4, extras=target_configs_extras
    )
    dbt_cli_profile = DbtCliProfile(
        name="dbt_transformations",
        target="dev",
        target_configs=target_configs,
    )
    dbt_cli_profile.get_profile()
    print(dbt_cli_profile.get_profile())
    DbtCoreOperation(
        commands=["ls &&", "dbt debug", "dbt run"],
        project_dir="dbt_transformations",
        profiles_dir="dbt_transformations",
        stream_output=True,
        overwrite_profiles=True,
        dbt_cli_profile=dbt_cli_profile,
    ).run()
