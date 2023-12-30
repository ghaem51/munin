from pyVim.connect import SmartConnectNoSSL
from pyVmomi import vim

class vCenterAPIRequest:
    def __init__(self, host, user, password):
        try:
            service_instance = SmartConnectNoSSL(
                host=host,
                user=user,
                pwd=password
            )
            self.content = service_instance.RetrieveContent()
        except Exception as e:
            print(f"Failed to connect to vCenter: {str(e)}")
            return None
    def get_all_vms(self):
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder,
            [vim.VirtualMachine],
            True
        )
        vms = container.view
        container.Destroy()
        return vms
    
    def get_vms_from_site(self,site_name):
        if not hasattr(self, 'sites'):
            self.sites = self.get_sites()
        # Find the specified site
        site = next((s for s in self.sites if s.name == site_name), None)
        if not site:
            print(f"Site {site_name} not found")
            return None
        container = site.vmFolder
        view_type = [vim.VirtualMachine]
        recursive = True
        vm_view = self.content.viewManager.CreateContainerView(
            container, view_type, recursive
        )

        vms = vm_view.view
        vm_view.Destroy()
        return vms

    def get_sites(self):
        container = self.content.rootFolder
        view_type = [vim.Datacenter]
        recursive = True
        dc_view = self.content.viewManager.CreateContainerView(
            container, view_type, recursive
        )
        sites = dc_view.view
        dc_view.Destroy()
        self.sites = sites
        return sites
