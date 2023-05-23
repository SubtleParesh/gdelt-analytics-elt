variable "instance_root_username" {
  description = "Instance Root Username"
  type        = string
  default     = "ubuntu"
}

variable "instance_size" {
  description = "Instance Size of azure vm"
  type        = string
  default     = "Standard_B2s"
}

variable "instance_big_size" {
  description = "Instance Size of azure vm"
  type        = string
  default     = "Standard_B4ms" //Standard_D4plds_v5
}

variable "master_vm" {
  description = "Instance Size of azure vm"
  type        = string
  default     = "master-vm"
}

variable "node_vm" {
  description = "Instance Size of azure vm"
  type        = string
  default     = "node-vm"
}

variable "resource_group_name" {
  description = "Instance Size of azure vm"
  type        = string
  default     = "lighthouse-resources"
}

variable "consul_version" {
  description = "Consul version"
  default     = "1.12.3"
}

variable "nomad_version" {
  description = "Nomad version"
  default     = "1.3.3"
}

variable "vault_version" {
  description = "Vault version"
  default     = "1.8.5"
}

variable "creds_output_path" {
  description = "Where to save the id_rsa config file. Should end in a forward slash `/` ."
  type        = string
  default     = "../"
}

variable "environment" {
  description = "Where to save the id_rsa config file. Should end in a forward slash `/` ."
  type        = string
  default     = "../"
}


variable "azure_creds" {
  type = object({
    subscription_id = string
    tenant_id       = string
  })
  sensitive = true
}
