from typing import List


# an AIml node with other nodes (node_set) for a multi-branch tree of Aiml patterns
class Aiml:
    def __init__(self, text: str, origin: str, template_list: List[str]):
        self.text = text
        self.origin = origin
        self.template_list = template_list
        self.node_set = {}

    def __repr__(self):
        return self.text + " /from:" + self.origin

    def __str__(self):
        return self.__repr__()


# an AIml binding to a successful match
class AimlBinding:
    def __init__(self, token_list, text: str = '', origin: str = '', offset: int = 0):
        self.text = text
        self.origin = origin
        self.offset = offset
        self.token_list = token_list

    def __repr__(self):
        return self.text + " /from:" + self.origin + " /@" + str(self.offset)

    def __str__(self):
        return self.__repr__()
