# google_cloud_storage.py
import json
import os
from google.oauth2 import service_account
from google.cloud import storage
from urllib.parse import urlparse, unquote
import requests

class GoogleCloudStorage:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def initialize(cls, project_id, service_account_key_str):
        instance = cls.instance()
        if hasattr(instance, "_initialized"):
            return
        print('init google cloud storage...')
        service_account_key = json.loads(service_account_key_str)
        print(service_account_key)
        instance.credentials = service_account.Credentials.from_service_account_info(service_account_key)
        instance.client = storage.Client(credentials=instance.credentials, project=project_id)
        instance._initialized = True

    def get_file_content(self, file_url, local_folder=None):
        response = requests.get(file_url)
        response.raise_for_status()

        if local_folder is not None:
            local_file_path = os.path.join(local_folder, os.path.basename(file_url))
            with open(local_file_path, "wb") as local_file:
                local_file.write(response.content)
            print(f"File saved to {local_file_path}")
        else:
            file_content = response.content
            return file_content

    def upload_file_content(self, local_file, bucket_name, upload_file_name):
        print("--- local_file ---")
        print(local_file)
        try:
          # Ensure the client is initialized
          if not hasattr(self, "_initialized"):
            raise RuntimeError("Google Cloud Storage client not initialized. Call initialize first.")
            
          # Get the bucket
          bucket = self.client.get_bucket(bucket_name)

          # Create a blob for the file
          blob = bucket.blob(upload_file_name)

          # Upload the file
          with open(local_file, "rb") as file_obj:
              blob.upload_from_file(file_obj)

          print(f"File uploaded to: gs://{bucket_name}/{upload_file_name}")

        except Exception as e:
            print(f"Error uploading file: {str(e)}")
