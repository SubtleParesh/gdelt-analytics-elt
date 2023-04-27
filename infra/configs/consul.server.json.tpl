{
  "datacenter": "central",
  "data_dir": "/consul/data",
  "log_level": "INFO",
  "node_name": "server",
  "server": true,
  "bind_addr": "127.0.0.1",
  "client_addr": "0.0.0.0",
  "bootstrap_expect": 1,
  "limits": {
    "http_max_conns_per_client": 1000
  },
  "ui_config" : {
    "enabled" : true
  },
  "connect": {
     "enabled" : true
  }
}
