from typing import List
import kai.res
import os
import xml.etree.ElementTree
from kai.tokenizer.tokenizer import Tokenizer
from kai.aiml.expand_pattern import expand_brackets
from kai.aiml.model import Aiml


AIml_root = dict()
tk = Tokenizer()


# recursively chain new nodes into the existing tree that is aiml_root using node as a current pointer
def _add_pattern_helper(node: Aiml, origin: str, index: int, token_list: List[str], template_list: List[str]):
    if index + 1 == len(token_list):  # last item
        key = token_list[index].lower()
        if not key in node.node_set:
            template = Aiml(key, origin, [])
            for item in template_list:
                template.template_list.append(item)
            node.node_set[key] = template
        else:  # existing template, all these sets are alternatives
            for item in template_list:
                node.node_set[key].template_list.append(item)
    elif index < len(token_list):
        key = token_list[index].lower()
        if not key in node.node_set:
            template = Aiml(key, origin, [])
            node.node_set[key] = template
        else:
            template = node.node_set[key]
        _add_pattern_helper(template, origin, index + 1, token_list, template_list)


# add a new aiml pattern direct from file parse
def _add_pattern(pattern_list, template_list, aiml_name: str):
    for pattern_1 in pattern_list:
        expanded_pattern = expand_brackets(pattern_1)
        for pattern in expanded_pattern:
            token_list = tk.filter_punctuation(tk.filter_spaces(tk.tokenize_string(pattern)))
            if len(token_list) > 0:
                t0 = token_list[0].lower()
                if t0 == "*":  raise ValueError("pattern cannot start with *")
                if t0 not in AIml_root:
                    root = Aiml(t0, aiml_name, [])
                    AIml_root[t0] = root
                _add_pattern_helper(AIml_root[t0], aiml_name, 1, token_list, template_list)

####################################################################################################################

# process all AIML files
for aiml_file in kai.res.directory_content('aiml'):
    aiml_name = str(os.path.basename(aiml_file).split('.')[0])
    e = xml.etree.ElementTree.parse(aiml_file).getroot()
    for category in e.findall('category'):
        pattern_list = []
        for pattern in category.findall('pattern'):
            pattern_list.append(pattern.text)
        template_list = []
        for template in category.findall('template'):
            if template.text is not None:
                for sub_text in template.text.split("|"):
                    template_list.append(sub_text.strip())
        _add_pattern(pattern_list, template_list, aiml_name)
