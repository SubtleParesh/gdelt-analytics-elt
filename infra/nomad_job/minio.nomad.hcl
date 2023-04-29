

job "minio" {
  datacenters = ["home"]
  type        = "service"

  group "minio" {
    
    network {
      mode = "bridge"
      port "http" {
        to = 9090
        host_network = "wg"
      }
      port "api" {
        to = 9000
        host_network = "wg"
      }
    }

    service {
      name = "minio"
      port = "http"

      tags = [
        "traefik.enable=true",
        "traefik.http.routers.minio.rule=Host(`minio.kritrim.space`)",
        "traefik.http.routers.minio.entrypoints=websecure",
        "traefik.http.routers.minio.tls=true",
        "traefik.http.routers.minio.tls.certresolver=letsencrypt",
        "traefik.http.routers.minio.middlewares=authelia@file",
      ]
    }

    service {
      name = "minio-api"
      port = "api"

      tags = [
        "traefik.enable=true",
        "traefik.http.routers.minio_api.rule=Host(`api.minio.kritrim.space`)",
        "traefik.http.routers.minio_api.entrypoints=websecure",
        "traefik.http.routers.minio_api.tls=true",
        "traefik.http.routers.minio_api.tls.certresolver=letsencrypt",
      ]
    }

    task "minio" {
      driver = "docker"

      resources {
        cpu    = 100
        memory = 200
      }

      config {
        image = "minio/minio:latest"
        ports = ["http"]
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
        # Lines starting with a # are ignored
        # Empty lines are also ignored hange 2

        MINIO_ROOT_USER="{{ with secret "secret/minio" }}{{ .Data.username }}{{ end }}"
        MINIO_ROOT_PASSWORD="{{ with secret "secret/minio" }}{{ .Data.password }}{{ end }}"
        MINIO_VOLUMES="/mnt/data"

        EOF

        destination = "secrets/minio.env"
          env         = true
        }
    }
  }
}



