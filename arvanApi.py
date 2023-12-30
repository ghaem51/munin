import requests

# ArvanCloud API endpoint for getting VM data
api_url = 'https://napi.arvancloud.ir/ecc/v2/datacenters'

# API token for authentication
api_token = 'arvan api token'

def get_vm_data():
    headers = {
        'Apikey': f'{api_token}'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        vm_data = response.json()
        return vm_data['data']
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

# Call the function to get the VM data
vm_data = get_vm_data()
for vm in vm_data:
    print(vm)

else:
    print('Failed to retrieve VM data.')