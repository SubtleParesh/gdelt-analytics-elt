#!/usr/bin/env bash
sleep 3m
echo "Cloud Init Started - randomCode=dc1dfasdwd12d"
# sudo chmod +x /home/ubuntu/slack-server-notify
/home/ubuntu/slack-server-notify server LIGHTHOUSE\ Cloud\ Init\ Started\ :arrow_up:

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

sudo apt-get update
# System Tools
sudo apt-get install -y unzip tree redis-tools jq curl tmux git resolvconf


# sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release git


# Docker Installation
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose
      
# Java
sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-get update 
sudo apt-get install -y openjdk-8-jdk
JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")

# Hashicorp 
# Install package

curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update
sudo apt-get install -y consul
sudo apt-get install -y nomad
sudo apt-get install -y vault

echo "Installing jq"
curl --silent -Lo /bin/jq https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64
sudo chmod +x /bin/jq

echo "Configuring system time"
timedatectl set-timezone UTC

# Adds public ip to configuration


# ****************************************************************
# CONFIG FILES
# ****************************************************************


sudo mkdir /etc/consul.d.server
sudo mkdir /etc/consul.d
sudo mkdir /etc/nomad.d
sudo mkdir /etc/traefik

sudo cp /home/ubuntu/cloudinit/consul.server.json /etc/consul.d.server/consul.json
sudo cp /home/ubuntu/cloudinit/consul.agent.json /etc/consul.d/consul.json
sudo cp /home/ubuntu/cloudinit/consul.service /etc/systemd/system/consul.service
sudo cp /home/ubuntu/cloudinit/nomad.hcl /etc/nomad.d/nomad.hcl
sudo cp /home/ubuntu/cloudinit/traefik.yml /etc/traefik/traefik.yml
sudo cp /home/ubuntu/cloudinit/traefikConfig.yml /etc/traefik/traefikConfig.yml
sudo cp /home/ubuntu/cloudinit/traefik.service /etc/systemd/system/traefik.service
sudo cp /home/ubuntu/cloudinit/netplan_60-static.yaml /etc/netplan/60-static.yaml
sudo cp /home/ubuntu/cloudinit/daemon.json /etc/docker/daemon.json

sudo chmod 600 /etc/traefik/acme.json
mkdir /home/nomad
mkdir /home/nomad/job-volumes

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

sleep 60

sudo chown -R nomad:nomad /etc/nomad.d
sudo chmod -R 640 /etc/nomad.d/*

sudo systemctl enable nomad
sudo systemctl start nomad

cd /home/ubuntu
mkdir traefik
cd traefik
wget -q https://github.com/traefik/traefik/releases/download/v2.6.1/traefik_v2.6.1_linux_amd64.tar.gz
tar -zxvf traefik_v2.6.1_linux_amd64.tar.gz

mkdir /etc/traefik

sudo systemctl enable traefik
sudo systemctl start traefik


echo "Cloud Init Completed"
