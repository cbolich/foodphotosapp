from fastapi import FastAPI, Body, Request, Response, HTTPException, status
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from typing import List
from models import Downloads, UserRequest
from modules.queuing import queuing_function


app = FastAPI()

"""SET UP / MISC """
@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb+srv://{USER}:{PASSWORD}@foodphotosapp.4vgexei.mongodb.net/?retryWrites=true&w=majority")
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

    # Process the results
    for idx, result in enumerate(results):
        print(f"Result for {requests[idx]}: {result}")

    # improve prompt



    # choose relevant pose

    # prepare settings
    settings = app.database.settings.find_one({"settings_id": 1})
    if (not settings):
        return {"status": "error"}

    # send to A111



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
