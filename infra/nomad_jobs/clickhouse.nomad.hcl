job "clickhouse" {
  datacenters = ["dc1"]
  type        = "service"

  group "clickhouse" {

    network {
      port "http" {
        static = 38123
        to = 8123
      }
      port "https" {
        static = 39000
        to = 9000
      }
    }

    task "clickhouse" {
      driver = "docker"

      resources {
        cpu    = 100
        memory = 200
      }

      config {
        image = "clickhouse/clickhouse-server"
        memory_hard_limit = 2000
        ports = ["http", "https"]
        volume_driver = "local"

        volumes = [
          "/home/nomad/job-volumes/clickhouse:/var/lib/clickhouse",
        ]
      }

      template {
          data = <<EOF
              CLICKHOUSE_USER="clickhouse"
              CLICKHOUSE_PASSWORD="clickhouse"
              CLICKHOUSE_DATABASE="default"
        EOF

          destination = "secrets/environment.env"
          env         = true
        }
    }
  }
}
