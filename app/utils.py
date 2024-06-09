from random import randint


def generate_unique_id(
        length: int,
        existing_ids: list[str]
) -> str:
    new_id = ""

    for _ in range(length):
        curr_index = randint(0, 51)

        if curr_index < 26:
            curr_char = chr(ord('a') + curr_index)
        else:
            curr_char = chr(ord('A') + (curr_index - 26))

        new_id += curr_char

    if new_id in existing_ids:
        return generate_unique_id(length, existing_ids)
    else:
        return new_id


def get_random_combination(source: list, count: int) -> list:
    collection = []

    if count > 0:
        rand_index = randint(0, len(source) - 1)

        collection.append(source[rand_index])
        collection.extend(get_random_combination(
            [item for item, index in enumerate(source) if index != rand_index],
            count - 1
        ))

    return collection


def to_base(number: int, base: int) -> list[int]:
    digits = []

    while number > 0:
        digits.append(number % base)
        number //= base

    return digits


def from_base(digits: list[int], base: int) -> int:
    result = 0

    for power, multiplier in enumerate(digits):
        result += multiplier * (base ** power)

    return result
