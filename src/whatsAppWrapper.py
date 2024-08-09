import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()

class WHAPIClient:
    def __init__(self):
        self.WHAPI_URL = os.environ.get("WHAPI_URL")
        self.WHAPI_token = os.environ.get("WHAPI_token")

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.WHAPI_token}",
            "Content-Type": "application/json"
        }

    def get_messages_from_group(self, group_id):
        url = f"{self.WHAPI_URL}/messages/list/{group_id}"  # Replace with the actual endpoint
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code == 200:
            return response.json()  # Assuming the response is JSON
        else:
            response.raise_for_status()

    def save_messages_to_file(self, group_id, file_name):
        messages = self.get_messages_from_group(group_id)

        with open(file_name, 'w') as file:
            json.dump(messages, file, indent=4)

