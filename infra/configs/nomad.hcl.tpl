data_dir = "/opt/nomad/data"
bind_addr = "0.0.0.0"
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
  rpc = "127.0.0.1"
  serf = "127.0.0.1"
 }
 

consul {
  address = "127.0.0.1:9500"
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