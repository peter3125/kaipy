import unittest

from kai.parser.parser import Parser


# test the parser in general
class ParserTest(unittest.TestCase):
    # initialise the class
    def __init__(self, methodName: str):
        unittest.TestCase.__init__(self, methodName)
        self.parser = Parser()

    # test we can parse and words are compounded and spaces are removed
    def test_parser_1(self):
        sentence_list = self.parser.parse_document("Peter de Vocht was here.  He then moved to Wellington.")
        self.assertTrue(len(sentence_list) == 2)

        sentence_1 = sentence_list[0]
        self.assertTrue(len(sentence_1.token_list) == 6 and len(sentence_1.sentence_vec) == 300)

        sentence_2 = sentence_list[1]
        self.assertTrue(len(sentence_2.token_list) == 6 and len(sentence_2.sentence_vec) == 300)

    # test the parser's text cleaner
    def test_parser_2(self):
        sentence_list = self.parser.parse_document("“What is his name?”")
        self.assertTrue(len(sentence_list) == 1)
        self.assertTrue(len(sentence_list[0].token_list) == 7)
        self.assertTrue(len(sentence_list[0].sentence_vec) == 300)

    # test the parser's semantic for mr. mrs. and other compounds
    def test_parser_4(self):
        sentence_list = self.parser.parse_document("He is referred to as Mr. Woodhouse.")
        self.assertTrue(len(sentence_list) == 1)
        self.assertTrue(len(sentence_list[0].token_list) == 8)
        self.assertTrue(sentence_list[0].token_list[5].text == "Mr." and
                        sentence_list[0].token_list[5].semantic== "male")
        self.assertTrue(len(sentence_list[0].sentence_vec) == 300)

    # test the parser's semantic for mr. mrs. and other compounds
    def test_parser_5(self):
        sentence_list = self.parser.parse_document("He is referred to as mister Woodhouse.")
        self.assertTrue(len(sentence_list) == 1)
        self.assertTrue(len(sentence_list[0].token_list) == 8)
        self.assertTrue(sentence_list[0].token_list[5].text == "mister" and
                        sentence_list[0].token_list[5].semantic== "male")
        self.assertTrue(len(sentence_list[0].sentence_vec) == 300)

    # test the parser's semantic for mr. mrs. and other compounds
    def test_parser_6(self):
        sentence_list = self.parser.parse_document("She is referred to as Mrs. Woodhouse.")
        self.assertTrue(len(sentence_list) == 1)
        self.assertTrue(len(sentence_list[0].token_list) == 8)
        self.assertTrue(sentence_list[0].token_list[5].text == "Mrs." and
                        sentence_list[0].token_list[5].semantic== "female")
        self.assertTrue(len(sentence_list[0].sentence_vec) == 300)

    # test the parser's semantic for mr. mrs. and other compounds
    def test_parser_7(self):
        sentence_list = self.parser.parse_document("She is referred to as Miss Woodhouse.")
        self.assertTrue(len(sentence_list) == 1)
        self.assertTrue(len(sentence_list[0].token_list) == 8)
        self.assertTrue(sentence_list[0].token_list[5].text == "Miss" and
                        sentence_list[0].token_list[5].semantic== "female")
        self.assertTrue(len(sentence_list[0].sentence_vec) == 300)
