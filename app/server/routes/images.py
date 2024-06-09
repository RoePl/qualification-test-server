from io import BytesIO
from zipfile import ZipFile

from fastapi import APIRouter, HTTPException, status, UploadFile, Header
from fastapi.responses import StreamingResponse

from app.db import images, users
from app.server.routes.admins import validate_token
from app.utils import get_random_combination


class BinaryPipeline:
    def __init__(self, mode):
        self._buffer = BytesIO()
        self._mode = mode
        self._stream: ZipFile | None = None

    def __setitem__(self, key, value):
        try:
            self._stream.writestr(key, value)
        except AttributeError:
            raise IOError("function called on an idle pipeline")

    def __enter__(self):
        self._stream = ZipFile(self._buffer, self._mode)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._stream:
            self._stream.close()

    def __iter__(self):
        self._buffer.seek(0)

        return self._buffer


image_router = APIRouter(prefix="/images")


@image_router.post("")
async def add_images(new_images: list[UploadFile], authorization: str = Header()):
    validate_token(authorization)

    for item in new_images:
        images.insert(await item.read())


@image_router.get("/all")
async def get_all_images(authorization: str = Header()):
    validate_token(authorization)

    image_pln = BinaryPipeline(mode="a")

    with image_pln:
        for key, value in images.items():
            image_pln[key] = value

    return StreamingResponse(image_pln, media_type="application/zip")


@image_router.get("/shuffled/{user_id}/{length}")
async def get_next_combination(user_id: str, length: int):
    [target_user, ] = users.filter(lambda user: user.id == user_id)

    used_images = target_user.watched_images()
    total_images = images.keys()

    image_pln = BinaryPipeline(mode="a")

    unused_images = [
        key for key in total_images
        if key not in used_images
    ]

    if len(unused_images) < length:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="No combinations available for current user"
        )

    with image_pln:
        shuffle = get_random_combination(unused_images, length)

        for key in shuffle:
            image_pln[key] = images[key]

    return StreamingResponse(image_pln, media_type="application/zip")


@image_router.delete("/id/{image_id}")
async def delete_image_by_id(image_id: str, authorization: str = Header()):
    validate_token(authorization)

    try:
        del images[image_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="image not found"
        )
