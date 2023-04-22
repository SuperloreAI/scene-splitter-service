import os
import falcon
import subprocess
from scenedetect import detect, ContentDetector, split_video_ffmpeg
import logging
logging.basicConfig(level=logging.DEBUG)


class SceneDetectResource:
    def on_get(self, req, resp):
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
      # try:
      #     split_video_ffmpeg_custom(
      #         local_file,
      #         scene_list=scene_list,
      #         output_file_template=export_dir + "/scene-$SCENE_NUMBER.mp4"
      #     )
      # except Exception as e:
      #     print(e)

      print("Finished splitting frames")
      # Scenes Detected!
      resp.status = falcon.HTTP_200
      resp.content_type = 'text/plain'
      resp.text = 'Scenes Detected'



# def split_video_ffmpeg_custom(input_video, scene_list, output_file_template):
#     for idx, (start, end) in enumerate(scene_list):
#         command = [
#             "ffmpeg",
#             "-y",  # Overwrite output files without asking.
#             "-i", input_video,
#             "-ss", str(start.get_seconds()),
#             "-to", str(end.get_seconds()),
#             "-codec", "copy",
#             output_file_template.replace("$SCENE_NUMBER", str(idx + 1)),
#         ]

#         print("Running command:", " ".join(command))
#         process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#         stdout, stderr = process.communicate()
#         return_code = process.returncode

#         if return_code != 0:
#             print("ffmpeg command failed with return code:", return_code)
#             print("stdout:", stdout)
#             print("stderr:", stderr)
#             break