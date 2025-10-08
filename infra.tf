terraform {
  required_providers {
    azurerm = {
      source  = "azurerm"
      version = "4.40.0"
    }
  }
}
provider "azurerm" {
  features {}
}
resource "azurerm_managed_disk" "res-0" {
  create_option                     = "FromImage"
  disk_access_id                    = ""
  disk_encryption_set_id            = ""
  disk_iops_read_only               = 0
  disk_iops_read_write              = 500
  disk_mbps_read_only               = 0
  disk_mbps_read_write              = 60
  disk_size_gb                      = 30
  edge_zone                         = ""
  gallery_image_reference_id        = ""
  hyper_v_generation                = "V2"
  image_reference_id                = "/Subscriptions/6a89954b-4a58-4fef-ab89-2414bad6272d/Providers/Microsoft.Compute/Locations/westeurope/Publishers/canonical/ArtifactTypes/VMImage/Offers/0001-com-ubuntu-server-jammy/Skus/22_04-lts-gen2/Versions/22.04.202507300"
  location                          = "westeurope"
  max_shares                        = 0
  name                              = "escapegame1_OsDisk_1_4fcd31bb0d6f43f5a3c5c2894648f597"
  network_access_policy             = "AllowAll"
  on_demand_bursting_enabled        = false
  optimized_frequent_attach_enabled = false
  os_type                           = "Linux"
  performance_plus_enabled          = false
  public_network_access_enabled     = true
  resource_group_name               = "ESCAPEGAME"
  secure_vm_disk_encryption_set_id  = ""
  security_type                     = ""
  source_resource_id                = ""
  source_uri                        = ""
  storage_account_id                = ""
  storage_account_type              = "Standard_LRS"
  tags                              = {}
  tier                              = ""
  trusted_launch_enabled            = true
  upload_size_bytes                 = 0
  zone                              = "3"
}

resource "azurerm_linux_virtual_machine" "res-5" {
  admin_password                                         = "" # Masked sensitive attribute
  admin_username                                         = "azureuser"
  allow_extension_operations                             = true
  availability_set_id                                    = ""
  bypass_platform_safety_checks_on_user_schedule_enabled = false
  capacity_reservation_group_id                          = ""
  computer_name                                          = "escapegame1"
  custom_data                                            = "" # Masked sensitive attribute
  dedicated_host_group_id                                = ""
  dedicated_host_id                                      = ""
  disable_password_authentication                        = true
  disk_controller_type                                   = "SCSI"
  edge_zone                                              = ""
  encryption_at_host_enabled                             = false
  eviction_policy                                        = ""
  extensions_time_budget                                 = "PT1H30M"
  license_type                                           = ""
  location                                               = "westeurope"
  max_bid_price                                          = -1
  name                                                   = "escapegame1"
  network_interface_ids                                  = [azurerm_network_interface.res-7.id]
  patch_assessment_mode                                  = "ImageDefault"
  patch_mode                                             = "AutomaticByPlatform"
  platform_fault_domain                                  = -1
  priority                                               = "Regular"
  provision_vm_agent                                     = true
  proximity_placement_group_id                           = ""
  reboot_setting                                         = "IfRequired"
  resource_group_name                                    = "EscapeGame"
  secure_boot_enabled                                    = true
  size                                                   = "Standard_D4s_v3"
  source_image_id                                        = ""
  tags                                                   = {}
  user_data                                              = ""
  virtual_machine_scale_set_id                           = ""
  vm_agent_platform_updates_enabled                      = false
  vtpm_enabled                                           = true
  zone                                                   = "3"
  additional_capabilities {
    hibernation_enabled = false
    ultra_ssd_enabled   = false
  }
  boot_diagnostics {
    storage_account_uri = ""
  }
  identity {
    identity_ids = []
    type         = "SystemAssigned"
  }
  os_disk {
    caching                          = "ReadWrite"
    disk_encryption_set_id           = ""
    disk_size_gb                     = 30
    name                             = "escapegame1_OsDisk_1_4fcd31bb0d6f43f5a3c5c2894648f597"
    secure_vm_disk_encryption_set_id = ""
    security_encryption_type         = ""
    storage_account_type             = "Standard_LRS"
    write_accelerator_enabled        = false
  }
  source_image_reference {
    offer     = "0001-com-ubuntu-server-jammy"
    publisher = "canonical"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }
}
resource "azurerm_bastion_host" "res-6" {
  copy_paste_enabled        = true
  file_copy_enabled         = false
  ip_connect_enabled        = false
  kerberos_enabled          = false
  location                  = "westeurope"
  name                      = "EscapGame-bastion"
  resource_group_name       = "EscapeGame"
  scale_units               = 2
  session_recording_enabled = false
  shareable_link_enabled    = false
  sku                       = "Developer"
  tags                      = {}
  tunneling_enabled         = false
  virtual_network_id        = azurerm_virtual_network.res-10.id
  zones                     = []
}
resource "azurerm_network_interface" "res-7" {
  accelerated_networking_enabled = false
  auxiliary_mode                 = ""
  auxiliary_sku                  = ""
  dns_servers                    = []
  edge_zone                      = ""
  internal_dns_name_label        = ""
  ip_forwarding_enabled          = false
  location                       = "westeurope"
  name                           = "escapegame1204-b6da4c5d"
  resource_group_name            = "EscapeGame"
  tags                           = {}
  ip_configuration {
    gateway_load_balancer_frontend_ip_configuration_id = ""
    name                                               = "escapegame1204-defaultIpConfiguration"
    primary                                            = true
    private_ip_address                                 = "10.0.0.4"
    private_ip_address_allocation                      = "Dynamic"
    private_ip_address_version                         = "IPv4"
    public_ip_address_id                               = azurerm_public_ip.res-9.id
    subnet_id                                          = "/subscriptions/6a89954b-4a58-4fef-ab89-2414bad6272d/resourceGroups/EscapeGame/providers/Microsoft.Network/virtualNetworks/EscapGame/subnets/default"
  }
}
resource "azurerm_network_security_group" "res-8" {
  location            = "westeurope"
  name                = "escapegame1-nsg"
  resource_group_name = "EscapeGame"
  security_rule = [{
    access                                     = "Allow"
    description                                = ""
    destination_address_prefix                 = "*"
    destination_address_prefixes               = []
    destination_application_security_group_ids = []
    destination_port_range                     = "22"
    destination_port_ranges                    = []
    direction                                  = "Inbound"
    name                                       = "SSH"
    priority                                   = 300
    protocol                                   = "Tcp"
    source_address_prefix                      = "*"
    source_address_prefixes                    = []
    source_application_security_group_ids      = []
    source_port_range                          = "*"
    source_port_ranges                         = []
  }]
  tags = {}
}
resource "azurerm_public_ip" "res-9" {
  allocation_method       = "Static"
  ddos_protection_mode    = "VirtualNetworkInherited"
  edge_zone               = ""
  idle_timeout_in_minutes = 15
  ip_tags                 = {}
  ip_version              = "IPv4"
  location                = "westeurope"
  name                    = "escapegame1-ip-b6da4c5d"
  resource_group_name     = "EscapeGame"
  sku                     = "Standard"
  sku_tier                = "Regional"
  tags                    = {}
  zones                   = ["3"]
}
resource "azurerm_virtual_network" "res-10" {
  address_space                  = ["10.0.0.0/16"]
  bgp_community                  = ""
  dns_servers                    = []
  edge_zone                      = ""
  flow_timeout_in_minutes        = 0
  location                       = "westeurope"
  name                           = "EscapGame"
  private_endpoint_vnet_policies = "Disabled"
  resource_group_name            = "EscapeGame"
  subnet = [{
    address_prefixes                              = ["10.0.0.0/24"]
    default_outbound_access_enabled               = false
    delegation                                    = []
    id                                            = "/subscriptions/6a89954b-4a58-4fef-ab89-2414bad6272d/resourceGroups/EscapeGame/providers/Microsoft.Network/virtualNetworks/EscapGame/subnets/default"
    name                                          = "default"
    private_endpoint_network_policies             = "Disabled"
    private_link_service_network_policies_enabled = true
    route_table_id                                = ""
    security_group                                = ""
    service_endpoint_policy_ids                   = []
    service_endpoints                             = []
  }]
  tags = {}
}
resource "azurerm_network_interface_security_group_association" "res-11" {
  network_interface_id      = azurerm_network_interface.res-7.id
  network_security_group_id = azurerm_network_security_group.res-8.id
}