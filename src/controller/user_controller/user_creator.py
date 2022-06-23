from models.db_models import User
from util.errors import ObjectAlreadyExists, ValidationError
from email_validator import validate_email, EmailNotValidError

from passlib.hash import bcrypt


class UserCreator:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    async def __call__(self):
        if await self.allowed_to_create():
            user = await self.create_user()
        else:
            return False

        return user

    async def create_user(self):
        return await User.create(
            email=self.email,
            password=bcrypt.hash(self.password)
        )

    async def allowed_to_create(self):
        try:
            if await User.exists(email=self.email):
                raise ObjectAlreadyExists
            validate_email(self.email)
        except (ObjectAlreadyExists, EmailNotValidError, ValidationError) as exc:
            raise exc

        return True