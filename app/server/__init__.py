from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from os import environ
from .routes import image_router, user_router, admin_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{environ[f'CLIENT_HOST']}:{environ[f'CLIENT_PORT']}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_router = APIRouter(prefix="/image-deck")

main_router.include_router(image_router)
main_router.include_router(user_router)
main_router.include_router(admin_router)

app.include_router(main_router)
