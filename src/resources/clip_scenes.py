
class ClipScenesResource:
    def on_post(self, req, resp):

      # Return predicted output files path
      # not sure if code after this will still fire?
      # the caller is responsible for saving to database, while this scene-splitter-service handles long lived operations
      resp.status = falcon.HTTP_200
      resp.content_type = 'text/plain'
      resp.text = 'Scenes Detected'

      # download video from file
      sample_bucket="superlore-video-sources-738437"
      sample_file="https://storage.googleapis.com/superlore-video-sources-738437/April%2019%20Bitbunny%203.mp4"
      local_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')
      gcs_instance = GoogleCloudStorage.instance()
      content = gcs_instance.get_file_content(sample_file, local_folder=local_folder)

      # clip the scenes
      print("Scene detection...")
      local_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'bitbunny.mp4')
      print("Local file...")
      print(local_file)
      scene_list = detect(local_file, ContentDetector())
      print("Scenes...")
      print(scene_list)
      export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')
      output_file_template = os.path.join(export_dir, "scene-$SCENE_NUMBER.mp4")
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

      # upload the scenes
      sample_bucket="superlore-video-sources-738437"
      local_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')
      sample_file = os.path.join(local_folder, "bitbunny.mp4")
      gcs_instance = GoogleCloudStorage.instance()
      content = gcs_instance.upload_file_content(sample_file, sample_bucket, "scene-detect/falcon-bitbunny.mp4")
      print(content)

      # delete the local files
      print('deleting local files...')

      # (optional) tell another service that the clips are done clipping
      # or tell another service that it can vectorize the clips now
      # ideally there is a central service responsible for the media_asset status updates