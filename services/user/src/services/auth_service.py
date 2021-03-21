import logging
from src.services.jwt_service import JwtService
from src.repositories.user_repository import UserRepository
from typing import Tuple


class AuthService():
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def sign_up(self, email: str, password: str) -> Tuple[str, int]:
        created = self.user_repository.create_user(
            email=email, password=password)
        encoded, exp = self._encode_user_jwt(created)
        return str(encoded), exp

    def _encode_user_jwt(self, user):
        return JwtService.encode_jwt({"email": user.email, "_id": str(user._id)})
