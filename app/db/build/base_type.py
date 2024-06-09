from pydantic import BaseModel


class BaseType(BaseModel):
    def __eq__(self, other: 'BaseType') -> bool:
        if type(self) is not type(other):
            return False

        return self.model_dump() == other.model_dump()

    def validate(self, dependencies: list['BaseType']):
        pass
