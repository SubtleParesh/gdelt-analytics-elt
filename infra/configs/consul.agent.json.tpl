{
  "datacenter": "central",
  "data_dir": "/opt/consul",
  "log_level": "INFO",
  "node_name": "server-agent",
  "server": false,
  "retry_join": ["127.0.0.1:8301"],
  "bind_addr": "127.0.0.1",
  "client_addr": "0.0.0.0",
  "ports": {
    "dns": 9600,
    "http": 9500,
    "https": 9501,
    "serf_lan": 9301,
    "serf_wan": 9302
  },
  "limits": {
    "http_max_conns_per_client": 500
  },
  "ui_config" : {
      "enabled" : false
  }
}