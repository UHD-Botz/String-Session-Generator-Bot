import motor.motor_asyncio
from config import MONGO_DB_URI


class Database:
    def __init__(self, uri: str, database_name: str):
        if not uri:
            raise ValueError("❌ MONGO_DB_URI is not set")

        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

        # Ensure unique index on user_id
        self.col.create_index("user_id", unique=True)

    def new_user(self, user_id: int, name: str):
        return {
            "user_id": int(user_id),
            "name": name
        }

    async def add_user(self, user_id: int, name: str):
        if await self.is_user_exist(user_id):
            return
        user = self.new_user(user_id, name)
        try:
            await self.col.insert_one(user)
        except Exception:
            pass  # ignore duplicate insert race condition

    async def is_user_exist(self, user_id: int) -> bool:
        user = await self.col.find_one({"user_id": int(user_id)})
        return bool(user)

    async def total_users_count(self) -> int:
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({}, {"_id": 0})

    async def delete_user(self, user_id: int):
        await self.col.delete_one({"user_id": int(user_id)})


db = Database(MONGO_DB_URI, "uhdbots")
