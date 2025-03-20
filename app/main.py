from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List
import models
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB")]
    print("Connected to MongoDB!")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

@app.get("/")
async def root():
    return {"message": "FastAPI MongoDB CRUD API"}

@app.post("/items/", response_model=models.ItemModel, status_code=status.HTTP_201_CREATED)
async def create_item(item: models.ItemModel):
    new_item = await app.mongodb.items.insert_one(item.dict())
    created_item = await app.mongodb.items.find_one({"_id": new_item.inserted_id})
    return models.ItemModel(**created_item)

@app.get("/items/", response_model=List[models.ItemModel])
async def list_items():
    items = await app.mongodb.items.find().to_list(1000)
    return [models.ItemModel(**item) for item in items]

@app.get("/items/{id}", response_model=models.ItemModel)
async def get_item(id: str):
    try:
        item = await app.mongodb.items.find_one({"_id": ObjectId(id)})
        if item:
            return models.ItemModel(**item)
        raise HTTPException(status_code=404, detail=f"Item with id {id} not found")
    except:
        raise HTTPException(status_code=400, detail=f"Invalid id format")

@app.put("/items/{id}", response_model=models.ItemModel)
async def update_item(id: str, item: models.ItemModel):
    try:
        item_dict = item.dict()
        # Remove _id if it exists to avoid conflicts
        item_dict.pop('id', None)
        
        update_result = await app.mongodb.items.update_one(
            {"_id": ObjectId(id)}, {"$set": item_dict}
        )
        
        if update_result.modified_count == 1:
            updated_item = await app.mongodb.items.find_one({"_id": ObjectId(id)})
            return models.ItemModel(**updated_item)
            
        raise HTTPException(status_code=404, detail=f"Item with id {id} not found")
    except:
        raise HTTPException(status_code=400, detail=f"Invalid id format or item data")

@app.delete("/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(id: str):
    try:
        delete_result = await app.mongodb.items.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 1:
            return
        raise HTTPException(status_code=404, detail=f"Item with id {id} not found")
    except:
        raise HTTPException(status_code=400, detail=f"Invalid id format")

