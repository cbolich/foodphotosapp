import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import asyncio

asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

#url = "https://b26f8865141710f62b.gradio.live/sdapi/v1/txt2img" 
url = "http://192.168.1.158:7860/sdapi/v1/txt2img"

payload = {
    "prompt": "sushi on a black plate",
    "steps": 5
}


#response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
response = requests.post(url, json=payload)

r = response.json()

# receive generate images back and save 
for i in r['images']:
	image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
	image.save('output.png')

'''
    png_payload = {
        "image": "data:image/png;base64," + i
    }
    response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", response2.json().get("info"))
    image.save('output.png', pnginfo=pnginfo)
'''

