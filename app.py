from typing import Any, Optional
from bson import ObjectId
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

db_url = os.getenv("MONGODB_URL")
collection = "BOOKS"
table_name = "ISBN_REG_LIST"


class MongoDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[collection]
        self.collection = self.db[table_name]

    async def create_index(self, column_name: str):
        await self.collection.create_index(column_name, unique=True)

    async def close(self):
        self.client.close()


class BookModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    ISBN: str = Field(min_length=10, max_length=13, description="Book ISBN number")
    author: str
    pages: int
    publisher: str
    year_published: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdateBookModel(BaseModel):
    title: str | None = None
    ISBN: str = Field(min_length=10, max_length=13, description="Book ISBN number")
    author: str | None = None
    pages: int | None = None
    publisher: str | None = None
    year_published: datetime | None = None


class ApiResponse(BaseModel):
    code: str = Field(default="00")
    msg: str = Field(default="Success")
    details: Optional[dict] = Field(default_factory=dict)

    @staticmethod
    async def build_api_response(code: code, msg: msg, details: details or {}):
        return {"code": code, "msg": msg, "details": details}

    @staticmethod
    async def build_failure_response(details: details or {}):
        return {"code": "99", "msg": "Failed", "details": details}

    @classmethod
    async def build_details_api_response(cls, details: details or {}):
        instance = cls()
        return {"code": instance.code, "msg": instance.msg, "details": details}


class BookDbService:
    def __init__(self, db: MongoDB):
        self.db = db

    async def init_indexes(self):
        await self.db.create_index("ISBN")

    async def get_one_record(self, isbn: str) -> dict[str, str | Any]:
        record = await self.db.collection.find_one({"ISBN": isbn})
        if not record:
            raise HTTPException(status_code=400, detail=f"record with isbn: {isbn} not found")
        return await ApiResponse.build_details_api_response({"record": record})

    async def get_all_book_records(self) -> dict[str, str | Any]:
        records_cursor = self.db.collection.find({})
        records = await records_cursor.to_list(None)
        return await ApiResponse.build_details_api_response({"books": records})

    async def create_new_record(self, entry: BookModel) -> dict[str, str | dict | Any]:
        """
        create a new book record in the ISBN registration
        :param entry:
        :return str:
        """
        try:
            new_record = await self.db.collection.insert_one(entry.model_dump(by_alias=True))
            if not new_record:
                raise HTTPException(status_code=400, detail="book record could not be added")
        except:
            raise HTTPException(status_code=400, detail="book record could not be added")
        return await ApiResponse.build_details_api_response({"ISBN": entry.ISBN})

    async def insert_many_records(self, book_list: list[BookModel]) -> dict[str, str | Any]:
        """
        add many book records
        :param book_list:
        :return str:
        """
        created_records = await self.db.collection.insert_many([
            book.model_dump(by_alias=True) for book in book_list
        ])
        return await ApiResponse.build_details_api_response(
            f"{len(created_records.inserted_ids)} inserted successfully")

    async def update_one_record(self, book: UpdateBookModel) -> str | dict[str, str | dict | Any]:
        """
        update a book record in the db
        :param book:
        :return str:
        """
        record = self.db.collection.find_one("ISBN", book.ISBN)
        if not record:
            return f"Book record with isbn: {book.ISBN} not found"

        await self.db.collection.update_one(
            {"ISBN": book.ISBN},
            {"$set": book.model_dump(by_alias=True, exclude_unset=True)}
        )
        return await ApiResponse.build_details_api_response(f"record with ISBN {book.ISBN} updated")

    async def update_many_records(self, books: list[UpdateBookModel]) -> str | dict[str, str | dict | Any]:
        """
        update many book records
        this method ignores empty fields and invalid
        :param books:
        :return str:
        """
        non_existent_records = []
        for book in books:
            deleted_record = self.db.collection.find_one_and_update(
                {"ISBN": book.ISBN},
                {"$set": book.model_dump(by_alias=True, exclude_unset=True)}
            )
            if deleted_record is None: non_existent_records.append(book.ISBN)
        if non_existent_records:
            return f"Failed to update {len(non_existent_records)} record(s): {', '.join(non_existent_records)}"
        return await ApiResponse.build_details_api_response(
            f"All {len(books) - len(non_existent_records)} records updated successfully.")

    async def delete_record(self, isbn: str) -> str | dict[str, str | dict | Any]:
        """
        delete a book record from database
        :param isbn:
        :return:
        """
        deleted_record = await self.db.collection.delete_one({"ISBN": isbn})
        if deleted_record == 0:
            raise HTTPException(status_code=400, detail=f"Book with ISBN: {isbn} could not be deleted")
        return await ApiResponse.build_details_api_response(f"record with {isbn} deleted successfully")

    async def delete_many_records(self, isbns: list[str]) -> str | dict[str, str | dict | Any]:
        """
        delete many book records
        :param isbns:
        :return str:
        """
        non_existent_records = []
        for isbn in isbns:
            if not self.db.collection.delete_many({"ISBN": isbn}):
                non_existent_records.append(isbn)
        if non_existent_records:
            return await ApiResponse.build_details_api_response(
                f"{len(isbns) - len(non_existent_records)} record(s) deleted successfully. "
                f"{len(non_existent_records)} record(s) could not be deleted:\n {", ".join(non_existent_records)}")
        return await ApiResponse.build_details_api_response("All records deleted successfully.")


app = FastAPI()


@app.on_event("startup")
async def start_up_event():
    await Controller.book_service.init_indexes()


class Controller:
    book_service = BookDbService(MongoDB())

    @staticmethod
    @app.get("/get-by-isbn/{isbn}")
    async def get_book(isbn: str) -> dict[str, str | Any]:
        return await Controller.book_service.get_one_record(isbn)

    @staticmethod
    @app.get("/get-all-books")
    async def get_books() -> dict[str, str | Any]:
        return await Controller.book_service.get_all_book_records()

    @staticmethod
    @app.post("/add-record")
    async def add_new_record(book: BookModel) -> dict[str, str | dict | Any]:
        return await Controller.book_service.create_new_record(book)

    @staticmethod
    @app.post("/add-multiple-records")
    async def add_multiple(books: list[BookModel]):
        return await Controller.book_service.insert_many_records(books)

    @staticmethod
    @app.put("/update-record")
    async def update_one_record(book: UpdateBookModel) -> dict[str, str | Any]:
        return await Controller.book_service.update_one_record(book)

    @staticmethod
    @app.put("/update-many")
    async def update_many_records(books: list[UpdateBookModel]) -> dict[str, str | Any]:
        return await Controller.book_service.update_many_records(books)

    @staticmethod
    @app.delete("/delete-record/{isbn}")
    async def delete_record(isbn: str) -> dict[str, str | Any]:
        return await Controller.book_service.delete_record(isbn)

    @staticmethod
    @app.delete("/delete-many")
    async def delete_many_records(isbns: list[str]) -> dict[str, str | Any]:
        return await Controller.book_service.delete_many_records(isbns)

    @staticmethod
    @app.get("/close")
    async def close_db_connection() -> str:
        await Controller.book_service.db.close()
        return "DB connection closed"
