#!/usr/bin/env bash
sleep 3m
echo "Cloud Init Started"


# INSTALL SYSTEM PACKAGES
sudo apt-get install -y unzip tree redis-tools jq curl tmux git resolvconf apt-transport-https ca-certificates curl gnupg lsb-release

# ****************************************************************
# ADD APT REPOSITORY SOURCES
# ****************************************************************

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add -

sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo add-apt-repository -y ppa:openjdk-r/ppa

sudo apt-get update

# INSTALL DOCKER
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose

# INSTALL JAVA
sudo apt-get update
sudo apt-get install -y openjdk-8-jdk

# INSTALL HASHICORP-CONSUL, NOMAD

sudo apt-get install -y consul nomad

# INSTALL JQ
curl --silent -Lo /bin/jq https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64
sudo chmod +x /bin/jq

echo "Configuring system time"
timedatectl set-timezone UTC

# ****************************************************************
# CONFIG FILES
# ****************************************************************

sudo mkdir /etc/consul.d.server
sudo mkdir /etc/consul.d
sudo mkdir /etc/nomad.d
sudo mkdir /etc/traefik

# SETUP CONFIGURATION FILES
sudo cp /home/ubuntu/cloudinit/consul.server.json /etc/consul.d.server/consul.json
sudo cp /home/ubuntu/cloudinit/consul.agent.json /etc/consul.d/consul.json
sudo cp /home/ubuntu/cloudinit/consul.service /etc/systemd/system/consul.service
sudo cp /home/ubuntu/cloudinit/nomad.hcl /etc/nomad.d/nomad.hcl
sudo cp /home/ubuntu/cloudinit/traefik.yml /etc/traefik/traefik.yml
sudo cp /home/ubuntu/cloudinit/traefikConfig.yml /etc/traefik/traefikConfig.yml
sudo cp /home/ubuntu/cloudinit/traefik.service /etc/systemd/system/traefik.service
sudo cp /home/ubuntu/cloudinit/netplan_60-static.yaml /etc/netplan/60-static.yaml
sudo cp /home/ubuntu/cloudinit/daemon.json /etc/docker/daemon.json

sudo chown -R nomad:nomad /etc/nomad.d
sudo chmod -R 640 /etc/nomad.d/*
sudo chmod 600 /etc/traefik/acme.json

mkdir /home/nomad
mkdir /home/nomad/job-volumes
mkdir /home/ubuntu/traefik
mkdir /etc/traefik
mkdir /home/nomad/job-volumes/metabase-plugins

# ****************************************************************
# SETUP RAW FILES
# ****************************************************************

cd /home/ubuntu/traefik || exit
wget -q https://github.com/traefik/traefik/releases/download/v2.6.1/traefik_v2.6.1_linux_amd64.tar.gz
tar -zxvf traefik_v2.6.1_linux_amd64.tar.gz


cd /home/nomad/job-volumes/metabase-plugins/ || exit
wget https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.1.3/clickhouse.metabase-driver.jar
sudo chmod -R a+rwx  /home/nomad/job-volumes/metabase-plugins

# ****************************************************************
# CONSUL
# ****************************************************************

sudo docker run -d \
  -v /etc/consul.d.server:/consul/config \
  -v /data/consul.server:/consul/data \
  --net=host \
  --restart always \
  --name=consul_server \
  consul agent --config-dir=/consul/config

sleep 120

sudo systemctl enable consul
sudo systemctl start consul

sleep 120

sudo systemctl enable nomad
sudo systemctl start nomad

sudo systemctl enable traefik
sudo systemctl start traefik

sleep 60

export NOMAD_ADDR=http://10.0.2.5:4646

nomad job run /home/ubuntu/nomad_jobs/clickhouse.nomad.hcl
nomad job run /home/ubuntu/nomad_jobs/minio.nomad.hcl
nomad job run /home/ubuntu/nomad_jobs/metabase.nomad.hcl
nomad job run /home/ubuntu/nomad_jobs/prefect.nomad.hcl
nomad job run /home/ubuntu/nomad_jobs/prefect_agent_worker.nomad.hcl

echo "Cloud Init Completed"
