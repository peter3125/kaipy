import uuid


# session class / object
class Session:
    def __init__(self, first_name: str, surname: str, email: str, session: uuid.UUID):
        self.first_name = first_name
        self.surname = surname
        self.email = email
        self.session =session

    def get_username(self) -> str:
        return self.first_name + " " + self.surname


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


class UnIndex:
    def __init__(self, sentence_id: uuid.UUID, word: str, shard: int):
        self.sentence_id = sentence_id
        self.word = word
        self.shard = shard


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
