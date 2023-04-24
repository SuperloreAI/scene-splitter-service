import falcon
import os
from google_cloud.gcp_storage import GoogleCloudStorage, check_bucket
from scenedetect import detect, ContentDetector, split_video_ffmpeg

class ClipScenesResource:
    def on_post(self, req, resp):
      """
      POST/clip-scenes
      req.media = {
        "videoUrl": "https://google-cloud-bucket.com/.../video.mp4",
        "assetID": "0000-0000-0000-0000"
      }
      """

      print("we about to get lit")
      try:
          # Read the request body as a JSON object
          json_body = req.media
          print(json_body)
      except Exception as e:
            print(f"Unexpected error: {e}")
            raise
          
      print(json_body)
      
      videoUrl = json_body['videoUrl']
      assetID = json_body['assetID']
      
      try:
          check_bucket(videoUrl)
          print("The URL matches one of the approved buckets")
      except ValueError as e:
          print("Error:", e)

      # download video from file
      local_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', assetID)
      os.makedirs(local_folder, exist_ok=True)
      gcs_instance = GoogleCloudStorage.instance()
      custom_file_name = f"{assetID}_video.mp4"
      content = gcs_instance.get_file_content(videoUrl, local_folder=local_folder, custom_file_name=custom_file_name)

      # clip the scenes
      print("Scene detection...")
      local_file = os.path.join(local_folder, custom_file_name)
      scene_list = detect(local_file, ContentDetector())
      print("Scenes...")
      print(scene_list)
      export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', assetID, "scenes")
      os.makedirs(export_dir, exist_ok=True)
      output_file_template = os.path.join(export_dir, f"{assetID}_video_scene_$SCENE_NUMBER.mp4")
      print("Splitting frames...")
      try:
        split_video_ffmpeg(
          local_file, 
          scene_list=scene_list,
          output_file_template=output_file_template
        )
      except Exception as e:
        print(e)
        print("ffmpeg output:", e.output)
      print("Finished splitting frames")

      # # upload the scenes
      # sample_bucket="superlore-video-sources-738437"
      # local_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')
      # sample_file = os.path.join(local_folder, "bitbunny.mp4")
      # gcs_instance = GoogleCloudStorage.instance()
      # content = gcs_instance.upload_file_content(sample_file, sample_bucket, "scene-detect/falcon-bitbunny.mp4")
      # print(content)

      # # delete the local files
      # print('deleting local files...')

      # # (optional) tell another service that the clips are done clipping
      # # or tell another service that it can vectorize the clips now
      # # ideally there is a central service responsible for the media_asset status updates
      
      resp.status = falcon.HTTP_200
      resp.content_type = 'text/plain'
      resp.text = 'Clip Scenes'
      
      # print("we can still do stuff after resp.")