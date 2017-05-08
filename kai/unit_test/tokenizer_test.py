import unittest

from kai.tokenizer.tokenizer import Tokenizer


# test the tokenizer
class TokenizerTest(unittest.TestCase):
    # initialise the class
    def __init__(self, methodName: str):
        unittest.TestCase.__init__(self, methodName)
        self.tokenizer = Tokenizer()

    # test we can parse and words are compounded and spaces are removed
    def test_tokenizer_1(self):
        token_list = self.tokenizer.tokenize_string("This, is a  test string.  Is what I mean   to talk about?")
        self.assertTrue(len(token_list) == 26)

    # and test filter spaces
    def test_tokenizer_2(self):
        token_list = self.tokenizer.filter_spaces(self.tokenizer.tokenize_string("This, is a  test string.  Is what I mean   to talk about?"))
        self.assertTrue(len(token_list) == 15)
