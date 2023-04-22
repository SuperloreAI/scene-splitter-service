# my_project/my_project/app.py
import falcon
import os
from wsgiref import simple_server
from dotenv import load_dotenv
from secret_manager import SecretManager, secret_name_app_backend
from google_cloud.gcp_storage import GoogleCloudStorage

from resources.download_video import DownloadVideoResource, UploadVideoResource
from resources.scene_detect import SceneDetectResource
from resources.clip_scenes import ClipScenesResource

# Load environment variables from the .env file
load_dotenv()

# Set the Google Cloud project ID
project_id = os.environ["PROJECT_ID"]

# Decode the base64-encoded service account key
base64_encoded_key = os.environ["GOOGLE_APPLICATION_CREDENTIALS_BASE64"]

# Create a Secret Manager instance
print('creating secret manager instance...')
secret_manager = SecretManager(project_id, base64_encoded_key)

# Initialize Google Cloud Storage
print('init google cloud storage...')
gcs_service_account_key_str = secret_manager.get_secret(secret_name_app_backend)
GoogleCloudStorage.initialize(project_id, gcs_service_account_key_str)


# Default response
def create_response(req, resp):
    resp.status = falcon.HTTP_200
    resp.content_type = 'text/plain'
    resp.text = 'Hello, world!'

# Start the server
app = falcon.App()
app.add_route('/', create_response)

# for testing purposes only
app.add_route('/test/download-video', DownloadVideoResource())
app.add_route('/test/upload-video', UploadVideoResource())
app.add_route('/test/scene-detect', SceneDetectResource())

# for real production
app.add_route('/clip-scenes', ClipScenesResource())

if __name__ == '__main__':
    with simple_server.make_server('0.0.0.0', 8000, app) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()
