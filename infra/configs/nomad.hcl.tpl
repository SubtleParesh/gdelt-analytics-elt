data_dir = "/opt/nomad/data"
bind_addr = "127.0.0.1"
# Enable the server
server {
  enabled = true
  bootstrap_expect = 1
}
client {
  enabled       = true
}

advertise {
  http = "127.0.0.1"
  rpc = "127.0.0.1"
  serf = "127.0.0.1"
 }
 

consul {
  address = "127.0.0.1:9500"
  server_service_name = "nomad"
  client_service_name = "nomad-client"
}

vault {
  enabled = true
  address = "http://127.0.0.1:8200"
}

plugin "docker" {
  config {
    # endpoint = "unix:///var/run/docker.sock"

    # auth {
    #   config = "/etc/docker-auth.json"
    #   helper = "ecr-login"
    # }

    # tls {
    #   cert = "/etc/nomad/nomad.pub"
    #   key  = "/etc/nomad/nomad.pem"
    #   ca   = "/etc/nomad/nomad.cert"
    # }

    # extra_labels = ["job_name", "job_id", "task_group_name", "task_name", "namespace", "node_name", "node_id"]

    # gc {
    #   image       = true
    #   image_delay = "3m"
    #   container   = true

    #   dangling_containers {
    #     enabled        = true
    #     dry_run        = false
    #     period         = "5m"
    #     creation_grace = "5m"
    #   }
    # }

    volumes {
      enabled      = true
      selinuxlabel = "z"
    }

    allow_privileged = true
  }
}