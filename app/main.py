from fastapi import FastAPI, Body, Request, Response, HTTPException, status
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from typing import List
from models import Downloads, UserRequest
from modules.queuing import queuing_function
import asyncio
import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin

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
    
    #example requests
    requests = ["Request 1", "Request 2", "Request 3"]

    #call the queuing function
    results = await queuing_function(requests)
#    results = queuing_function(user_request_dict)


    # log the user request
    app.database.requests.insert_one(user_request_dict)
    print("logged")

    # Process the results
    for idx, result in enumerate(results):
        print(f"Result for {requests[idx]}: {result}")

    # improve prompt



    # choose relevant pose

    # prepare settings
    settings = app.database.settings.find_one({"settings_id": 0})
    if (not settings):
        return {"status": "error"}


    # pass in actual prompt
    settings["prompt"] = user_request_dict["prompt"]
    settings["negative_prompt"] = "blurry, low quality, animated, cartoon, silverware, fork, knife, spoon, chopsticks,"
    
    payload = {
        "enable_hr": False,
        "denoising_strength": 0,
        "firstphase_width": 0,
        "firstphase_height": 0,
        "hr_scale": 2,
        "hr_upscaler": None,
        "hr_second_pass_steps": 0,
        "hr_resize_x": 0,
        "hr_resize_y": 0,
        "prompt": user_request_dict["prompt"],
        "styles": [
            "string"
        ],
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        #"sampler_name": "string",
        "batch_count": 10,
        "n_iter": 1,
        "steps": 50,
        "cfg_scale": 8.5,
        "width": 768,
        "height": 768,
        "restore_faces": False,
        "tiling": False,
        "do_not_save_samples": True,
        "do_not_save_grid": True,
        "negative_prompt": "animated",
        "eta": 0,
        "s_churn": 0,
        "s_tmax": 0,
        "s_tmin": 0,
        "s_noise": 1,
        "override_settings": {},
        "override_settings_restore_afterwards": True,
        "script_args": [],
        #"sampler_index": "Euler A",
        #"script_name": "string",
        "send_images": True,
        "save_images": False,
        "alwayson_scripts": {}
    }

    # send to A111
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    url = "http://192.168.1.158:7860/sdapi/v1/txt2img"
    response = requests.post(url, json=payload)

    r = response.json()
    print(r['parameters'])
    print(r['info'])
    print(len(r['images']))
    
    count = 0
    # receive generate images back and save 
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        print("saving")
        image.save(f'output{count}.png')
        print("saved")
        count+= 1

    # get response back

    # save reponses to data base
    """ 
    for file in results:
        save_image(file, app.database.outputs)

    """

    # find a way to send images to user

    return {"status": "working"}


# This lists 100 items in the downloads colelction
@app.get("/downloads", response_description="List all dls", response_model=List[Downloads])
def list_downloads(request: Request):
    dls = list(request.app.database["Downloads"].find(limit=100))
    return [document_to_model(download) for download in dls]

@app.get("/queue/status", response_description="Get Queue Status")
def queue_status(request: Request, user_id: Optional[int] = None):
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
