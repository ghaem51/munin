import pynetbox
from pyVmomi import vim
from pprint import pprint

class netboxAPIRequest:
    def __init__(self, host, port, token, use_ssl=False):
        try:
            netbox = pynetbox.api(url=f"http://{host}:{port}", token=token)
            self.netbox = netbox
        except Exception as e:
            print(f"Failed to connect to NetBox: {str(e)}")
            return None
    def convert_to_slug(self, name):
        return name.lower().replace('/', '_').replace('.', '_').replace(' ', '-').replace('(', '').replace(')', '')
    def get_sites(self):
        try:
            # cluster_name = 'Your Cluster Name'  # Replace with the actual cluster name
            return self.netbox.dcim.sites.all()
        except Exception as e:
            print(f"Failed to get Sites in NetBox: {str(e)}")

    def get_vms(self):
        try:
            # cluster_name = 'Your Cluster Name'  # Replace with the actual cluster name
            return self.netbox.virtualization.virtual_machines.all()
        except Exception as e:
            print(f"Failed to get Sites in NetBox: {str(e)}")

    def get_or_add_platform(self, platform_name):
        try:
            try:
                filter_params = {
                    "name": platform_name
                }
                result = self.netbox.dcim.platforms.get(**filter_params)
                if (result == None):
                    platform = {
                        "name": platform_name,
                        "slug": self.convert_to_slug(platform_name)
                    }
                    return self.netbox.dcim.platforms.create(platform)
                else:
                    return result
            except Exception as e:
                print(f"Failed to get Platform in NetBox: {str(e)}")
                platform = {
                    "name": platform_name,
                    "slug": self.convert_to_slug(platform_name)
                }
                return self.netbox.dcim.platforms.create(platform)
        except Exception as e:
            print(f"Failed to add Platform to NetBox: {str(e)}")

    def create_vm_in_netbox_from_vcenter(self, vm, site_name):
        try:
            # cluster_name = 'Your Cluster Name'  # Replace with the actual cluster name
            filter_params = {
                "name": site_name
            }
            site = self.netbox.dcim.sites.get(**filter_params)
            # cluster = netbox.virtualization.clusters.get(name=cluster_name)
            # print(dir(site[0]))
            total_disk_capacity = 0
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualDisk):
                    total_disk_capacity += device.capacityInKB
            total_disk_capacity_gb = total_disk_capacity / 1024 / 1024
            platform = self.get_or_add_platform(vm.summary.config.guestFullName)
            vm_data = {
                "name": vm.name,
                "vcpus": vm.summary.config.numCpu,
                "memory": vm.summary.config.memorySizeMB,
                "status": "active",
                "disk": int(total_disk_capacity_gb),
                'site': site.id,
                "platform": platform.id
            }
            created_vm = self.netbox.virtualization.virtual_machines.create(vm_data)
            print(f"VM {created_vm.name} created in NetBox with ID: {created_vm.id}")
            device = self.netbox.dcim.devices.get(created_vm.id)
            # pprint(self.netbox.ipam.ip_addresses.all())
            # # Add VM IPs and interface information to NetBox
            for nic in vm.guest.net:
                interface_data = {
                    'name': nic.network,
                    'virtual_machine': created_vm.id,
                    'type': 'virtual',
                    'mac_address': nic.macAddress,
                    "enabled": True,
                    'description': 'Interface Description'  # Add any additional interface information
                }
                created_interface = self.netbox.virtualization.interfaces.create(interface_data)
                print(f"Interface {created_interface.name} created in NetBox for VM {created_vm.name}")
                for ip in nic.ipAddress:
                    ip_data = {
                        'address': ip,
                        'assigned_object_type' : 'virtualization.vminterface',
                        'assigned_object_id': created_interface.id
                    }
                    self.netbox.ipam.ip_addresses.create(ip_data)
                    print(f"IP {ip} added to NetBox for Interface {created_interface.name}")

        except Exception as e:
            print(f"Failed to create VM in NetBox: {str(e)}")
    
    def create_vm_in_netbox_from_wazuh(self, agentInfo,agentHardwareInfo,agentNetInfo, site_name):
        try:
            cluster_name = 'Your Cluster Name'  # Replace with the actual cluster name
            filter_params = {
                "name": site_name+'-DC'
            }
            print(site_name)
            site = self.netbox.dcim.sites.get(**filter_params)
            platform = self.get_or_add_platform(agentInfo['os']['name'])
            vm_data = {
                "name": agentInfo['name'],
                "vcpus": agentHardwareInfo['cpu']['cores'],
                "memory": agentHardwareInfo['ram']['total'],
                "status": "active",
                'site': site.id,
                "platform": platform.id
            }
            created_vm = self.netbox.virtualization.virtual_machines.create(vm_data)
            print(f"VM {created_vm.name} created in NetBox with ID: {created_vm.id}")
            device = self.netbox.dcim.devices.get(created_vm.id)
            # pprint(self.netbox.ipam.ip_addresses.all())
            # # Add VM IPs and interface information to NetBox
            for nic in agentNetInfo:
                if nic['mac'][-1] == ":":
                    nic['mac'] = nic['mac'][:-1]
                interface_data = {
                    'name': nic['name'],
                    'virtual_machine': created_vm.id,
                    'type': 'virtual',
                    'mac_address': nic['mac'],
                    "enabled": True,
                    'description': 'Interface Description'  # Add any additional interface information
                }
                created_interface = self.netbox.virtualization.interfaces.create(interface_data)
                print(f"Interface {created_interface.name} created in NetBox for VM {created_vm.name}")
                ip_data = {
                    'address': agentInfo['ip']+'/32',
                    'assigned_object_type' : 'virtualization.vminterface',
                    'assigned_object_id': created_interface.id
                }
                self.netbox.ipam.ip_addresses.create(ip_data)
                print(f"IP {agentInfo['ip']+'/32'} added to NetBox for Interface {created_interface.name}")

        except Exception as e:
            print(f"Failed to create VM in NetBox: {str(e)}")

    def create_site(self, vm_site_name):
        site_data = {
            "name": vm_site_name,
            "slug": vm_site_name.lower().replace(' ', '-').replace('.','_'),
            "status": "active",
            # Add other attributes as needed
        }
        site = self.netbox.dcim.sites.create(site_data)
        print(f"Site '{site.name}' created successfully.")
        return site
        
    # Example usage
    