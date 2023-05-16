data_dir = "/opt/nomad/data"
bind_addr = "10.0.2.5"

# Enable the server
server {
  enabled = true
  bootstrap_expect = 1
}

client {
  enabled       = true
}

advertise {
  http = "0.0.0.0"
  rpc = "10.0.2.5"
  serf = "10.0.2.5"
 }


consul {
  address = "10.0.2.5:9500"
  server_service_name = "nomad"
  client_service_name = "nomad-client"
}


plugin "docker" {
  config {
    volumes {
      enabled      = true
      selinuxlabel = "z"
    }
    allow_privileged = true
  }
}
