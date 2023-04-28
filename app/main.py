from fastapi import FastAPI, Body, Request, Response, HTTPException, status
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from typing import List
from models import Downloads, UserRequest
from queuing import queuing_function, get_queue_status
import asyncio
import json
import requests
import io
import os
import base64
from PIL import Image, PngImagePlugin
from datetime import datetime

app = FastAPI()

"""SET UP / MISC """
@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb+srv://jfrabut2:yCHemjm0O8FEbDt3@foodphotosapp.4vgexei.mongodb.net/?retryWrites=true&w=majority")
    app.database = app.mongodb_client["fpa"]

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

# This is a helper function that I found was needed sometimes
def document_to_model(document: dict) -> Downloads:
    document["_id"] = str(document["_id"])
    return Downloads(**document)


"""ROUTES"""
@app.get("/", response_description="Home")
def home(request: Request):
    return {"message": "Welcome home"}


# main image generation route
@app.post("/gen", response_description="Generate photos")
async def generate(request: Request, userRequest: UserRequest):
    # get prompt and other parameters from user
    user_request_dict = userRequest.dict()
    print(user_request_dict)
    
    # log the user request
    app.database.requests.insert_one(user_request_dict)

    # Process the results

    # improve prompt

    # choose relevant pose
    tmp = app.database.poses.find_one({"tags": user_request_dict["pose"]})
    pose = tmp["img"]
    img_base64 = base64.b64encode(pose).decode('utf-8')
    print(tmp["filename"])
    

    # prepare settings
    control_net_payload = {
        "enable_hr": 0,
        "denoising_strength": 0,
        "firstphase_width": 0,
        "firstphase_height": 0,
        "hr_scale": 2,
        "hr_second_pass_steps": 0,
        "hr_resize_x": 0,
        "hr_resize_y": 0,
        "prompt": "user_request_dict[\"prompt\"]",
        "styles": [
            "string"
        ],
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 50,
        "cfg_scale": 7,
        "width": 512,
        "height": 512,
        "restore_faces": 0,
        "tiling": 0,
        "do_not_save_samples": 0,
        "do_not_save_grid": 0,
        "negative_prompt": "blurry, low quality, animated, cartoon, silverware, fork, knife, spoon, chopsticks,",
        "eta": 0,
        "s_churn": 0,
        "s_tmax": 0,
        "s_tmin": 0,
        "s_noise": 1,
        "override_settings": {},
        "override_settings_restore_afterwards": 1,
        "script_args": [],
        "sampler_index": "Euler",
        "send_images": 1,
        "save_images": 0,
        "alwayson_scripts": {},
        "controlnet_units": [
                {
                    "input_image": "img_base64",
                    "mask": "",
                    "module": "canny",
                    "model": "control_sd15_canny",
                    "weight": 1,
                    "resize_mode": "Crop and Resize",
                    "lowvram": 0,
                    "processor_res": 512,
                    "threshold_a": 64,
                    "threshold_b": 64,
                    "guidance": 1,
                    "guidance_start": 0,
                    "guidance_end": 1,
                    "guessmode": 1,
                    "pixel_perfect": 0
                }
            ]
        }

    control_net_payload["controlnet_units"][0]["input_image"] = img_base64
    control_net_payload["prompt"] = user_request_dict["prompt"]

    # This is the old payload (no control net)
    # payload = {
    #     "enable_hr": False,
    #     "denoising_strength": 0,
    #     "firstphase_width": 0,
    #     "firstphase_height": 0,
    #     "hr_scale": 2,
    #     "hr_upscaler": None,
    #     "hr_second_pass_steps": 0,
    #     "hr_resize_x": 0,
    #     "hr_resize_y": 0,
    #     "prompt": user_request_dict["prompt"],
    #     "styles": [
    #         "string"
    #     ],
    #     "seed": -1,
    #     "subseed": -1,
    #     "subseed_strength": 0,
    #     "seed_resize_from_h": -1,
    #     "seed_resize_from_w": -1,
    #     #"sampler_name": "string",
    #     "batch_count": 10,
    #     "n_iter": 1,
    #     "steps": 50,
    #     "cfg_scale": 8.5,
    #     "width": 768,
    #     "height": 768,
    #     "restore_faces": False,
    #     "tiling": False,
    #     "do_not_save_samples": True,
    #     "do_not_save_grid": True,
    #     "negative_prompt": "animated",
    #     "eta": 0,
    #     "s_churn": 0,
    #     "s_tmax": 0,
    #     "s_tmin": 0,
    #     "s_noise": 1,
    #     "override_settings": {},
    #     "override_settings_restore_afterwards": True,
    #     "script_args": [],
    #     #"sampler_index": "Euler A",
    #     #"script_name": "string",
    #     "send_images": True,
    #     "save_images": False,
    #     "alwayson_scripts": {}
    # }

    # send to A111
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    url = "http://192.168.1.158:7860/controlnet/txt2img"
    # response = requests.post(url, json=control_net_payload)

    # r = response.json()

    count = 0

     #call the queuing function
    results = await queuing_function(request, url, control_net_payload)

    r = results[0]
    image_list = []

    #receive generate images back and save 
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
        image_list.append(i.split(",", 1)[0])
        
        while os.path.isfile(f'output{count}.png'):
            count += 1
        image.save(f'output{count}.png')
        print(f"saved as output{count}.png")
        app.database.outputs.insert_one({"image": i.split(",", 1)[0], "filename": f'output{count}.png', "creation_time": datetime.now()})

        count += 1

    # find a way to send images to users

    return {"status": "working"}


# This lists 100 items in the downloads colelction
@app.get("/downloads", response_description="List all dls", response_model=List[Downloads])
def list_downloads(request: Request):
    dls = list(request.app.database["Downloads"].find(limit=100))
    return [document_to_model(download) for download in dls]

@app.get("/queue/status", response_description="Get Queue Status")
def queue_status(request: Request, user_id: int = None):
    status = get_queue_status(user_id)
    response = {
        "msg": "estimation",
        "rank": status["rank"],
        "queue_size": status["queue_size"],
        "avg_event_process_time": status["avg_event_process_time"],
        "avg_event_concurrent_process_time": status["avg_event_concurrent_process_time"],
        "rank_eta": status["rank_eta"],
        "queue_eta": status["queue_eta"],
    }
    return response
