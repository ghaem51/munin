import requests
import json
class slackAPIRequest:
    def __init__(self, url, auth=None, headers=None, params=None, data=None, verify=False):
        self.url = url
        self.auth = auth
        self.headers = headers
        self.params = params
        self.data = data
        self.verify = verify

    def sendAlert(self,text,username):
        response = requests.post(
            self.url,
            json.dumps({"text": text,"username":username})
        )
        return response