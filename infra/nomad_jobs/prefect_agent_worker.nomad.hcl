job "prefect-agent-worker" {
  datacenters = ["node1"]
  type        = "service"

  group "prefect-agent-worker" {

    task "prefect-agent" {
      driver = "docker"

      resources {
        cpu    = 1000
        memory = 2000
      }

      config {
        image = "prefecthq/prefect:2-python3.10"
        args = [
          "prefect",
          "agent",
          "start",
          "--pool",
          "default-agent-pool",
          "--work-queue",
          "node",
          "--limit",
          "1"
        ]
        privileged = true
        memory_hard_limit = 7500
        volume_driver = "local"
        volumes = [
          "/var/run/docker.sock:/var/run/docker.sock",
        ]
      }

      template {
          data = <<EOF
              PREFECT_API_URL= http://10.0.2.5:4200/api
              PREFECT_LOGGING_LEVEL= DEBUG
              DOCKER_HOST=unix://var/run/docker.sock
              EXTRA_PIP_PACKAGES="pandas clickhouse-connect==0.5.18 clickhouse-driver==0.2.5 minio prefect_dask==0.2.3 dask==2023.4.0 requests dbt-core==1.4.5 pyarrow fastparquet dbt-clickhouse==1.4.0 dbt-extractor==0.4.1 prefect-sqlalchemy dask[dataframe] prefect-dbt[cli] prefect-dbt prefect-shell prefect-sqlalchemy==0.2.2 hydra-core aiohttp requests"
              # Following Secrets/Configs can be overridden
              CLICKHOUSE_USERNAME=admin
              CLICKHOUSE_PASSWORD=password
              CLICKHOUSE_IP_ADDRESS=10.0.2.5
              CLICKHOUSE_PORT=38123
              MINIO_USERNAME=admin
              MINIO_PASSWORD=password
              MINIO_IP_ADDRESS=10.0.2.5
              MINIO_PORT=39191
              IP_ADDRESS=10.0.2.5
              NUM_WORKERS=4
              NUM_THREADS=1
        EOF

          destination = "local/environment.env"
          env         = true
        }
    }
  }
}
