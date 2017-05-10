from random import randint
from typing import List

from kai.cassandra.model import Session
from kai.cassandra.logger import log_entry
from kai.parser.parser import Parser, is_imperative, is_question
from kai.parser.pronouns import resolve_first_and_second_person
from kai.cassandra.indexes import get_num_search_tokens
from kai.cassandra.information import find_token_list
from kai.aiml.matcher import match_token_string_list
from kai.sl.model import convert_aiml_binding, ATResult


parser = Parser()


# ask a question and get an answer;  uses QA  information system and AIml to answer questions
# that have been previously taught or are available through AIml
def ask(session: Session, text: str) -> (List[ATResult], str):
    ask_teach_result = []
    username = session.get_username()
    if 0 < len(text) < 255:
        log_entry(username, "ask:" + text)

        sentence_list = parser.parse_document(text)
        if len(sentence_list) == 0:
            return [], "Please ask me a proper question."
        elif len(sentence_list) > 1:
            return [], "Question too complex, more than one sentence."

        token_list = sentence_list[0].token_list
        if not is_question(token_list) and not is_imperative(token_list):
            return [], "That does not look like a question.  Ask me question or give me a command please."

        # 1. AIml query
        aiml_result = match_token_string_list([token.text for token in token_list], session.email)
        if len(aiml_result) > 0:
            ar = aiml_result[0]
            # more than one binding?  pick a random result
            if len(aiml_result) > 1:
                ar = aiml_result[randint(0, len(aiml_result))]
            ask_teach_result.append(convert_aiml_binding(ar))

        # resolve first and second person before the db query
        resolve_first_and_second_person(username, "Kai", token_list)

        # 2. db search
        if get_num_search_tokens(token_list) > 1:
            ask_teach_result.extend(find_token_list(token_list, username, 0))

    return ask_teach_result, ""
