from prefect.deployments import Deployment
from prefect.filesystems import GitHub

from main import main_flow

if __name__ == "__main__":
    github_block_name = "gdelt-analytics-etl-github"
    github_url = "https://github.com/SubtleParesh/gdelt-analytics-etl.git"

    github_storage_block = GitHub(repository=github_url, reference="develop").save(
        github_block_name, overwrite=True
    )

    github_storage = GitHub.load(github_block_name)
    docker_deployment = Deployment.build_from_flow(
        name="master_flow_gdelt",
        flow=main_flow,
        version="1.0.0",
        storage=github_storage,
        entrypoint="./workflows/main_flow.py:main_flow",
        parameters={
            "master_csv_list_url": "http://data.gdeltproject.org/gdeltv2/lastupdate.txt",
            "min_date": "1/04/2023",
            "clean_start": True,
        },
        work_queue_name="node",
    )
    deployment_id = docker_deployment.apply()
