from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Downloads

router = APIRouter()

def document_to_model(document: dict) -> Downloads:
    document["_id"] = str(document["_id"])
    return Downloads(**document)

@router.post("/", response_description="Log a new download", status_code=status.HTTP_201_CREATED, response_model=Downloads)
def create_download(request: Request, download: Downloads = Body(...)):
    dl = jsonable_encoder(download)
    new_dl = request.app.database["Downloads"].insert_one(dl)
    created_dl = request.app.database["Downloads"].find_one(
        {"_id": new_dl.inserted_id}
    )

    return created_dl


@router.get("/", response_description="List all dls", response_model=List[Downloads])
def list_downloads(request: Request):
    dls = list(request.app.database["Downloads"].find(limit=100))
    return [document_to_model(download) for download in dls]