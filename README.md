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
☑️ compile into prod release
☑️ add dockerfile and deploy to cloudrun