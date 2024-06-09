from os import environ
from typing import Callable, Union, Generator
from random import randint
from app.utils import from_base, to_base


class Base64:
    @staticmethod
    def chr(number: int) -> str:
        if number < 0 or number >= 64:
            raise ValueError("number out of encoding range")

        if number < 26:
            return chr(ord('A') + number)
        elif number < 52:
            return chr(ord('a') + (number - 26))
        elif number < 62:
            return chr(ord('0') + (number - 52))
        elif number == 62:
            return '+'
        else:
            return '/'

    @staticmethod
    def ord(character: str) -> int:
        if len(character) == 0:
            raise ValueError("can't decode an empty string")

        if len(character) > 1:
            raise ValueError("can't decode a multi-character string")

        if 'A' <= character <= 'Z':
            return ord(character) - ord('A')
        elif 'a' <= character <= 'z':
            return 26 + (ord(character) - ord('a'))
        elif '0' <= character <= '9':
            return 52 + (ord(character) - ord('0'))
        elif character == '+':
            return 62
        elif character == '/':
            return 63
        else:
            raise ValueError("no matches found")

    @staticmethod
    def str(value: Union[int, list[int]]) -> str:
        result = ""

        if isinstance(value, int):
            value = to_base(value, 64)
            value.reverse()

        for digit in value:
            result += Base64.chr(digit)

        return result

    @staticmethod
    def digits(string: str) -> list[int]:
        return [Base64.ord(character) for character in string]

    @staticmethod
    def int(value: Union[str, list[str]]) -> int:
        if isinstance(value, list):
            value = ''.join(value[::-1])

        digits = Base64.digits(value)
        digits.reverse()

        return from_base(digits, 64)


class Encryptor:
    def __init__(self, key: str, transform: Callable[[int, int], int]):
        if len(key) > 64:
            raise ValueError()

        self._key = key
        self._transform = transform

    def encode(self, sequence: str) -> str:
        random_indexes = [
            randint(0, len(self._key) - 1)
            for _ in sequence
        ]

        seq_unicodes = [ord(character) for character in sequence]
        key_unicodes = [ord(character) for character in self._key]

        body = [
            self._transform(
                # key_unicodes[random_indexes[index]],
                ord(self._key[random_indexes[index]]),
                seq_unicodes[index]
            ) for index in range(len(sequence))
        ]

        body = [
            Base64.str(item)
            for item in body
        ]

        keys = [Base64.chr(item) for item in random_indexes]
        chunks = []

        for index in range(len(random_indexes)):
            value = body[index]
            length = Base64.str(len(value))
            separator = '%' if len(length) > 1 else ''
            prefix = '&' if separator and index else ''

            chunks.append(f"{prefix}{length}{separator}{value}")

        for _ in self._split(''.join(chunks)):
            continue

        return f"{''.join(keys)}:{''.join(chunks)}"

    def decode(self, sequence: str) -> str:
        [keys, body] = sequence.split(':')
        keys = Base64.digits(keys)
        result = []

        for index, value in enumerate(self._split(body)):
            value = Base64.int(value)
            key = ord(self._key[keys[index]])
            unicode = 0

            while self._transform(key, unicode) != value:
                unicode += 1

            result.append(chr(unicode))

        return ''.join(result)

    @staticmethod
    def _split(sequence: str) -> Generator[str, None, None]:
        chunks = sequence.split('&')

        for item in chunks:
            if '%' in item:
                [length, tail] = item.split('%')
                length = Base64.int(length)

                yield tail[:length]
                item = tail[length:]

            while len(item) > 0:
                length = Base64.int(item[0])
                item = item[1:]

                yield item[:length]
                item = item[length:]


token_generator = Encryptor(
    environ["SERVER_ENCRYPTION_KEY"],
    lambda a, b: 3 ** (a + b)
)