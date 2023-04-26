import falcon
import os
from google_cloud.gcp_storage import GoogleCloudStorage, check_bucket, resize_with_aspect_ratio
from scenedetect import detect, ContentDetector, split_video_ffmpeg
import cv2
import shutil
import uuid
import requests

class ClipScenesResource:
    def on_post(self, req, resp):
      """
      POST/clip-scenes
      req.media = {
        "videoUrl": "https://google-cloud-bucket.com/.../video.mp4",
        "assetID": "0000-0000-0000-0000",
        "title": "Video Title"
      }
      """
      bucket_name = os.environ["CLOUD_BUCKET"]
      gcs_instance = GoogleCloudStorage.instance()

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
      title = json_body['title']
      
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
      gcs_instance.get_file_content(videoUrl, local_folder=local_folder, custom_file_name=custom_file_name)

      # clip the scenes
      print("Scene detection...")
      local_file = os.path.join(local_folder, custom_file_name)
      scene_list = detect(local_file, ContentDetector())
      num_scenes = len(scene_list)
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
      
      frames_save_db = [
        # { frame_asset_id, frame_url, scene_asset_id, scene_url, org_video_asset_id, org_video_url }
      ]

      for i in range(1, num_scenes+1):
        asset_id_scene = str(uuid.uuid4())
        scene_number = f"{i:03d}"
        scene_file = os.path.join(export_dir, f"{assetID}_video_scene_{scene_number}.mp4")
        print(scene_file)
        # upload to gbucket
        top_folder_level = f"https://storage.googleapis.com/{bucket_name}/original_video_{assetID}/"
        uploaded_scene_url = gcs_instance.upload_file_content(scene_file, bucket_name, f"original_video_{assetID}/scene_{scene_number}_asset_id_{asset_id_scene}.mp4")
        print("Uploaded content scene to google cloud bucket!")
        print(uploaded_scene_url)
        # Load the video using OpenCV
        cap = cv2.VideoCapture(scene_file)
        # Get the total number of frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"There are {total_frames} total frames")
        # Calculate the step size and generate equally spaced frame numbers
        step_size = total_frames // 4
        equally_spaced_frames = [step_size, step_size * 2, step_size * 3]
        # Create the output folder
        frame_output_dir = os.path.join(export_dir,f"{assetID}_video_scene_{scene_number}")
        print(f"Extracting frames to {frame_output_dir}")
        os.makedirs(frame_output_dir, exist_ok=True)
        # Create the frames
        for i, frame_num in enumerate(equally_spaced_frames):
            asset_id_frame = str(uuid.uuid4())
            print(f"Operating on frame {frame_num}")
            # Set the position in the video
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            # Read the frame
            ret, frame = cap.read()
            print(f"Reading frame...")
            print(ret)
            if ret:
                # resized_frame = resize_with_aspect_ratio(frame, 244)
                output_frame_path = f"{frame_output_dir}/frame_{i + 1}.png"
                print(f"Allegedly writing to {output_frame_path}")
                cv2.imwrite(output_frame_path, frame)
                # upload to cloud bucket
                uploaded_frame_url = gcs_instance.upload_file_content(output_frame_path, bucket_name, f"original_video_{assetID}/scene_{scene_number}_asset_id_{asset_id_scene}/frame_{i + 1}_asset_id_{asset_id_frame}.png")
                print("Uploaded content frame to google cloud bucket!")
                print(uploaded_frame_url)
                # save to database
                frames_save_db.append({
                  "frame_asset_id": asset_id_frame,
                  "frame_url": uploaded_frame_url,
                  "scene_asset_id": asset_id_scene,
                  "scene_url": uploaded_scene_url,
                  "original_asset_id": assetID,
                  "original_asset_url": videoUrl,
                  "top_folder_level": top_folder_level,
                  "title": title,
                })
                
      print(frames_save_db)
      
      # send to postgres
      postgres_db_url = os.environ["MAIN_DB_SERVER"]
      headers = {'Content-Type': 'application/json'}
      data = {
        "scenes": frames_save_db,
        "top_folder_level": top_folder_level,
        "title": title
      }
      response = requests.post(postgres_db_url, json=data, headers=headers)
      # Check the status code of the response
      if response.status_code == 200:
          print('Request was successful')
          print(response.json())  # Assuming the response is JSON
      else:
          print(f'Request failed with status code: {response.status_code}')
          print(response.text)

      # delete the local files
      if os.path.exists(local_folder):
        shutil.rmtree(local_folder)
        
      # response to finish
      resp.status = falcon.HTTP_200
      resp.content_type = 'text/plain'
      resp.text = 'Clip Scenes'
      
      # print("we can still do stuff after resp.")