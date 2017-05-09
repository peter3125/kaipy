from typing import List
from kai.aiml.manager import AIml_root
from kai.aiml.model import AimlBinding, Aiml
from kai.tokenizer.tokenizer import Tokenizer


tk = Tokenizer()


# enhance AIml with dynamic values that can be used to annotate time, usernames and statistics
def replace_magic_values(match_list: List[AimlBinding], email: str):
    import datetime
    import time
    now = datetime.datetime.now()
    for match in match_list:
        text = match.text
        if "{stats}" in text:  text = text.replace("{stats}", "system statistics: todo")
        if "{year}" in text:  text = text.replace("{year}", str(now.year))
        if "{day}" in text:  text = text.replace("{day}", str(now.day))
        if "{month}" in text:  text = text.replace("{month}", str(now.month))
        if "{time}" in text:  text = text.replace("{time}", time.strftime("%H:%M:%S"))
        if "{email}" in text:  text = text.replace("{email}", email)
        if "{name}" in text:  text = text.replace("{name}", "I can't tell you your name but your email address is " + email)
        if "{star}" in text:  text = text.replace("{star}", ' '.join(match.token_list))
        match.text = text

# helper - finish binding an AIML template
# finish the bindings and set a match_list to return to the caller
def _finish_bind(match_list: List[AimlBinding], origin: str, list: List[str],
                 bindings: List[AimlBinding]) -> List[AimlBinding]:
    final_match_list = []
    for item in list:
        match_list.append(AimlBinding(text=item, origin=origin,token_list=[]))
    if len(bindings) > 0:
        new_match_list = []
        stack_index = bindings[0].offset
        token_list = bindings[0].token_list
        next_stack = -1
        next_index = 1
        if len(bindings) > 1:
            next_stack = bindings[next_index].offset
        for i in range(0, len(match_list)):
            match = match_list[i]
            while next_stack >= 0 and i >= next_stack and next_index < len(bindings):
                token_list = bindings[next_index].token_list
                stack_index = bindings[next_index].offset
                next_index += 1
                if next_index < len(bindings):
                    next_stack = bindings[next_index].offset
                else:
                    next_stack = -1  # no more
            if i >= stack_index and len(token_list) > 0:
                new_match = AimlBinding(text=match.text, offset=match.offset, origin=origin, token_list=token_list)
                new_match_list.append(new_match)
            else:
                new_match_list.append(match)
        for item in new_match_list:
            final_match_list.append(item)
    return final_match_list


# recursively match and bind items with AIML templates from rule as a root
# complicated - jump from node to node with recursion and optional wild-card matching to
# match any possible pattern as fast as possible
def _match(token_list: List[str], index: int, rule: Aiml, match_list: List[AimlBinding],
           binding_list: List[AimlBinding]) -> List[AimlBinding]:
    if len(token_list) > 0 and index < len(token_list) and len(rule.node_set) > 0:
        curr = token_list[index].lower()
        if curr in rule.node_set:  # next token?
            match_list = _match(token_list, index + 1, rule.node_set[curr], match_list, binding_list)
        if "*" in rule.node_set:
            star_list = []
            current = rule.node_set["*"]
            first_current = current
            # start eating text for the wild card
            while index < len(token_list):
                curr_str = token_list[index].lower()
                if curr_str in current.node_set:
                    current = current.node_set[curr_str]
                    index += 1
                    break
                star_list.append(token_list[index])
                index += 1
            # set the binding
            binding_list.append(AimlBinding(origin=first_current.origin, offset=len(match_list), token_list=star_list))
            if index < len(token_list):
                match_list = _match(token_list, index, current, match_list, binding_list)
            else:
                return _finish_bind(match_list, current.origin, current.template_list, binding_list)
        return match_list
    elif len(token_list) > 0 and index == len(token_list):
        if len(rule.template_list) == 0:  # end, but nothing to match
            # hope we have a *
            if "*" not in rule.node_set:
                binding_list.append(AimlBinding(offset=len(match_list), origin=rule.origin, token_list=[]))
                return _finish_bind(match_list, rule.origin, rule.template_list, binding_list)
            else:
                pattern = rule.node_set["*"]
                binding_list.append(AimlBinding(offset=len(match_list), origin=pattern.origin, token_list=[]))
                return _finish_bind(match_list, pattern.origin, pattern.template_list, binding_list)
        else:
            binding_list.append(AimlBinding(offset=len(match_list), origin=rule.origin, token_list=[]))
            return _finish_bind(match_list, rule.origin, rule.template_list, binding_list)
    return match_list


####################################################################################################################

# match a list of tokens against possible entries in the aiml system
# and perform magic value replacement, email is the user's email for those purposes
def match_token_list(token_list: List[str], email=''):
    match_list = []
    filtered_token_list = tk.filter_punctuation(tk.filter_spaces(token_list))
    if len(filtered_token_list) > 0:
        curr = filtered_token_list[0].lower()
        if curr in AIml_root:
            match_list = _match(filtered_token_list, 1, AIml_root[curr], match_list, [])
        replace_magic_values(match_list, email)  # replace any {} magic values
    return match_list
