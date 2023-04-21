from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

app = FastAPI()

# Replace with your MongoDB connection string if needed
MONGODB_URI = "mongodb://admin:secret@mongodb:27017"

client = AsyncIOMotorClient(MONGODB_URI)
db = client.my_database
items_collection = db.items

class Item(BaseModel):
    id: str = None
    name: str
    description: str
    price: float

@app.on_event("startup")
async def startup_event():
    global items_collection
    items_collection = db.items

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    item_dict = item.dict()
    item_dict["_id"] = ObjectId()
    await items_collection.insert_one(item_dict)
    item.id = str(item_dict["_id"])
    return item

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    item = await items_collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(**item)

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, updated_item: Item):
    item = await items_collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await items_collection.replace_one({"_id": ObjectId(item_id)}, updated_item.dict())
    updated_item.id = item_id
    return updated_item

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    delete_result = await items_collection.delete_one({"_id": ObjectId(item_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
