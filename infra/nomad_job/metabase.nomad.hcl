job "metabase" {
  datacenters = ["home"]
  type        = "service"

  group "metabase" {
    
    network {
      port "http" {
        to = 3000
        host_network = "wg"
      }
      port "https" {
        to = 3000
        host_network = "wg"
      }
    }

    service {
      name = "metabase"
      port = "https"

      tags = [
        "traefik.enable=true",
        "traefik.http.routers.metabase.rule=Host(`metabase.kritrim.space`)",
        "traefik.http.routers.metabase.entrypoints=websecure",
        "traefik.http.routers.metabase.tls=true",
        "traefik.http.routers.metabase.tls.certresolver=letsencrypt",
        "traefik.http.routers.metabase.middlewares=authelia@file",
      ]

      check {
        type     = "http"
        path     = "/"
        interval = "2s"
        timeout  = "2s"
      }
    }

    task "metabase" {
      driver = "docker"

      resources {
        cpu    = 100
        memory = 100
      }

      config {
        image = "metabase/metabase:v0.46.1"
        memory_hard_limit = 2000
        volumes = [
          "/home/nomad/job-volumes/metabase-data:/metabase-data",
          "/home/nomad/job-volumes/metabase-plugins:/plugins"
        ]        
        volume_driver = "local"
        ports = ["http", "https"]
        # command = "cp /plugins-copy/ /plugins"
        # command = "curl -o /plugins/clickhouse_plugin.jar https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.1.3/clickhouse.metabase-driver.jar"
      }

      template {
          data = <<EOF
              # Lines starting with a # are ignored
              # Empty lines are also ignored Change 2
              MB_DB_FILE=/metabase-data/metabase.db
              JAVA_TIMEZONE=Asia/Kolkata
        EOF

          destination = "secrets/environment.env"
          env         = true
        }       
    }

      # Define the pre-start task to download the file
      # to the local mount point
      #  task "pre-start-nomad" {
      #   driver = "exec"

      #   config {
      #     command = "curl -o /home/nomad/job-volumes/metabase-plugins/clickhouse_plugin.jar https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.1.3/clickhouse.metabase-driver.jar"
      #     # mount_path = "/home/nomad/job-volumes/metabase-plugins"
      #   }
      # }
  }
}



