import uuid


# session class / object
class Session:
    def __init__(self, first_name: str, surname: str, email: str, session: uuid.UUID):
        self.first_name = first_name
        self.surname = surname
        self.email = email
        self.session = session

    def get_username(self) -> str:
        return self.first_name + " " + self.surname

    def __str__(self):
        return self.get_username() + " /email:" + self.email + " /session:" + str(self.session)

    def __repr__(self):
        return self.__str__()


# an index of the search system
class Index:
    def __init__(self, sentence_id: uuid.UUID, word: str, tag: str, shard: int, offset: int, topic: str, score: float):
        self.sentence_id = sentence_id
        self.word = word
        self.tag = tag
        self.shard = shard
        self.offset = offset
        self.topic = topic
        self.score = score

    def __str__(self):
        return self.word + " /tag:" + self.tag + " /offset:" + str(self.offset) + " /score:" + str(self.score)

    def __repr__(self):
        return self.__str__()


class UnIndex:
    def __init__(self, sentence_id: uuid.UUID, word: str, shard: int):
        self.sentence_id = sentence_id
        self.word = word
        self.shard = shard

    def __str__(self):
        return self.word + " /sentence_id:" + str(self.sentence_id)

    def __repr__(self):
        return self.__str__()


class IndexMatch:
    def __init__(self, sentence_id: uuid.UUID, word: str, tag: str, shard: int, offset: int,
                 topic: str, score: float, keyword_index: int):
        self.sentence_id = sentence_id
        self.word = word
        self.tag = tag
        self.shard = shard
        self.offset = offset
        self.topic = topic
        self.score = score
        self.keyword_index = keyword_index

    def __str__(self):
        return self.word + " /tag:" + self.tag + " /offset:" + str(self.offset) + " /score:" + \
               str(self.score) + " /kw:" + str(self.keyword_index)

    def __repr__(self):
        return self.__str__()


# a return result for the service layer
class ATResult:
    def __init__(self, text: str, timestamp: str, topic: str, sentence_id: uuid.UUID = None, kb_id: uuid.UUID = None):
        self.text = text
        self.timestamp = timestamp
        self.topic = topic
        self.sentence_id = sentence_id
        self.kb_id = kb_id

    def __str__(self):
        return self.text + " /topic:" + self.topic + " /time:" + self.timestamp

    def __repr__(self):
        return self.__str__()


# a Kai user
class User:
    def __init__(self, email: str, first_name: str, surname: str, salt: uuid.UUID, password_hash: str):
        self.email = email
        self.first_name = first_name
        self.surname =surname
        self.salt = salt
        self.password_hash = password_hash

    def get_username(self) -> str:
        return self.first_name + " " + self.surname

    def __str__(self):
        return self.get_username() + " /email:" + self.email

    def __repr__(self):
        return self.__str__()
