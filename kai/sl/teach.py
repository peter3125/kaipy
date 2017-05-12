import uuid

from kai.cassandra.model import Session
from kai.parser.parser import Parser, is_imperative, is_question, has_verb
from kai.parser.pronouns import resolve_first_and_second_person
from kai.cassandra.indexes import get_num_search_tokens, index_token_list, remove_indexes
from kai.cassandra.information import save_sentence, delete_sentence
from kai.cassandra.logger import log_entry


parser = Parser()


# teach a fact, returns a message upon completion
def teach(session: Session, text: str) -> str:
    username = session.get_username()
    if 0 < len(text) < 255:
        log_entry(username, "teach:" + text)
        sentence_list = parser.parse_document(text)
        if len(sentence_list) == 0:
            return "Please teach me something, this looks like an empty sentence."
        elif len(sentence_list) > 1:
            return "Teach me using simple single sentences please."

        # replace I and you, references with user and KAI
        sentence_0 = sentence_list[0]
        resolve_first_and_second_person(username, "Kai", sentence_0.token_list)
        if is_imperative(sentence_0.token_list):
            return "That looks like a request or a command rather than information. (your sentence is in the imperative)"
        if is_question(sentence_0.token_list):
            return "That looks like a question, not something I can learn from. (your sentence is a question)"
        if not has_verb(sentence_0.token_list):
            return "I don't understand your statement, can you please change it? (your sentence has no verbs)"
        if get_num_search_tokens(sentence_0.token_list) <= 1:
            return "There is something wrong with this sentence, Please rephrase it. (your sentence does not have enough information)"

        save_sentence(sentence_0, topic=username)  # pk = sentence_id only
        # make it find-able
        index_token_list(topic=username, shard=0, sentence_id=sentence_0.id, token_list=sentence_0.token_list)
        # add it to the global indexes (a sentence's main data is indexed by its id only as pk)
        index_token_list(topic="global", shard=0, sentence_id=sentence_0.id, token_list=sentence_0.token_list)

        return "ok, got that and stored \"%s\" away as factoid \"%s\"." % (text, str(sentence_0.id))
    else:
        return "Text message empty or too large."


# remove a previous teaching
def forget(session: Session, factoid_str: str):
    factoid_id = uuid.UUID("{" + factoid_str + "}")
    username = session.get_username()
    log_entry(username, "forget:" + factoid_str)
    delete_sentence(factoid_id, username)
    # remove both sets of indexes
    remove_indexes(factoid_id, username)
    remove_indexes(factoid_id, "global")
