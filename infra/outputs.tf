
output "azure_vm_ip" {
  value       = azurerm_public_ip.lighthouse.ip_address
  sensitive   = false
  description = "Azure VM - HQ IP"
}