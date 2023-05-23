data_dir = "/opt/nomad/data"
bind_addr = "10.0.2.6"
datacenter = "node1"

# Enable the server
server {
  enabled = false
  bootstrap_expect = 1
}

client {
  enabled = true
}

advertise {
  http = "10.0.2.6"
  rpc = "10.0.2.6"
  serf = "10.0.2.6"
}

consul {
  address = "10.0.2.6:9500"
  server_service_name = "nomad"
  client_service_name = "nomad-node"
}

plugin "docker" {
  config {
    volumes {
      enabled = true
      selinuxlabel = "z"
    }
    allow_privileged = true
  }
}
