import json
import os
from os import path
import inspect
from typing import Type, Callable, Any, TypeVar
from app.db.build.base_type import BaseType


T = TypeVar("T", bound=BaseType)


class Table:
    def __init__(self, model: Type[T], directory: str = None):
        self.bucket_path = directory
        self._row_type = model

    def for_each(self, consumer: Callable[[T], None]):
        table = self.data

        for item in table:
            consumer(item)

        self.data = table

    def map(self, transform: Callable[[T], T]) -> list[Any]:
        return [transform(row) for row in self.data]

    def filter(self, predicate: Callable[[T], bool]) -> list[T]:
        return [row for row in self.data if predicate(row)]

    def insert(self, rows: list[T], *, returning: Callable[[T], Any] = None):
        table = self.data
        collected_values = []

        for row in rows:
            row.validate(table)

            if returning:
                collected_values.append(returning(row))

            table.append(row)

        self.data = table

        if returning:
            return collected_values

    @property
    def data(self) -> list[T]:
        with open(self.bucket_path, mode="r") as table:
            return [
                self._row_type.model_validate(row)
                for row in json.load(table)
            ]

    @data.setter
    def data(self, rows: list[T]):
        with open(self.bucket_path, mode="w") as table:
            json.dump([
                row.model_dump()
                for row in rows
            ], table, indent=4)


def connect_tables(bucket_directory):
    context = inspect.stack()[1]
    namespace = context.frame.f_locals

    anchor = path.join(
        path.dirname(context.filename),
        bucket_directory
    )

    bucket_relpath = path.relpath(anchor)

    for key, value in namespace.items():
        if not isinstance(value, Table):
            continue

        head = f"{key}.json"
        value.bucket_path = f"{bucket_relpath}/{head}"

        if head not in os.listdir(anchor):
            with open(value.bucket_path, mode="a") as table:
                table.write("[]")
