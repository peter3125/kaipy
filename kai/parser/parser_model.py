import json
from typing import List


# sentence holder, this is what is returned
class Token:
    def __init__(self, text, index, tag, dep, ancestor_list, semantic):
        self.text = text                        # text of the token
        self.index = index                      # index of the token in the document 0..n
        self.dep = dep                          # the name of the SRL dependency
        self.tag = tag                          # penn tag, ucase
        self.ancestor_list = ancestor_list      # dependency tree parent list
        self.synid = -1                         # synset id (default -1, not set)
        self.semantic = semantic                # semantic of this object
        self.anaphora = ''                      # anaphora resolution


# a sentence is a list of tokens
class Sentence:
    def __init__(self, token_list: List[Token]):
        self.token_list = token_list

    def len(self):
        return len(self.token_list)

    def get(self, i: int) -> Token:
        return self.token_list[i]


# simple json encoder
class JsonSystem(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Token):
            return {'text': obj.text, 'index': obj.index, 'synid': obj.synid,
                    'semantic': obj.semantic, 'tag': obj.tag, 'dep': obj.dep,
                    'list': obj.ancestor_list, 'anaphora': obj.anaphora}
        elif isinstance(obj, Sentence):
            return {'token_list': obj.token_list}
        return json.JSONEncoder.default(self, obj)
