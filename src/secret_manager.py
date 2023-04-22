# secret_manager.py
import os
import base64
import json
from google.oauth2 import service_account
from google.cloud import secretmanager_v1 as secretmanager

class SecretManager:
    def __init__(self, project_id, base64_encoded_key):
        decoded_key = base64.b64decode(base64_encoded_key)
        print('secret manager decoded key...')
        print(decoded_key)
        service_account_key = json.loads(decoded_key)
        self.credentials = service_account.Credentials.from_service_account_info(service_account_key)
        self.client = secretmanager.SecretManagerServiceClient(credentials=self.credentials)
        self.project_id = project_id

    def get_secret(self, secret_name, version="latest"):
        secret_version_name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
        response = self.client.access_secret_version(request={"name": secret_version_name})
        secret_payload = response.payload.data.decode("UTF-8")
        print(secret_payload)
        return secret_payload


# secrets used in google cloud
secret_name_app_backend="App-Backend-Credentials"
secret_name_openai="openai"
secret_name_firebase="FirebaseConfig"
