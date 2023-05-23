job "prefect" {
  datacenters = ["dc1"]
  type        = "service"

  group "prefect" {

    network {
      port "prefect_api" {
        static = 4200
        to = 4200
      }
      port "prefect_db" {
        static = 5432
        to = 5432
      }
    }

    service {
      name = "prefect"
      port = "prefect_api"

      tags = [
        "traefik.enable=true",
        "traefik.http.routers.prefect.rule=Host(`prefect.gdelt-analytics.centralindia.cloudapp.azure.com`)",
        "traefik.http.routers.prefect.entrypoints=web,websecure",
        "traefik.http.routers.prefect.middlewares=default-auth@file",
      ]
    }

    task "prefect" {
      driver = "docker"

      resources {
        cpu    = 250
        memory = 400
      }

      config {
        image = "prefecthq/prefect:2-python3.11"
        args = [
          "prefect",
          "server",
          "start"
        ]
        network_mode="host"
        memory_hard_limit = 2000
        ports = ["prefect_api"]
        volume_driver = "local"

        volumes = [
          "/home/nomad/job-volumes/prefect:/root/.prefect",
          "/home/nomad/job-volumes/prefect-flows:/flows"
        ]
      }

      template {
          data = <<EOF
              PREFECT_ORION_API_HOST = "0.0.0.0"
              PREFECT_ORION_DATABASE_CONNECTION_URL = "postgresql+asyncpg://prefect:prefect_password@{{ env "NOMAD_IP_prefect_db" }}:{{ env "NOMAD_PORT_prefect_db" }}/prefect_server"
              PREFECT_ORION_ANALYTICS_ENABLED = "false"
              PREFECT_LOGGING_SERVER_LEVEL = "WARNING"
              PREFECT_API_URL = "http://gdelt-analytics.centralindia.cloudapp.azure.com:4200/api"
        EOF

          destination = "local/environment.env"
          env         = true
        }
    }


    task "prefect-postgres-db" {
      driver = "docker"

      resources {
        cpu    = 250
        memory = 400
      }

      config {
        image = "postgres:15.3"
        memory_hard_limit = 1500
        ports = ["prefect_db"]
        volume_driver = "local"
        volumes = [
          "/home/nomad/job-volumes/postgres:/var/lib/postgresql/data",
        ]
      }

      template {
          data = <<EOF
              POSTGRES_USER = "prefect"
              POSTGRES_PASSWORD = "prefect_password"
              POSTGRES_DB = "prefect_server"
        EOF

          destination = "secrets/environment.env"
          env         = true
        }
    }

    task "prefect-agent" {
      driver = "docker"

      resources {
        cpu    = 200
        memory = 500
      }

      config {
        image = "prefecthq/prefect:2-python3.10"
        args = [
          "prefect",
          "agent",
          "start",
          "-q",
          "default",
          "--limit",
          "1"
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
              PREFECT_API_URL= http://10.0.2.5:4200/api
              PREFECT_LOGGING_LEVEL=ERROR
              DOCKER_HOST=unix://var/run/docker.sock
              EXTRA_PIP_PACKAGES="pandas clickhouse-connect==0.5.18 clickhouse-driver==0.2.5 minio prefect_dask requests dbt-core==1.4.5 pyarrow fastparquet dbt-clickhouse==1.4.0 dbt-extractor==0.4.1 prefect-sqlalchemy dask[dataframe] prefect-dbt[cli] prefect-dbt prefect-shell prefect-sqlalchemy==0.2.2 hydra-core aiohttp requests"
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
              NUM_WORKERS=1
              NUM_THREADS=1
        EOF

          destination = "local/environment.env"
          env         = true
        }
    }
  }
}
