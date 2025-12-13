import random
def make_otp(length: int = 5) -> str:
    start = 10 ** (length - 1)
    end = (10 ** length) - 1
    return str(random.randint(start, end))
