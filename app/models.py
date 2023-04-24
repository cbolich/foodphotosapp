import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Downloads(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    user: str = Field(...)
    filename: str = Field(...)
    date: str = Field(datetime.now())

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "title": "Jacob Frabutt",
                "filename": "img764679.jpg",
                "date": "2023-04-23 17:16:21.892940"
            }
        }

