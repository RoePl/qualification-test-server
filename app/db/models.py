from pydantic import BaseModel
from .build.base_type import BaseType
from app.utils import generate_unique_id


class Choice(BaseModel):
    image_combination: list[str]
    selected_image: str


class User(BaseType):
    id: str | None = None
    choices: list[Choice] = []
    __id_length__ = 6

    def validate(self, dependencies: list['User']):
        existing_ids = [row.id for row in dependencies]

        self.id = generate_unique_id(User.__id_length__, existing_ids)

    def watched_images(self) -> list[str]:
        used_combinations = [
            choice.image_combination
            for choice in self.choices
        ]

        watched_images = [
            item for combination
            in used_combinations
            for item in combination
        ]

        return watched_images


class Administrator(BaseType):
    email: str
    password: str

    def validate(self, dependencies: list['Administrator']):
        if self.email in [row.email for row in dependencies]:
            raise ValueError("Email already exists")
