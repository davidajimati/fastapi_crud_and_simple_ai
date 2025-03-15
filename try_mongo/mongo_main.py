import os
import asyncio
from try_mongo.db.MongoDB import MongoDB
from try_mongo.service.UserService import UserService


async def main():
    db = MongoDB(os.environ["MONGODB_URL"], "testdb")
    user_service = UserService(db)

    new_user = {
        "email": "david@example.com",
        "chat_history": "Hello, Great and mighty world. Thou art great, but thine creator is unexplainable and much greater!",
        "username": "david"
    }
    created_user = await user_service.create_user(new_user)
    print("Created User:", created_user)

    # Retrieve the user
    retrieved_user = await user_service.get_user("test@example.com")
    print("Retrieved User:", retrieved_user)

    # Update the user's chat history
    updated_user = await user_service.update_user(
        "test@example.com", {"chat_history": "Updated chat history"}
    )
    print("Updated User:", updated_user)

    # Delete the user
    # deletion_success = await user_service.delete_user("test@example.com")
    # print("Deletion Successful:", deletion_success)

    await db.close()


# Run the example
asyncio.run(main())
