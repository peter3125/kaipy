import unittest
from typing import List

from kai.parser.compound_noun import get_longest_word_sequence
from kai.parser.parser_model import Token


# test the longest word algorithm
class CompoundNounTest(unittest.TestCase):
    # initialise the class
    def __init__(self, methodName: str):
        unittest.TestCase.__init__(self, methodName)

    # convert a json block to a token list
    def _json_to_token_list(self,json) -> List[Token]:
        token_list = []
        for token in json:
            token_obj = Token(token["text"], token["index"], token["tag"], token["dep"], token["list"], token["semantic"])
            token_list.append(token_obj)
        return token_list

    # test stemming
    def test_longest_word_1(self):
        tokens = [{"index": 0, "list": [], "tag": "DT", "text": "The", "dep": "ROOT", "synid": -1, "semantic": ""},
                    {"index": 1, "list": [1], "tag": "JJ", "text": "old", "dep": "adj", "synid": -1, "semantic": ""},
                    {"index": 2, "list": [2], "tag": "NN", "text": "lady", "dep": "nsubj", "synid": -1, "semantic": ""}]
        token_list = self._json_to_token_list(tokens)
        self.assertTrue(len(token_list) == 3)

        new_token_list = get_longest_word_sequence(token_list)
        self.assertTrue(len(new_token_list) == 2)
        old_lady = new_token_list[1]
        self.assertTrue(old_lady.tag == "NN")
        self.assertTrue(old_lady.text == "old lady")
        self.assertTrue(old_lady.dep == "nsubj")
        self.assertTrue(len(old_lady.ancestor_list) == 1 and old_lady.ancestor_list[0] == 1)

    # test "billion-dollar grass" hyphenated/space words
    def test_longest_word_2(self):
        tokens = [{"index": 0, "list": [], "tag": "NN", "text": "billion", "dep": "ROOT", "synid": -1, "semantic": ""},
                    {"index": 1, "list": [1], "tag": " ", "text": "-", "dep": "compound", "synid": -1, "semantic": ""},
                    {"index": 2, "list": [2], "tag": "NN", "text": "dollar", "dep": "nsubj", "synid": -1, "semantic": ""},
                    {"index": 3, "list": [3], "tag": "NN", "text": "grass", "dep": "nsubj", "synid": -1, "semantic": ""}]
        token_list = self._json_to_token_list(tokens)
        self.assertTrue(len(token_list) == 4)

        new_token_list = get_longest_word_sequence(token_list)
        self.assertTrue(len(new_token_list) == 1)
        bdg = new_token_list[0]
        self.assertTrue(bdg.tag == "NN")
        self.assertTrue(bdg.text == "billion-dollar grass")

