import requests

class wazuhAPIRequest:
    def __init__(self, host, port, user, password, use_ssl=False):
        try:
            self.host = host
            self.port = port
            self.use_ssl = use_ssl
            if (not use_ssl):
                import urllib3
                urllib3.disable_warnings()
            token = requests.get(url=f'https://{host}:{port}/security/user/authenticate', auth=(user, password), verify=use_ssl)
            self.token = token.json()['data']['token']
        except Exception as e:
            print(f"Failed to connect to wazuhMaster: {str(e)}")
            return None    
    # Example usage
    def get_agents(self):
        return requests.get(url=f'https://{self.host}:{self.port}/agents', headers={"Authorization": f"Bearer {self.token}"},verify=self.use_ssl).json()['data']['affected_items']
    def get_agentHardwareInfo(self,id):
        return requests.get(url=f'https://{self.host}:{self.port}/syscollector/{id}/hardware', headers={"Authorization": f"Bearer {self.token}"},verify=self.use_ssl).json()['data']['affected_items']
    def get_agentNetInfo(self,id):
        return requests.get(url=f'https://{self.host}:{self.port}/syscollector/{id}/netiface', headers={"Authorization": f"Bearer {self.token}"},verify=self.use_ssl).json()['data']['affected_items']