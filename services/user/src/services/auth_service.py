from repositories.user_repository import UserRepository
from entities.user import UserEntity
from services.jwt_service import JwtService
from typing import List, Optional, Tuple


class AuthService():
    def __init__(self, user_repository: UserRepository, jwt_service: JwtService) -> None:
        self.user_repository = user_repository
        self.jwt_service = jwt_service

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

    def get_users(self, page: int, per_page: int) -> List[UserEntity]:
        users = self.user_repository.get_users(page=page, per_page=per_page)
        return users

    def _encode_user_jwt(self, user: UserEntity):
        return self.jwt_service.encode_jwt({"email": user.email, "_id": str(user._id)})
