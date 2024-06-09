import json

from fastapi import APIRouter, HTTPException, status

from app.db import admins
from app.db.models import Administrator
from app.encryption import token_generator

admin_router = APIRouter(prefix="/admins")


def validate_token(token: str):
    try:
        credentials = json.loads(token_generator.decode(token))
        potential_admin = Administrator(**credentials)

        if potential_admin not in admins.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="no matches for provided credentials"
            )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="invalid authorization token"
        )


@admin_router.get("/auth")
async def authenticate_admin(email: str, password: str):
    potential_admin = Administrator(email=email, password=password)

    if potential_admin in admins.data:
        return token_generator.encode(json.dumps(
            {
                "email": email,
                "password": password
            }
        ))
