from fastapi import FastAPI, Body, Request, Response, HTTPException, status
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from typing import List
from models import Downloads, UserRequest
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

    # log the user request
    app.database.requests.insert_one(user_request_dict)
    print("logged")

    # improve prompt

    # choose relevant pose

    # prepare settings
    settings = app.database.settings.find_one({"settings_id": 0})
    if (not settings):
        return {"status": "error"}


    print(settings)

    # pass in actual prompt
    settings["prompt"] = user_request_dict["prompt"]
    settings["negative_prompt"] = "blurry, low quality, animated, cartoon, silverware, fork, knife, spoon, chopsticks,"
    


    # send to A111
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    url = "http://192.168.1.158:7860/sdapi/v1/txt2img"
    response = requests.post(url, json=payload)

    r = response.json()

    # receive generate images back and save 
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        image.save(f'output{i}.png')


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
