from fastapi import APIRouter, Header

from app.db import users
from app.db.models import Choice, User
from app.server.routes.admins import validate_token

user_router = APIRouter(prefix="/users")


@user_router.get("")
async def get_all_users(authorization: str = Header()) -> list[User]:
    validate_token(authorization)

    return users.data


@user_router.post("")
async def create_user() -> str:
    [user_id, ] = users.insert([User()], returning=lambda user: user.id)

    return user_id


@user_router.post("/{user_id}/choices")
async def register_user_choice(user_id: str, user_choice: Choice):
    def add_choice_to_user(user: User):
        if user.id == user_id:
            user.choices.append(user_choice)

    users.for_each(add_choice_to_user)
