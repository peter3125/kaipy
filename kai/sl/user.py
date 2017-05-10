import os
import uuid
import hashlib, binascii

from kai.cassandra.model import User, Session
from kai.cassandra.user import get_user, save_user
from kai.cassandra.session import save_session, delete_session, get_session


invalid_user = User('', '', '', uuid.uuid4(), '')
invalid_session = Session('', '', '', uuid.uuid4())


# create a new user if does not already exist, returns user object and error string
def create_user(email: str, first_name: str, surname: str, password_str: str, min_password_length) -> (User, str):
    if len(email.strip()) == 0 or len(first_name.strip()) == 0 or len(surname.strip()) == 0 or \
                    len(password_str.strip()) < min_password_length:
        return invalid_user, "invalid user parameters, minimum password length %s" % min_password_length

    existing_user = get_user(email)
    if existing_user is not None:
        return invalid_user, "a user with that email address already exists: %s" % email.strip().lower()

    # create a new salt
    salt = uuid.uuid4()
    password_hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password_str.strip().encode("utf-8"), salt.bytes, 100001))

    # save the user object
    password_hash_str = password_hash.decode("utf-8")
    new_user = User(email, first_name, surname, salt, password_hash_str)
    save_user(new_user)

    return new_user, ""


# sign in an existing user and create a session
def sign_in(email: str, password_str: str, min_password_length) -> (Session, str):
    if len(email.strip()) == 0 or len(password_str.strip()) < min_password_length:
        return invalid_session, "invalid login parameters, minimum password length %s" % min_password_length

    # check we've got an email address
    existing_user = get_user(email)
    if existing_user is None:
        return invalid_session, "a user with that email does not exists: %s" % email.strip().lower()

    # check we've got the right password
    salt = existing_user.salt
    password_hash = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password_str.strip().encode("utf-8"), salt.bytes, 100001))
    password_hash_str = password_hash.decode("utf-8")
    if password_hash_str != existing_user.password_hash:
        return invalid_session, "sign-in: password incorrect"

    # create a new session and return it
    sess_id = uuid.uuid4()
    session = Session(existing_user.first_name, existing_user.surname, existing_user.email, sess_id)
    # save to db
    save_session(sess_id, existing_user.email, existing_user.first_name, existing_user.surname)
    return session, ""


# remove an existing session by id
def sign_out(session_id: uuid.UUID):
    delete_session(session_id)


# retrieve an existing session object by id
def get_session_from_session_id(session_id: uuid.UUID) -> Session:
    return get_session(session_id)
