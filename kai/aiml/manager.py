import logging
from typing import List
import kai.res
import os
import xml.etree.ElementTree
from kai.tokenizer.tokenizer import Tokenizer
from kai.aiml.expand_pattern import expand_brackets


aim_set = dict()
tk = Tokenizer()


class Aiml:
    def __init__(self, text: str, origin: str, template_list: List[str]):
        self.text = text
        self.origin = origin
        self.template_list = template_list


class AimlBinding:
    def __init__(self, text: str, origin: str, offset: int, token_list):
        self.text = text
        self.origin = origin
        self.offset = offset
        self.token_list = token_list


# add a new aiml pattern
def add_pattern(pattern_list, template_list, aiml_name: str):
    for pattern_1 in pattern_list:
        expanded_pattern = expand_brackets(pattern_1)
        for pattern in expanded_pattern:
            token_list = tk.filter_punctuation(tk.filter_spaces(tk.tokenize_string(pattern)))


# process all AIML files
for aiml_file in kai.res.directory_content('aiml'):
    aiml_name = str(os.path.basename(aiml_file).split('.')[0])
    try:
        e = xml.etree.ElementTree.parse(aiml_file).getroot()
        for category in e.findall('category'):
            pattern_list = []
            for pattern in category.findall('pattern'):
                pattern_list.append(pattern.text)
            template_list = []
            for template in category.findall('template'):
                template_list.append(template.text)
            add_pattern(pattern_list, template_list, aiml_name)
    except:
        pass
