terraform {
  required_version = ">= 0.14.9"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.46.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "${var.azure_creds.subscription_id}"
  tenant_id       = "${var.azure_creds.tenant_id}"
  skip_provider_registration = true
}

resource "azurerm_resource_group" "master" {
  name     = var.resource_group_name
  location = "Central India"
}

resource "azurerm_virtual_network" "master" {
  name                = "master-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.master.location
  resource_group_name = azurerm_resource_group.master.name
}

resource "azurerm_subnet" "master" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.master.name
  virtual_network_name = azurerm_virtual_network.master.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_public_ip" "master" {
  name                = "master_public_ip"
  resource_group_name = azurerm_resource_group.master.name
  location            = azurerm_resource_group.master.location
  allocation_method   = "Static"
  domain_name_label = "gdelt-analytics"

  tags = {
    environment = "Production"
  }
}

resource "azurerm_network_interface" "master" {
  name                = "master-nic"
  location            = azurerm_resource_group.master.location
  resource_group_name = azurerm_resource_group.master.name

  ip_configuration {
    name                          = "master"
    subnet_id                     = azurerm_subnet.master.id
    private_ip_address_allocation = "Static"
    public_ip_address_id          = azurerm_public_ip.master.id
    private_ip_address            = "10.0.2.5"
  }
}


resource "azurerm_network_security_group" "master" {
  name                = "master_nsg"
  location            = azurerm_resource_group.master.location
  resource_group_name = azurerm_resource_group.master.name

  # This port is enabled for file provisioning initially, needs to be restricted later
  # can be updated to only allow run machine ip address using tf functions

  security_rule {
    name                       = "allow_internal"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "10.0.2.0/24"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "ssh"
    priority                   = 300
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "http"
    priority                   = 310
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "nomad"
    priority                   = 350
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "4646"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "traefik_http_web"
    priority                   = 360
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "consul"
    priority                   = 380
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "8500"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "minio"
    priority                   = 390
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "39090"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "minio_api"
    priority                   = 392
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "39191"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "clickhouse"
    priority                   = 395
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "38123"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }


  security_rule {
    name                       = "prefect"
    priority                   = 400
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "4200"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "metabase"
    priority                   = 410
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "3000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "ping"
    priority                   = 440
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "ICMP"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    environment = "Production"
  }
}

resource "azurerm_network_interface_security_group_association" "main" {
  network_interface_id      = azurerm_network_interface.master.id
  network_security_group_id = azurerm_network_security_group.master.id
}

resource "azurerm_linux_virtual_machine" "master" {
  name                = var.master_vm
  resource_group_name = azurerm_resource_group.master.name
  location            = azurerm_resource_group.master.location
  size                = var.instance_size
  admin_username      = var.instance_root_username

  custom_data = base64encode(templatefile("${path.module}/scripts/cloud_init_master.hcl.sh", {
    consul_version     = var.consul_version,
    nomad_version      = var.nomad_version,
    vault_version      = var.vault_version,
    datacenter         = "dc1",
    gossip_key         = random_id.consul_gossip_encryption_key.b64_std,
    master_token       = random_uuid.consul_master_token.result,
    agent_server_token = random_uuid.consul_agent_server_token.result,
    server_ip          = azurerm_public_ip.master.ip_address
  }))

  network_interface_ids = [
    azurerm_network_interface.master.id,
  ]

  admin_ssh_key {
    username   = var.instance_root_username
    public_key = tls_private_key.ssh.public_key_openssh
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS" // StandardSSD_LRS, Standard_LRS
    disk_size_gb = "64"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  connection {
    type        = "ssh"
    user        =  var.instance_root_username
    host        = azurerm_public_ip.master.ip_address
    private_key = tls_private_key.ssh.private_key_pem
  }

  provisioner "file" {
    source      = "${path.module}/configs/master/cloudinit"
    destination = "/home/${var.instance_root_username}/"
  }

  provisioner "file" {
      source      = "${path.module}/nomad_jobs"
      destination = "/home/${var.instance_root_username}/"
    }


  provisioner "file" {
    content = templatefile("${path.module}/configs/master/nomad.hcl.tpl", {
      master_token = random_uuid.consul_master_token.result,
      server_ip    = azurerm_public_ip.master.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/nomad.hcl"
  }


  provisioner "file" {
    content = templatefile("${path.module}/configs/master/consul.server.json.tpl", {
      server_ip = azurerm_public_ip.master.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/consul.server.json"
  }


  provisioner "file" {
    content = templatefile("${path.module}/configs/master/consul.agent.json.tpl", {
      server_ip = azurerm_public_ip.master.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/consul.agent.json"
  }


  provisioner "file" {
    content = templatefile("${path.module}/configs/master/netplan_config.tpl", {
      server_ip = azurerm_public_ip.master.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/netplan_60-static.yaml"
  }
}

resource "azurerm_public_ip" "node" {
  name                = "node_public_ip"
  resource_group_name = azurerm_resource_group.master.name
  location            = azurerm_resource_group.master.location
  allocation_method   = "Static"
}


resource "azurerm_network_interface" "node" {
  name                = "node-nic"
  location            = azurerm_resource_group.master.location
  resource_group_name = azurerm_resource_group.master.name

  ip_configuration {
    name                          = "node"
    subnet_id                     = azurerm_subnet.master.id
    private_ip_address_allocation = "Static"
    public_ip_address_id          = azurerm_public_ip.node.id
    private_ip_address            = "10.0.2.6"
  }
}

resource "azurerm_network_interface_security_group_association" "node_nisg" {
  network_interface_id      = azurerm_network_interface.node.id
  network_security_group_id = azurerm_network_security_group.master.id
}

resource "azurerm_linux_virtual_machine" "node" {
  name                = var.node_vm
  resource_group_name = azurerm_resource_group.master.name
  location            = azurerm_resource_group.master.location
  size                = var.instance_size
  admin_username      = var.instance_root_username

  custom_data = base64encode(templatefile("${path.module}/scripts/cloud_init_node.hcl.sh", {
    consul_version     = var.consul_version,
    nomad_version      = var.nomad_version,
    vault_version      = var.vault_version,
    datacenter         = "dc1",
    gossip_key         = random_id.consul_gossip_encryption_key.b64_std,
    master_token       = random_uuid.consul_master_token.result,
    agent_server_token = random_uuid.consul_agent_server_token.result,
    master_ip          = azurerm_public_ip.master.ip_address
  }))

  network_interface_ids = [
    azurerm_network_interface.node.id,
  ]

  admin_ssh_key {
    username   = var.instance_root_username
    public_key = tls_private_key.ssh.public_key_openssh
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS" // StandardSSD_LRS, Standard_LRS
    disk_size_gb = "30"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  connection {
    type        = "ssh"
    user        =  var.instance_root_username
    host        =  azurerm_public_ip.node.ip_address
    private_key =  tls_private_key.ssh.private_key_pem
  }

  provisioner "file" {
    source      = "${path.module}/configs/master/cloudinit"
    destination = "/home/${var.instance_root_username}/"
  }

  provisioner "file" {
      source      = "${path.module}/nomad_jobs"
      destination = "/home/${var.instance_root_username}/"
    }


  provisioner "file" {
    content = templatefile("${path.module}/configs/node/nomad.agent.hcl.tpl", {
      master_token = random_uuid.consul_master_token.result,
      server_ip    = azurerm_public_ip.node.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/nomad.hcl"
  }


  provisioner "file" {
    content = templatefile("${path.module}/configs/node/consul.agent.json.tpl", {
      server_ip = azurerm_public_ip.node.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/consul.agent.json"
  }


  provisioner "file" {
    content = templatefile("${path.module}/configs/node/netplan_config.tpl", {
      server_ip = azurerm_public_ip.node.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/netplan_60-static.yaml"
  }
}
