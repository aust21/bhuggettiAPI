import random


def generate_code():
    code = set()

    while len(code) < 7:
        num = random.randint(0, 9)
        code.add(str(num))
    return "".join(code)


print(generate_code())