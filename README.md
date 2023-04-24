# Scene Detect Microservice

## Setup

```bash
$ pip install -r requirements.txt
$ python src/app.py
```

## Todo

the individual parts are set up:
✅ http web server using falcon py & python 3.6 (required by PyDetectScene)
✅ google cloud auth to secret manager & storage bucket upload
✅ PyDetectScene + OpenCV works
✅ connect it all together into a single http post flow (individual parts all working)
✅ Upload scenes & frames to cloud storage with asset_ids
☑️ Delete local files
☑️ Send frames to postgres server (which also hits banana inference to vector embed the actual frames)
☑️ compile into prod release
☑️ add dockerfile and deploy to cloudrun