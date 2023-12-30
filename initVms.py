from vcenterApi import vCenterAPIRequest
from netboxApi import netboxAPIRequest
from settings import *
from wazuhApi import wazuhAPIRequest
from apiCall import slackAPIRequest 
alert = slackAPIRequest(alert_webhook,verify=True)
try:
    vcenter = vCenterAPIRequest(vcenter_host, vcenter_user, vcenter_password)
    netbox = netboxAPIRequest(netbox_host, netbox_port, netbox_token)
    vcenter_sites = vcenter.get_sites()
    netbox_sites = netbox.get_sites()
    netbox_sites_names = {item['name'] for item in netbox_sites}
    vcenter_sites_not_in_netbox = [item for item in vcenter_sites if item.name not in netbox_sites_names]
    vcenter_sites_in_netbox = [item for item in vcenter_sites if item.name in netbox_sites_names]
    # create vcenter sites
    for vcenter_site in vcenter_sites_not_in_netbox:
        result = netbox.create_site(vcenter_site.name)
    # update netbox sites
    netbox_sites = netbox.get_sites()
    netbox_sites_names = {item['name'] for item in netbox_sites}
    # check vcenter sites vms

    netbox_vms = netbox.get_vms()
    netbox_vms_names = {item['name'] for item in netbox_vms}

    for vcenter_site in vcenter_sites_in_netbox:
        vcenter_vms = vcenter.get_vms_from_site(vcenter_site.name)
        vcenter_vms_not_in_netbox = [item for item in vcenter_vms if item.name not in netbox_vms_names]
        for vcenter_vm in vcenter_vms_not_in_netbox:
            netbox.create_vm_in_netbox_from_vcenter(vcenter_vm, vcenter_site.name)

    # check wazuh vms
    if (wazuh_check):
        try:
            wazuh = wazuhAPIRequest(wazuh_host,wazuh_host_port, wazuh_user, wazuh_password)
            wazuh_agents = wazuh.get_agents()
            netbox_vms = netbox.get_vms()
            netbox_vms_names = {item['name'] for item in netbox_vms}
            wazuh_vms_not_in_netbox = [item for item in wazuh_agents if item['name'] not in netbox_vms_names]
            netboxSites = netbox.get_sites()
            netbox_sites_names = {item['name'].replace("-DC", "") for item in netboxSites}
            for wazuh_agent in wazuh_vms_not_in_netbox:
                agentHardwareInfo = wazuh.get_agentHardwareInfo(wazuh_agent['id'])[0]
                agentNetInfo = wazuh.get_agentNetInfo(wazuh_agent['id'])
                if wazuh_agent['name'].split("-")[0] in netbox_sites_names:
                    print(wazuh_agent['name'])
                    netbox.create_vm_in_netbox_from_wazuh(wazuh_agent,agentHardwareInfo,agentNetInfo,wazuh_agent['name'].split("-")[0])
                else:
                    print(wazuh_agent['name'])
                    netbox.create_site(wazuh_agent['name'].split("-")[0]+'-DC')
                    netbox.create_vm_in_netbox_from_wazuh(wazuh_agent,agentHardwareInfo,agentNetInfo,wazuh_agent['name'].split("-")[0])
                
        except Exception as e:
            print(e)
except Exception as e:
    alert.sendAlert(f"{e}","netbox")