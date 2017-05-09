import uuid
from kai.cassandra.cluster import cassy
from kai.cassandra.model import Session


# get a session by session_str or return None if dne
def get(session: uuid.UUID) -> Session:
    cols = ["first_name", "surname", "email"]
    where_map = {"session": session }
    result_list = cassy().db_select("session", cols, where_map)
    if len(result_list) >= 1:
        result = result_list[0]
        return Session(result[0], result[1], result[2], session)
    return None


# delete a session by session_str
def delete(session: uuid.UUID):
    where_map = {"session": session }
    cassy().db_delete("session", where_map)


# save a session
def save(id: uuid.UUID, email: str, first_name: str, surname: str):
    if len(email) == 0 or len(first_name) == 0 or len(surname) == 0:
        raise ValueError("session save(): invalid parameter(s)")
    value_map = {"email": email, "first_name": first_name, "surname": surname, "session": id}
    cassy().db_insert("session", value_map)

