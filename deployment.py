from prefect.filesystems import GitHub
from prefect.infrastructure import DockerContainer
from prefect.deployments import Deployment, run_deployment
from main import main_flow


if __name__ == "__main__":
    github_storage_block = GitHub(
            repository="https://github.com/SubtleParesh/gdelt-analytics-etl.git",
            reference="main"
        ).save("gdelt-analytics-etl-github", overwrite=True)

    github_storage = GitHub.load("gdelt-analytics-etl-github")
    docker_deployment = Deployment.build_from_flow(
        name="master_flow_gdelt",
        flow=main_flow,
        version="1.0.0",
        storage=github_storage,
        entrypoint="workflows/main.py:main_flow",
        parameters= {
            "master_csv_list_url":"http://data.gdeltproject.org/gdeltv2/lastupdate.txt",
            "min_date": "1/04/2023",
            "clean_start": True
        }
        # schedule=
    )
    deployment_id = docker_deployment.apply()

    run_deployment(
        name="Intialization Ingest Data/master_flow_gdelt",
        parameters= {
            "master_csv_list_url":"http://data.gdeltproject.org/gdeltv2/masterfilelist.txt",
            "min_date": "1/04/2023",
            "clean_start": True
        }
    )