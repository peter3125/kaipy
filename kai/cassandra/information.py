import uuid
import json
from typing import List
from kai.parser.model import Token, Sentence, sentence_from_dict
from kai.tokenizer.tokenizer import token_list_to_string
from kai.cassandra.cluster import cassy
from kai.cassandra.model import ATResult
from kai.cassandra.indexes import read_indexes_with_filter_for_tokens
from kai.utility.utils import current_datetime_as_string
from kai.sl.json_serialiser import JsonSystem


# save a token list into the system under the given id
def save_sentence(sentence: Sentence, topic: str):
    if len(sentence.token_list) == 0 or len(topic) == 0 or len(sentence.sentence_vec) != 300:
        raise ValueError("invalid sentence or topic")

    value_map = {"id": sentence.id, "topic": topic}
    cassy().db_insert("sentence_by_topic", value_map)

    sentence_json = json.dumps(sentence, cls=JsonSystem)
    token_map = {"id": sentence.id, "topic": topic, "json_data": sentence_json}
    cassy().db_insert("sentence_by_id", token_map)


# remove a token list from the system
def delete_sentence(sentence_id: uuid.UUID, topic: str) -> str:
    cassy().db_delete("sentence_by_topic", {"topic": topic, "id": sentence_id})
    cassy().db_delete("sentence_by_id", {"id": sentence_id})
    return "factoid \"" + str(sentence_id) + "\" removed."


# read a sentence from the db
def get_sentence_by_id(sentence_id: uuid.UUID) -> (Sentence, str):
    where_map = {"id": sentence_id}
    cols = ["json_data", "topic"]
    row_list = cassy().db_select("sentence_by_id", cols, where_map)
    if len(row_list) == 1:
        row = row_list[0]
        json_dict = json.loads(row[0])
        topic = row[1]
        return sentence_from_dict(json_dict), topic
    else:
        return None, ""


# find a token-list match for the given list of tokens and topic
def find_sentence_list(token_list: List[Token], topic: str, shard: int = 0) -> List[ATResult]:
    index_list = read_indexes_with_filter_for_tokens(token_list, topic, shard)
    result_list = []
    for sentence_id in index_list.keys():
        sentence, topic = get_sentence_by_id(sentence_id)
        if len(sentence.token_list) > 0:
            text = token_list_to_string(sentence.token_list)
            result_list.append(ATResult(text, current_datetime_as_string(), topic, sentence_id))
    return result_list
