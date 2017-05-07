import unittest
import uuid
import logging

from kai.cassandra.cluster import Cassandra


# test cassandra access
class CassandraCrudTest(unittest.TestCase):
    # initialise the class
    def __init__(self, methodName: str):
        unittest.TestCase.__init__(self, methodName)

    # test cassandra complete CRUD set
    def test_cassandra(self):
        logging.getLogger('cassandra').setLevel(logging.ERROR)
        cassandra = Cassandra({'keyspace': 'kai_test', 'rf': 1, 'host': 'localhost', 'port': 9042})

        # word text, tag text, shard int, sentence_id uuid, offset int, topic text, score double,
        id_list = []
        for i in range(0, 10):
            id = uuid.uuid4()
            cassandra.db_insert("word_index", {"sentence_id": id, "word": "test", "tag": "NN",
                                               "shard": 0, "offset": i, "topic": "test", "score": 1.0})
            id_list.append(id)

        # select with no limits, no pagination
        result_list = cassandra.db_select("word_index", ["sentence_id", "offset", "topic", "score"],
                                          {"word": "test", "shard": 0})
        self.assertTrue(len(result_list) == 10)

        # select with limit
        result_list = cassandra.db_select("word_index", ["sentence_id", "offset", "topic", "score"],
                                          {"word": "test", "shard": 0}, pg_size=3)
        self.assertTrue(len(result_list) == 3)

        # select with offset and limit
        result_list = cassandra.db_select("word_index", ["sentence_id", "offset", "topic", "score"],
                                          {"word": "test", "shard": 0, "topic": "test"},
                                          pg_field="sentence_id", pg_value=id_list[5], pg_size=3)
        self.assertTrue(len(result_list) > 0)

        cassandra.db_delete("word_index", {"sentence_id": id_list[0], "topic": "test", "word": "test", "shard": 0})
        cassandra.db_drop_keyspace()
