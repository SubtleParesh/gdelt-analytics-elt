job "prefect-agent-worker" {
  datacenters = ["node1"]
  type        = "service"

  group "prefect-agent-worker" {

    task "prefect-agent" {
      driver = "docker"

      resources {
        cpu    = 100
        memory = 100
      }

      config {
        image = "prefecthq/prefect:2-python3.10"
        args = [
          "prefect",
          "agent",
          "start",
          "-q",
          "node"
        ]
        privileged = true
        memory_hard_limit = 5500
        volume_driver = "local"
        volumes = [
          "/var/run/docker.sock:/var/run/docker.sock",
        ]
      }

      template {
          data = <<EOF
              PREFECT_API_URL= http://{{ env "NOMAD_IP_prefect_api" }}:4200/api
              PREFECT_LOGGING_LEVEL= DEBUG
              DOCKER_HOST= unix://var/run/docker.sock
              EXTRA_PIP_PACKAGES="pandas clickhouse-connect==0.5.18 clickhouse-driver==0.2.5 minio prefect_dask requests dbt-core==1.4.5 pyarrow fastparquet dbt-clickhouse==1.4.0 dbt-extractor==0.4.1 prefect-sqlalchemy dask[dataframe] prefect-dbt[cli] prefect-dbt prefect-shell prefect-sqlalchemy==0.2.2"
        EOF

          destination = "local/environment.env"
          env         = true
        }
    }
  }
}
