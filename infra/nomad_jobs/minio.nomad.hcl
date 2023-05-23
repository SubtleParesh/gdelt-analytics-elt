
job "minio" {
  datacenters = ["dc1"]
  type        = "service"

  group "minio" {

    network {
      port "http" {
        static = 39090
        to = 9090
      }
      port "api" {
        static = 39191
        to = 9000
      }
    }

    task "minio" {
      driver = "docker"

      resources {
        cpu    = 100
        memory = 200
      }

      config {
        image = "minio/minio:latest"
        ports = ["http", "api"]
        memory_hard_limit = 2000
        volumes = [
          "/home/nomad/job-volumes/minio:/mnt/data"
        ]
        volume_driver = "local"
        args = [
          "server",
          "--console-address", ":9090"
        ]
     }

     template {
        data = <<EOF
        MINIO_ROOT_USER=admin
        MINIO_ROOT_PASSWORD=password
        MINIO_VOLUMES=/mnt/data
        EOF

        destination = "secrets/minio.env"
          env         = true
        }
    }
  }
}
