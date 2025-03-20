from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List
import models
import os
from contextlib import asynccontextmanager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI MongoDB CRUD API"}

@app.post("/items/", response_model=models.ItemModel, status_code=status.HTTP_201_CREATED)
async def create_item(item: models.ItemModel):
    # 여기서 model_dump()를 사용하여 딕셔너리로 변환 (dict() 대신)
    item_dict = item.model_dump(exclude={"id"})

    new_item = await app.mongodb.items.insert_one(item_dict)
    created_item = await app.mongodb.items.find_one({"_id": new_item.inserted_id})

    # ObjectId를 문자열로 변환
    if created_item and "_id" in created_item:
        created_item["_id"] = str(created_item["_id"])

    return models.ItemModel(**created_item)

@app.get("/items/")
async def list_items():
    items = await app.mongodb.items.find().to_list(1000)
    for i in items:
        i["_id"] = str(i["_id"])
    return [models.ItemModel(**i) for i in items]

@app.get("/items/{id}")
async def get_item(id: str):
    try:
        item = await app.mongodb.items.find_one({"_id": ObjectId(id)})
        if item:
            item["_id"] = str(item["_id"])
            return models.ItemModel(**item)
        raise HTTPException(status_code=404, detail=f"Item with id {id} not found")
    except:
        raise HTTPException(status_code=400, detail=f"Invalid id format")

@app.put("/items/{id}")
async def update_item(id: str, item: models.ItemModel):
    try:
        item_dict = item.dict()
        item_dict.pop("id", None)
        update_result = await app.mongodb.items.update_one(
            {"_id": ObjectId(id)}, {"$set": item_dict}
        )
        if update_result.modified_count == 1:
            updated_item = await app.mongodb.items.find_one({"_id": ObjectId(id)})
            updated_item["_id"] = str(updated_item["_id"])
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB")]
    print("Connected to MongoDB!")
    yield
    app.mongodb_client.close()

app.router.lifespan_context = lifespan