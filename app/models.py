from pydantic import BaseModel, Field, field_serializer, model_serializer
from typing import Optional, Any, Dict
from bson import ObjectId

class PyObjectId(ObjectId):
    # Pydantic v2에서는 __get_validators__와 __modify_schema__ 대신 다른 방식을 사용합니다
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> Dict[str, Any]:
        return {
            "type": "string",
            "validator": lambda v: ObjectId(v) if isinstance(v, str) and ObjectId.is_valid(v) else v
        }

class ItemModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    description: Optional[str] = None
    price: float = Field(...)
    quantity: int = Field(...)

    model_config = {
        "populate_by_name": True,  # v2에서는 allow_population_by_field_name 대신 이것을 사용
        "arbitrary_types_allowed": True,
        "json_schema_extra": {     # v2에서는 schema_extra 대신 이것을 사용
            "example": {
                "name": "Item Name",
                "description": "Item Description",
                "price": 10.5,
                "quantity": 5
            }
        }
    }

    # ObjectId를 문자열로 변환하기 위한 시리얼라이저
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId) -> str:
        return str(id)