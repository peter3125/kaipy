import unittest

from kai.aiml.matcher import match_token_string_list
from kai.tokenizer.tokenizer import Tokenizer


tk = Tokenizer()


# test cassandra access
class AimlTest(unittest.TestCase):
    # initialise the class
    def __init__(self, method_name: str):
        unittest.TestCase.__init__(self, method_name)

    # test AIML loaded can match certain patterns as we'd expect
    def test_match_1(self):
        result_list = match_token_string_list(tk.tokenize_string("activate the robot!"))
        self.assertTrue(len(result_list) == 1)
        self.assertTrue("AI activated. Awaiting your command" in result_list[0].text)

    # test a wildcard with binding data item
    def test_match_2(self):
        result_list = match_token_string_list(tk.tokenize_string("when will you have a body?"))
        self.assertTrue(len(result_list) == 1)
        self.assertTrue("I will finish the robot body as soon as I can raise the funds for it." in result_list[0].text)
        self.assertTrue(len(result_list[0].token_list) == 2)
        self.assertTrue(' '.join(result_list[0].token_list) == "have a")
