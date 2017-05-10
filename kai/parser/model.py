from typing import List


# sentence holder, this is what is returned
class Token:
    def __init__(self, text, index, tag, dep, ancestor_list, semantic, anaphora=''):
        self.text = text                        # text of the token
        self.index = index                      # index of the token in the document 0..n
        self.dep = dep                          # the name of the SRL dependency
        self.tag = tag                          # penn tag, ucase
        self.ancestor_list = ancestor_list      # dependency tree parent list
        self.synid = -1                         # synset id (default -1, not set)
        self.semantic = semantic                # semantic of this object
        self.anaphora = anaphora                # anaphora resolution

    def __str__(self):
        ret_str = self.text() + " /tag:" + self.tag + " /dep:" + self.dep + " /index:" + str(self.index)
        if len(self.semantic) > 0:
            ret_str += " /semantic:" + self.semantic
        if len(self.anaphora) > 0:
            ret_str += " /anaphora:" + self.anaphora
        return ret_str

    def __repr__(self):
        return self.__str__()


# json helper, convert a token using a dict
def token_from_dict(d):
    t = Token(d['text'], d['index'], d['tag'], d['dep'], [], '')
    if "parent" in d:
        t.ancestor_list = [d['parent']]
    if "semantic" in d:
        t.semantic = d['semantic']
    if "anaphora" in d:
        t.semantic = d['anaphora']
    if "syn_id" in d:
        t.synid = d['syn_id']
    return t


# a sentence is a list of tokens
class Sentence:
    def __init__(self, token_list: List[Token]):
        self.token_list = token_list

    def len(self):
        return len(self.token_list)

    def get(self, i: int) -> Token:
        return self.token_list[i]

    # get the first semantic found in this sentence
    def get_first_semantic(self):
        for token in self.token_list:
            if len(token.semantic) > 0:
                return token.semantic
        return ""

    def __str__(self):
        return "[" + '], ['.join([str(token) for token in self.token_list]) + "]"

    def __repr__(self):
        return self.__str__()

