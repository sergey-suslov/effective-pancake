from src.repositories.user_repository import UserRepository
from src.entities.user import UserEntity
from src.services.jwt_service import JwtService
from typing import Optional, Tuple


class AuthService():
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def sign_up(self, email: str, password: str) -> Tuple[str, int]:
        created = self.user_repository.create_user(
            email=email, password=password)
        encoded, exp = self._encode_user_jwt(created)
        return str(encoded), exp

    def sign_in(self, email: str, password: str) -> Optional[Tuple[str, int]]:
        user = self.user_repository.get_user_by_email_and_password(
            email=email, password=password)
        if not user:
            return None
        encoded, exp = self._encode_user_jwt(user)
        return str(encoded), exp

    def profile(self, id: str) -> Optional[UserEntity]:
        user = self.user_repository.get_user_by_id(
            id=id)
        return user

    def _encode_user_jwt(self, user: UserEntity):
        return JwtService.encode_jwt({"email": user.email, "_id": str(user._id)})
