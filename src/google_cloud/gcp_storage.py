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

    def get_file_content(self, file_url, local_folder=None, custom_file_name=None):
        response = requests.get(file_url)
        response.raise_for_status()

        if local_folder is not None:
            file_name = custom_file_name if custom_file_name else os.path.basename(file_url)
            local_file_path = os.path.join(local_folder, file_name)
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


import re
from urllib.parse import urlparse

def check_bucket(url_string):
    approved_buckets = ["superlore-video-sources-738437"]
    parsed_url = urlparse(url_string)

    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError("Invalid URL")

    if parsed_url.scheme != 'https' or parsed_url.netloc != 'storage.googleapis.com':
        raise ValueError("URL is not a Google Cloud Storage URL")

    match = re.match(r'^/([^/]+)/', parsed_url.path)
    if not match:
        raise ValueError("Invalid Google Cloud Storage path")

    bucket = match.group(1)
    if bucket not in approved_buckets:
        raise ValueError("URL does not belong to any of the approved buckets")

    return True
