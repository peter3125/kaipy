from typing import List

import unittest

from kai.parser.model import Token, Sentence
from kai.lappin_leass.algorithm import LappinLeass


class TestLappinLeass(unittest.TestCase):
    # initialise the class
    def __init__(self, methodName: str):
        unittest.TestCase.__init__(self, methodName)
        self.ll = LappinLeass()

    # helper: check the anaphora are resolved as expected
    def _check_pronoun_reference(self, sentence_list: List[Sentence], anaphora: str, words: List[str]):
        for sentence in sentence_list:
            for t_token in sentence.token_list:
                if t_token.text.lower() in words:
                    self.assertEqual(t_token.anaphora, anaphora)

    # convert a json block to a sentence list
    def _json_to_sentence_list(self,json) -> List[Sentence]:
        sentence_list = []
        for sentence in json:
            token_list = []
            for token in sentence:
                token_obj = Token(token["text"], token["index"], token["tag"], token["dep"], token["list"], token["semantic"])
                if "anaphora" in token:
                    token_obj.anaphora = token["anaphora"]
                token_list.append(token_obj)
            sentence_list.append(Sentence(token_list))
        return sentence_list

    # test Lappin Leass algorithm - simple single sentence resolution
    def test_ll1(self):

        self.assertTrue(self.ll.n_back > 0)   # setup

        # John said he likes dogs
        s_list_1 = [[{"index":0,"list":[1],"tag":"NNP","text":"John","dep":"nsubj","semantic":"male"},
                     {"index":1,"list":[],"tag":"VBD","text":"said","dep":"ROOT","semantic":""},
                     {"index":2,"list":[3,1],"tag":"PRP","text":"he","dep":"nsubj","semantic":""},
                     {"index":3,"list":[1],"tag":"VBZ","text":"likes","dep":"ccomp","semantic":""},
                     {"index":4,"list":[3,1],"tag":"NNS","text":"dogs","dep":"dobj","semantic":""}]]

        sentence_list_1 = self._json_to_sentence_list(s_list_1)
        self.assertTrue(len(sentence_list_1) == 1)

        # check that we can detect the pronoun
        self.assertTrue(self.ll.has_pronoun(sentence_list_1[0]))

        # resolve the pronoun
        self.assertTrue(self.ll.resolve_pronouns(sentence_list_1) == 1)

        # check its the right one
        self.assertTrue(sentence_list_1[0].token_list[2].anaphora == "John")

    # test Lappin Leass algorithm - simple single sentence resolution with previously set anaphora on the NNP
    def test_ll2(self):

        self.assertTrue(self.ll.n_back > 0)   # setup

        # John said he likes dogs
        s_list_1 = [[{"index":0,"list":[1],"tag":"NNP","text":"John","dep":"nsubj","semantic":"male",
                                "anaphora": "John Carpenter"},
                     {"index":1,"list":[],"tag":"VBD","text":"said","dep":"ROOT","semantic":""},
                     {"index":2,"list":[3,1],"tag":"PRP","text":"he","dep":"nsubj","semantic":""},
                     {"index":3,"list":[1],"tag":"VBZ","text":"likes","dep":"ccomp","semantic":""},
                     {"index":4,"list":[3,1],"tag":"NNS","text":"dogs","dep":"dobj","semantic":""}]]

        sentence_list_1 = self._json_to_sentence_list(s_list_1)
        self.assertTrue(len(sentence_list_1) == 1)

        # check that we can detect the pronoun
        self.assertTrue(self.ll.has_pronoun(sentence_list_1[0]))

        # resolve the pronoun
        self.assertTrue(self.ll.resolve_pronouns(sentence_list_1) == 1)

        # check its the right one
        self.assertTrue(sentence_list_1[0].token_list[2].anaphora == "John Carpenter")


