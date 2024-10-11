import msgspec


class User(msgspec.Struct):
    first_name: str
    last_name: str
