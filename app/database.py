import motor.motor_asyncio
import os
from models import ItemModel

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
database = client[os.getenv("MONGODB_DB", "fastapi_db")]
item_collection = database.get_collection("items")
