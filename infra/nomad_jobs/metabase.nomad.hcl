job "metabase" {
  datacenters = ["dc1"]
  type        = "service"

  group "metabase" {

    network {
      port "http" {
        static = 3000
        to = 3000
      }
    }

    service {
      name = "metabase"
      port = "http"

      tags = [
        "traefik.enable=true",
        "traefik.http.routers.metabase.rule=Host(`gdelt-analytics.centralindia.cloudapp.azure.com`)",
        "traefik.http.routers.metabase.entrypoints=web,websecure",
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
        memory = 200
      }

      config {
        image = "metabase/metabase:v0.46.1"
        memory_hard_limit = 2000
        ports = ["http"]
        volume_driver = "local"

        volumes = [
          "/home/nomad/job-volumes/metabase-data:/metabase-data",
          "/home/nomad/job-volumes/metabase-plugins:/plugins",
        ]
      }

      template {
          data = <<EOF
              MB_DB_FILE=/metabase-data/metabase.db
        EOF

          destination = "secrets/environment.env"
          env         = true
        }
    }
  }
}
