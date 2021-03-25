from typing import Optional, Union


class UserEntity():
    def __init__(self, _id: Optional[str] = '', email: str = '', hash: Optional[str] = '', salt: Union[str, None] = '', *args, **kwargs) -> None:
        self._id = _id
        self.email = email
        self.hash = hash
        self.salt = salt
