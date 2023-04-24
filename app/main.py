from fastapi import FastAPI, Body, Request, Response, HTTPException, status
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from typing import List
from models import Downloads

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

# This lists 100 items in the downloads colelction
@app.get("/downloads", response_description="List all dls", response_model=List[Downloads])
def list_downloads(request: Request):
    dls = list(request.app.database["Downloads"].find(limit=100))
    return [document_to_model(download) for download in dls]
