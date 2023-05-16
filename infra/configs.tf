#############################
########    SSH     #########
##

resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_sensitive_file" "private_key" {
  content = tls_private_key.ssh.private_key_pem
  filename          = "${var.creds_output_path}/id_rsa"
}

resource "local_file" "public_key" {
  content  = tls_private_key.ssh.public_key_openssh
  filename = "${var.creds_output_path}/id_rsa.pub"
}

resource "random_uuid" "consul_master_token" {}
resource "random_uuid" "consul_agent_server_token" {}
resource "random_uuid" "consul_snapshot_token" {}

resource "random_id" "consul_gossip_encryption_key" {
  byte_length = 32
}
