from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db['users']

    async def create_indexes(self):
        await self.collection.create_index("email", unique=True)

    async def close(self):
        self.client.close()