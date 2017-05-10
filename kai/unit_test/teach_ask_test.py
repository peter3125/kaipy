import unittest
import uuid
import logging

from kai.sl.teach import teach
from kai.sl.ask import ask
from kai.cassandra.model import Session
from kai.cassandra.cluster import Cassandra, set_cassy


# test the parser in general
class TeachAskTest(unittest.TestCase):
    # initialise the class
    def __init__(self, methodName: str):
        unittest.TestCase.__init__(self, methodName)
        self.session = Session("Rock", "de Vocht", "a@b.com", uuid.uuid4())
        self.keyspace = 'kai_teach_ask_test'

    # test scaffold
    def test_setup(self):
        logging.getLogger('cassandra').setLevel(logging.ERROR)
        # remove any pre-existing data
        cassandra = Cassandra({'keyspace': self.keyspace, 'rf': 1, 'host': 'localhost', 'port': 9042}, run_setup=False)
        set_cassy(cassandra)  # set cassandra for API
        cassandra.db_drop_keyspace()
        # then re-create
        cassandra = Cassandra({'keyspace': self.keyspace, 'rf': 1, 'host': 'localhost', 'port': 9042})

        self._teach_ask_1()  # run the actual test

        cassandra.db_drop_keyspace()  # done - remove data

    # test we can teach and ask and get sensible results
    def _teach_ask_1(self):
        result_str = teach(self.session, "Rock de Vocht was here.")
        self.assertTrue("ok, got that and stored" in result_str)

        # and can we ask about it?
        result_list, err_str = ask(self.session, "who was here?")
        self.assertTrue(len(result_list) == 1)
        self.assertTrue("Rock de Vocht was here." in result_list[0].text)
