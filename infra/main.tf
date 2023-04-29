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

resource "azurerm_resource_group" "lighthouse" {
  name     = var.resource_group_name
  location = "Central India"
}

resource "azurerm_virtual_network" "lighthouse" {
  name                = "lighthouse-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.lighthouse.location
  resource_group_name = azurerm_resource_group.lighthouse.name
}

resource "azurerm_subnet" "lighthouse" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.lighthouse.name
  virtual_network_name = azurerm_virtual_network.lighthouse.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_public_ip" "lighthouse" {
  name                = "lighthouse_public_ip"
  resource_group_name = azurerm_resource_group.lighthouse.name
  location            = azurerm_resource_group.lighthouse.location
  allocation_method   = "Static"

  tags = {
    environment = "Production"
  }
}

resource "azurerm_network_interface" "lighthouse" {
  name                = "lighthouse-nic"
  location            = azurerm_resource_group.lighthouse.location
  resource_group_name = azurerm_resource_group.lighthouse.name

  ip_configuration {
    name                          = "lighthouse"
    subnet_id                     = azurerm_subnet.lighthouse.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.lighthouse.id
  }
}


resource "azurerm_network_security_group" "lighthouse" {
  name                = "lighthouse_nsg"
  location            = azurerm_resource_group.lighthouse.location
  resource_group_name = azurerm_resource_group.lighthouse.name

  # This port is enabled for file provisioning initially, needs to be restricted later
  # can be updated to only allow run machine ip address using tf functions
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

  # security_rule {
  #   name                       = "http"
  #   priority                   = 310
  #   direction                  = "Inbound"
  #   access                     = "Allow"
  #   protocol                   = "Tcp"
  #   source_port_range          = "*"
  #   destination_port_range     = "80"
  #   source_address_prefix      = "*"
  #   destination_address_prefix = "*"
  # }

  # security_rule {
  #   name                       = "https"
  #   priority                   = 320
  #   direction                  = "Inbound"
  #   access                     = "Allow"
  #   protocol                   = "Tcp"
  #   source_port_range          = "*"
  #   destination_port_range     = "443"
  #   source_address_prefix      = "*"
  #   destination_address_prefix = "*"
  # }


  # security_rule {
  #   name                       = "nomad"
  #   priority                   = 350
  #   direction                  = "Inbound"
  #   access                     = "Allow"
  #   protocol                   = "*"
  #   source_port_range          = "*"
  #   destination_port_range     = "4646"
  #   source_address_prefix      = "*"
  #   destination_address_prefix = "*"
  # }

  # security_rule {
  #   name                       = "traefik_http_web"
  #   priority                   = 360
  #   direction                  = "Inbound"
  #   access                     = "Allow"
  #   protocol                   = "*"
  #   source_port_range          = "*"
  #   destination_port_range     = "8080"
  #   source_address_prefix      = "*"
  #   destination_address_prefix = "*"
  # }

  # security_rule {
  #   name                       = "consul"
  #   priority                   = 380
  #   direction                  = "Inbound"
  #   access                     = "Allow"
  #   protocol                   = "*"
  #   source_port_range          = "*"
  #   destination_port_range     = "8500"
  #   source_address_prefix      = "*"
  #   destination_address_prefix = "*"
  # }


  # security_rule {
  #   name                       = "nomad_rpc"
  #   priority                   = 410
  #   direction                  = "Inbound"
  #   access                     = "Allow"
  #   protocol                   = "*"
  #   source_port_range          = "*"
  #   destination_port_range     = "4647"
  #   source_address_prefix      = "*"
  #   destination_address_prefix = "*"
  # }

  # security_rule {
  #   name                       = "nomad_serf"
  #   priority                   = 420
  #   direction                  = "Inbound"
  #   access                     = "Allow"
  #   protocol                   = "*"
  #   source_port_range          = "*"
  #   destination_port_range     = "4648"
  #   source_address_prefix      = "*"
  #   destination_address_prefix = "*"
  # }

  

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
  network_interface_id      = azurerm_network_interface.lighthouse.id
  network_security_group_id = azurerm_network_security_group.lighthouse.id
}

resource "azurerm_linux_virtual_machine" "lighthouse" {
  name                = var.instance_name
  resource_group_name = azurerm_resource_group.lighthouse.name
  location            = azurerm_resource_group.lighthouse.location
  size                = var.instance_size
  admin_username      = var.instance_root_username

  custom_data = base64encode(templatefile("${path.module}/scripts/vm_init.hcl.sh", {
    consul_version     = var.consul_version,
    nomad_version      = var.nomad_version,
    vault_version      = var.vault_version,
    datacenter         = "dc1",
    gossip_key         = random_id.consul_gossip_encryption_key.b64_std,
    master_token       = random_uuid.consul_master_token.result,
    agent_server_token = random_uuid.consul_agent_server_token.result,
    server_ip          = azurerm_public_ip.lighthouse.ip_address
  }))

  network_interface_ids = [
    azurerm_network_interface.lighthouse.id,
  ]                     

  admin_ssh_key {
    username   = var.instance_root_username
    public_key = tls_private_key.ssh.public_key_openssh
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS" // StandardSSD_LRS, Standard_LRS
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
    host        = azurerm_public_ip.lighthouse.ip_address
    private_key = tls_private_key.ssh.private_key_pem
  }

  provisioner "file" {
    source      = "${path.module}/configs/cloudinit"
    destination = "/home/${var.instance_root_username}/"
  }

  
  provisioner "file" {
    content = templatefile("${path.module}/configs/nomad.hcl.tpl", {
      master_token = random_uuid.consul_master_token.result,
      server_ip    = azurerm_public_ip.lighthouse.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/nomad.hcl"
  }


  provisioner "file" {
    content = templatefile("${path.module}/configs/consul.server.json.tpl", {
      server_ip = azurerm_public_ip.lighthouse.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/consul.server.json"
  }


  provisioner "file" {
    content = templatefile("${path.module}/configs/consul.agent.json.tpl", {
      server_ip = azurerm_public_ip.lighthouse.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/consul.agent.json"
  }


  provisioner "file" {
    content = templatefile("${path.module}/configs/netplan_config.tpl", {
      server_ip = azurerm_public_ip.lighthouse.ip_address
    })
    destination = "/home/${var.instance_root_username}/cloudinit/netplan_60-static.yaml"
  }
}
