# Deployment on Azure
- One VM
  - Consul + Nomad + Traefik + Docker (Rootless)
  - Nomad Jobs - Metabase(with clickhouse Support) +  Clickhouse 
  - Publicly Available - Metabase Public Dashboard
  - Public Authenticated - Metabase, Consul, Nomad, Traefik
  - Prefect installed and docker agent running

sudo chmod 777 -R ./metabase-data

https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.1.3/clickhouse.metabase-driver.jar


https://www.gdeltproject.org/data/lookups/CAMEO.country.txt
https://www.gdeltproject.org/data/lookups/