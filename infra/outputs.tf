output "master_public_ip" {
  value       = azurerm_linux_virtual_machine.master.public_ip_address
  sensitive   = false
  description = "Azure Master VM - HQ Public IP"
}


output "master_private_ip" {
  value       = azurerm_linux_virtual_machine.master.private_ip_address
  sensitive   = false
  description = "Azure Master VM - HQ Private IP"
}

output "node_public_ip" {
  value       = azurerm_linux_virtual_machine.node.public_ip_address
  sensitive   = false
  description = "Azure Node VM - HQ Public IP"
}


output "node_private_ip" {
  value       = azurerm_linux_virtual_machine.node.private_ip_address
  sensitive   = false
  description = "Azure Node VM - HQ Private IP"
}
