from dotenv import load_dotenv
from try_mongo.db.MongoDB import MongoDB
from try_mongo.model.UserModel import UserModel



load_dotenv()

class UserService:
    def __init__(self, db: MongoDB):
        self.db = db

    async def create_user(self, user_data: dict) -> UserModel:
        user = UserModel(**user_data)
        await self.db.collection.insert_one(user.model_dump(by_alias=True))
        return user

    async def get_user(self, email: str) -> UserModel:
        user_data = await self.db.collection.find_one({"email": email})
        if not user_data:
            return UserModel()
        return UserModel(**user_data)

    async def update_user(self, email: str, update_data: dict) -> UserModel:
        result = await self.db.collection.update_one(
            {"email": email}, {"$set": update_data}
        )
        if result.modified_count:
            return await self.get_user(email)
        return None

    async def delete_user(self, email: str) -> bool:
        result = await self.db.collection.delete_one({"email": email})
        return result.deleted_count > 0