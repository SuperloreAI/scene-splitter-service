
import os
import falcon
from google_cloud.gcp_storage import GoogleCloudStorage

class DownloadVideoResource:
    def on_get(self, req, resp):
        """Handles GET requests."""
        sample_bucket="superlore-video-sources-738437"
        sample_file="https://storage.googleapis.com/superlore-video-sources-738437/April%2019%20Bitbunny%203.mp4"
        local_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')
        gcs_instance = GoogleCloudStorage.instance()
        content = gcs_instance.get_file_content(sample_file, local_folder=local_folder)
        # Print the content
        print(content)
        # respond
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/plain'
        resp.text = 'Downloaded Resource'

class UploadVideoResource:
    def on_get(self, req, resp):
        """Handles GET requests."""
        sample_bucket="superlore-video-sources-738437"
        local_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')
        sample_file = os.path.join(local_folder, "bitbunny.mp4")
        gcs_instance = GoogleCloudStorage.instance()
        content = gcs_instance.upload_file_content(sample_file, sample_bucket, "scene-detect/falcon-bitbunny.mp4")
        # Print the content
        print(content)
        # respond
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/plain'
        resp.text = 'Uploaded Resource'