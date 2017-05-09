import unittest

from kai.lexicon.synonyms import get_synonym_list


# test the synonym system
class SynonymTest(unittest.TestCase):
    # initialise the class
    def __init__(self, methodName: str):
        unittest.TestCase.__init__(self, methodName)

    # test we can get a list of synonyms
    def test_synonyms_1(self):
        synonym_list = get_synonym_list("saltation")
        self.assertTrue("terpsichore" in synonym_list)
        self.assertTrue("dance" in synonym_list)
        self.assertTrue("dancing" in synonym_list)
