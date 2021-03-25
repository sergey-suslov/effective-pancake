from typing import Optional
import uuid
import hashlib

from bson.objectid import ObjectId
from src.errors.reposityry_errors import CouldNotCreateUser
from src.entities.user import UserEntity
from pymongo import MongoClient


class UserRepository():
    def __init__(self, client: MongoClient) -> None:
        self.client = client

    def create_user(self, email: str, password: str) -> UserEntity:
        existing = self.client.db.users.find_one({"email": email})
        if existing:
            return UserEntity(**existing)
        salt = uuid.uuid4().hex.upper()[0:6]
        hash = self._get_hash(password, salt)
        created_id = self.client.db.users.insert_one(
            {"email": email, "hash": hash, "salt": salt}).inserted_id
        created = self.client.db.users.find_one({'_id': created_id})
        if created is None:
            raise CouldNotCreateUser()

        return UserEntity(**created)

    def get_user_by_id(self, id: str) -> Optional[UserEntity]:
        existing = self.client.db.users.find_one(
            {"_id": ObjectId(id)}, projection=['email'])
        if not existing:
            return None
        existing["_id"] = str(existing["_id"])
        return UserEntity(**existing)

    def get_user_by_email_and_password(self, email: str, password: str) -> Optional[UserEntity]:
        existing = self.client.db.users.find_one(
            {"email": email})
        if not existing:
            return None
        user = UserEntity(**existing)
        hash = self._get_hash(password, user.salt)
        if hash != user.hash:
            return None
        return user

    def _get_hash(self, password, salt):
        hash = hashlib.sha256()
        hash.update(bytes(password, encoding='utf-8'))
        hash.update(bytes(salt, encoding='utf-8'))
        return str(hash.digest())
