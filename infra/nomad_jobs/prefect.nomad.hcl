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

      check {
        type     = "http"
        path     = "/"
        interval = "2s"
        timeout  = "2s"
      }
    }

    task "prefect" {
      driver = "docker"

      resources {
        cpu    = 100
        memory = 200
      }

      config {
        image = "prefecthq/prefect:2-python3.10"
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
        cpu    = 100
        memory = 200
      }

      config {
        image = "postgres:14"
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
          "default"
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
              EXTRA_PIP_PACKAGES="pandas clickhouse_connect minio prefect_dask requests dbt-core prefect-dbt[cli]"
        EOF

          destination = "local/environment.env"
          env         = true
        }    
    }
  }
}

