from kai.cassandra.model import User
from kai.cassandra.cluster import cassy


# create a new user object - do check this user doesn't already exist
def save_user(user: User):
    if len(user.email.strip()) == 0 or len(user.first_name.strip()) == 0 or len(user.surname.strip()) == 0 or \
       len(user.password_hash.strip()) == 0:
        raise ValueError("invalid user object")

    cassy().db_insert("user", {"email": user.email.strip().lower(), "first_name": user.first_name, "surname": user.surname,
                               "salt": user.salt, "password_hash": user.password_hash})


# return a user object (or none if dne) with all its details
def get_user(email: str) -> User:
    if len(email.strip()) > 0:
        cols = ["first_name", "surname", "salt", "password_hash"]
        row_list = cassy().db_select("user", cols, {"email": email.strip().lower()})
        if len(row_list) == 1:
            row = row_list[0]
            return User(email.strip().lower(), row[0], row[1], row[2], row[3])
    return None
