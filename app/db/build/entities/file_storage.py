import inspect
from os import path, listdir, remove
from typing import Generator

from app.utils import generate_unique_id


class FileStorage:
    __id_length__ = 8

    def __init__(self, bucket_directory: str):
        context = inspect.stack()[1]

        anchor = path.join(
            path.dirname(context.filename),
            bucket_directory
        )

        self._bucket_path = path.relpath(anchor)

    def __getitem__(self, key: str) -> bytes:
        if key not in self.keys():
            raise KeyError("item does not exist")

        with open(f"{self._bucket_path}/{key}", mode="r") as item:
            return item.read().encode("utf-8")

    def __delitem__(self, key: str):
        try:
            remove(f"{self._bucket_path}/{key}")
        except FileNotFoundError:
            raise KeyError("item does not exist")

    def insert(self, item: bytes):
        new_id = generate_unique_id(FileStorage.__id_length__, self.keys())

        with open(f"{self._bucket_path}/{new_id}", mode="wb") as registry:
            registry.write(item)

    def keys(self) -> list[str]:
        return listdir(self._bucket_path)

    def values(self) -> Generator[bytes, None, None]:
        for filename in listdir(self._bucket_path):
            with open(f"{self._bucket_path}/{filename}", mode="r") as item:
                yield item.read().encode("utf-8")

    def items(self) -> Generator[tuple[str, bytes], None, None]:
        for filename in listdir(self._bucket_path):
            with open(f"{self._bucket_path}/{filename}", mode="rb") as item:
                yield filename, item.read()
