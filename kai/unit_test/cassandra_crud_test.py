import unittest
import uuid
import logging

from kai.cassandra.cluster import Cassandra, set_cassy


# test cassandra access
class CassandraCrudTest(unittest.TestCase):
    # initialise the class
    def __init__(self, methodName: str):
        unittest.TestCase.__init__(self, methodName)

    # test cassandra complete CRUD set
    def test_cassandra(self):
        logging.getLogger('cassandra').setLevel(logging.ERROR)
        # remove any pre-existing data
        cassandra = Cassandra({'keyspace': 'kai_test', 'rf': 1, 'host': 'localhost', 'port': 9042}, run_setup=False)
        set_cassy(cassandra)  # set cassandra for API
        cassandra.db_drop_keyspace()
        # then re-create
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

        self._test_session()  # test db session system
        self._test_indexing()  # test db indexing system

        cassandra.db_drop_keyspace()  # done - remove data

    # test the session components of the database (private, not executed as a test)
    def _test_session(self):
        import kai.cassandra.session as cs
        import uuid

        guid1 = uuid.uuid4()
        cs.save(guid1, "a@b.c", "Rock", "de Vocht")

        session = cs.get(guid1)
        self.assertTrue(session is not None)
        self.assertTrue(session.surname == "de Vocht")
        self.assertTrue(session.first_name == "Rock")
        self.assertTrue(session.email == "a@b.c")

        cs.delete(guid1)
        session = cs.get(guid1)
        self.assertTrue(session is None)

        guid2 = uuid.uuid4()
        session_2 = cs.get(guid2)
        self.assertTrue(session_2 is None)

    # test the indexing and unindexing system
    def _test_indexing(self):
        from kai.parser.parser import Parser
        from kai.cassandra.indexes import index_token_list, remove_indexes
        from kai.cassandra.indexes import read_indexes_with_filter_for_tokens
        from kai.cassandra.indexes import get_num_search_tokens

        parser = Parser()
        sentence_id =uuid.uuid4()
        token_list = []
        sentence_list = parser.parse_document("This is the test text for Peter.")
        for sentence in sentence_list:
            token_list.extend(sentence.token_list)

        # index the text
        index_token_list("topic", 0, sentence_id, token_list)

        # perform a search
        result_set = read_indexes_with_filter_for_tokens(token_list, "topic", 0)
        self.assertTrue(sentence_id in result_set)
        self.assertTrue(len(result_set[sentence_id]) == get_num_search_tokens(token_list))

        # remove indexes
        remove_indexes(sentence_id, "topic")
        result_set_2 = read_indexes_with_filter_for_tokens(token_list, "topic", 0)
        self.assertTrue(len(result_set_2) == 0)
