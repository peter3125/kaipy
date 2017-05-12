import uuid
import logging
import kai.res
from typing import List

import en_core_web_sm
from kai.lappin_leass.algorithm import LappinLeass
from kai.parser.model import Token, Sentence
from kai.lexicon.compound_noun import get_longest_word_sequence


logging.info("loading spacy")
nlp = en_core_web_sm.load()
logging.info("spacy loaded")

logging.info("loading semantics")
semantics = dict()  # noun -> semantic
for file in kai.res.directory_content('semantics'):
    with open(file, 'r') as reader:
        for line in reader:
            line = line.strip()
            if len(line) > 0 and not line.startswith("#"):
                sem_str = line.split(",")
                if len(sem_str) >= 2:
                    words = sem_str[0:-1]
                    for word in words:
                        semantics[word] = sem_str[-1].lower()
logging.info("semantics loaded")

# verbs for question detection
verbs = {"do", "did", "does", "are", "is", "was", "have", "had"}


# is the token_list a question
def is_question(token_list: List[Token]) -> bool:
    if len(token_list) > 1:  # min sentence size
        if token_list[-1].text == "?":
            return True

        token0 = token_list[0]
        if "VB" in token0.tag:
            if token0.text.lower() in verbs:
                return True
        # any of the tokens is a WDT tag?
        for token in token_list:
            if token.tag == "WDT" or token.tag == "WP":
                return True
    return False


# is the sentence an imperative sentence?
def is_imperative(token_list: List[Token]) -> bool:
    if len(token_list) > 1:  # min sentence size
        if token_list[-1].text == "?":
            return False
        token0 = token_list[0]
        if token0.tag == "VB" or token0.tag == "VBP":
            return True
    return False


# check this set of tokens has verbs in it
def has_verb(token_list: List[Token]) -> bool:
    num_verbs = 0
    if len(token_list) > 1:  # min sentence size
        for token in token_list:
            if token.tag.startswith("VB"):
                num_verbs += 1
    return num_verbs > 0


# the text parser
class Parser:
    def __init__(self):
        self.en_nlp = nlp
        self.semantics = semantics
        self.ll = LappinLeass()

    # cleanup text to ASCII to avoid nasty python UTF-8 errors
    def cleanup_text(self, data):
        try:
            return data.decode("utf-8")
        except:
            text = ""
            for ch in data:
                if 32 <= ch <= 255:
                    text += chr(ch)
                else:
                    text += " "
            return text

    # convert from spacy to the above Token format for each sentence
    def _convert_sentence(self, sent):
        token_list = []
        for token in sent:
            ancestors = []
            for an in token.ancestors:
                ancestors.append(str(an.i))
            text = str(token)
            semantic = ''
            if token.tag_ == "NN" or token.tag_ == "NNS" or token.tag_ == "NNP" or token.tag_ == "NNPS":
                if text in self.semantics:
                    semantic = self.semantics[text]
            token_list.append(Token(text, token.i, token.tag_, token.dep_, ancestors, semantic))
        sentence_vec = [float(item) for item in sent.vector]  # convert to ordinary floats and array
        return Sentence(uuid.uuid4(), token_list, sentence_vec)

    # remove spaces from a sentence
    def remove_spaces(self, sentence: Sentence):
        return Sentence(sentence.id, [item for item in sentence.token_list if item.text != ' '], sentence.sentence_vec)

    # convert a document to a set of entity tagged, pos tagged, and dependency parsed entities
    def parse_document(self, text) -> List[Sentence]:
        doc = self.en_nlp(text)
        sentence_list = []
        for sent in doc.sents:
            sentence = self.remove_spaces(self._convert_sentence(sent))
            sentence_list.append(sentence)
        self.ll.resolve_pronouns(sentence_list)  # resolve anaphora where possible
        return_sentence_list = []
        for sentence in sentence_list:
            return_sentence_list.append(Sentence(sentence.id, get_longest_word_sequence(sentence.token_list),
                                                 sentence.sentence_vec))
        return return_sentence_list

