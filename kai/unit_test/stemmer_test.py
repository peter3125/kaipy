import unittest

from kai.lexicon.stemmer import get_stem


# test the stemmer lexicon system
class StemmerTest(unittest.TestCase):
    # initialise the class
    def __init__(self, methodName: str):
        unittest.TestCase.__init__(self, methodName)

    # test the stemmer
    def test_stems_1(self):
        self.assertTrue(get_stem("fought") == "fight")
        self.assertTrue(get_stem("busses") == "bus")
