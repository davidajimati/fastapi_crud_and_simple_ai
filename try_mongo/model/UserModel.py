from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class UserModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    email: EmailStr
    chat_history: str
    username: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
