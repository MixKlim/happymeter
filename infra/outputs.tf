output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "location" {
  value = azurerm_resource_group.rg.location
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "acr_name" {
  value = azurerm_container_registry.acr.name
}

output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.law.id
}

output "storage_account_name" {
  value = azurerm_storage_account.sa.name
}

output "storage_share_name" {
  value = azurerm_storage_share.share.name
}

output "container_app_environment_id" {
  value = azurerm_container_app_environment.env.id
}

output "backend_fqdn" {
  value = azurerm_container_app.backend.latest_revision_fqdn
}

output "frontend_fqdn" {
  value = azurerm_container_app.frontend.latest_revision_fqdn
}
