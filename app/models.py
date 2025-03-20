from pydantic import BaseModel, Field, field_serializer
from typing import Optional, Any, Dict
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, handler: Any) -> Dict[str, Any]:
        return handler.generate_schema(str)

    @classmethod
    def __get_pydantic_json_schema__(cls, _source_type: Any, _handler: Any) -> Dict[str, Any]:
        return {
            "type": "string",
            "format": "objectid",
            "pattern": "^[a-fA-F0-9]{24}$"
        }

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type="string")

class ItemModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    description: Optional[str] = None
    price: float = Field(...)
    quantity: int = Field(...)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "name": "Item Name",
                "description": "Item Description",
                "price": 10.5,
                "quantity": 5
            }
        }

    @field_serializer('id')
    def serialize_id(self, id: PyObjectId) -> str:
        return str(id)