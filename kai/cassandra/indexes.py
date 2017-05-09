import uuid
from typing import List
from kai.parser.model import Token
from kai.cassandra.cluster import cassy
from kai.cassandra.model import Index, UnIndex, IndexMatch
from kai.lexicon.stemmer import get_stem
from kai.lexicon.undesirables import is_undesirable


# add an index into the system, and its unindex equivalent for later removal
def add_index(sentence_id: uuid.UUID, word: str, tag: str, shard: int, topic: str, offset: int, score: float):
    # add the index
    value_set = {"sentence_id": sentence_id, "word": word, "tag": tag, "shard": shard,
                 "offset": offset, "topic": topic, "score": score}

    cassy().db_insert("word_index", value_set)

    # add the unindex
    # url text, origin text, shard int, word text, kb text,
    # primary key((url,origin,kb), word, shard)
    u_value_set = {"sentence_id": sentence_id, "word": word, "shard": shard}
    cassy().db_insert("word_unindex", u_value_set)


# read indexes using word and meta-data fields
def read_indexes(word: str, topic: str, shard: int):
    return_list = []
    columns = ["sentence_id", "offset", "tag", "score"]
    where_map = {"word": word.lower(), "shard": shard, "topic": topic}

    result_rows = cassy().db_select("word_index", columns, where_map)
    for row in result_rows:
        return_list.append(Index(row[0], word, row[2], shard, row[1], topic, row[3]))

    return return_list


# read the list of un-indexes for a url / origin / kb
def read_unindexes(sentence_id: uuid.UUID):
    return_list = []
    columns = ["word", "shard"]
    where_map = {"sentence_id": sentence_id}

    result_rows = cassy().db_select("word_unindex", columns, where_map)
    for row in result_rows:
        return_list.append(UnIndex(sentence_id, row[0], row[1]))

    return return_list


# remove an index using an unindex
def delete_index(topic: str, unidx: UnIndex):
    where_map = {"topic": topic, "word": unidx.word, "shard": unidx.shard, "sentence_id": unidx.sentence_id}
    cassy().db_delete("word_index", where_map)


# remove an unindex
def delete_unindex(sentence_id: uuid.UUID):
    where_map = {"sentence_id": sentence_id}
    cassy().db_delete("word_unindex", where_map)


# remove indexes for a sentence/topic pair
def remove_indexes(sentence_id: uuid.UUID, topic: str):
    # read the unindexes first
    unindex_list = read_unindexes(sentence_id)
    for unindex in unindex_list:
        # delete each word/topic
        delete_index(topic, unindex)

    delete_unindex(sentence_id)


# index a token list
def index_token_list(topic: str, shard: int, sentence_id: uuid.UUID, token_list: List[Token]):
    if len(topic) > 0 and len(token_list) > 0:
        offset = 0
        score = 1.0
        for token in token_list:
            stemmed = get_stem(token.text)
            # don't index aux verbs
            if not is_undesirable(stemmed) and token.tag != "AUX":
                add_index(sentence_id, stemmed, token.tag, shard, topic, offset, score)

                # also index sub parts of compound words like "New York" -> "New" and "York"
                # spaces in the token (multi word index)
                parts = []
                if " " in token.text:
                    parts.extend(token.text.split(" "))
                if "-" in token.text:
                    parts.extend(token.text.split("-"))

                if len(parts) > 1:
                    for part in parts:
                        part_lcase = part.lower()
                        if len(part_lcase) > 0 and not is_undesirable(part_lcase):
                            # add an index for parts of the words
                            add_index(sentence_id, part_lcase, token.tag, shard, topic, offset, score * 0.5)

                # also index semantics of words as a reference, e.g. "New York":city -> index city reference
                if len(token.semantic) > 0:
                    token_semantic = token.semantic.lower()
                    if len(token_semantic) > 0 and not is_undesirable(token_semantic):
                        add_index(sentence_id, token_semantic, token.tag, shard, topic, offset, score * 0.5)

            offset += 1


# are the two tags compatible
def _compatible_tag(tag1: str, tag2: str) -> bool:
    if len(tag1) >= 2 and len(tag2) >= 2:
        if tag1.startswith("NN") or tag2.startswith("NN"):
            # either matching nouns, or one of them is an adjective (e.g. blue can be a noun or JJ depending on use)
            return tag1[0:2] == tag2[0:2] or tag1[0:2] == "JJ" or tag2[0:2] == "JJ"

        if tag1.startswith("VB") or tag2.startswith("VB"):
            return tag1[0:2] == tag2[0:2]

        return True  # all other cases are ok, including missing tags


# read a set of indexes using words as a filter for a specific set of meta-data
# @param organisation_id the id of the organisation to read from
# @param tokenList a parsed + filtered set of tokens to search through the indexes
# @param shard the shard of the index
# @return a list of URLs that matched
def read_indexes_with_filter_for_tokens(token_list: List[Token], topic: str, shard: int):
    combined_indexes = dict()
    i = 0
    for token in token_list:  # for each token
        stemmed = get_stem(token.text)
        if not is_undesirable(stemmed):  # must be index-able
            indexes = read_indexes(stemmed, topic, shard)  # read the indexes

            if len(indexes) == 0:
                return dict()  # nothing returned - failed straight away
            elif i == 0:  # first index all items just added
                for index in indexes:
                    if _compatible_tag(token.tag, index.tag):
                        if index.sentence_id in combined_indexes:
                            list = combined_indexes[index.sentence_id]
                            list.append(IndexMatch(index.sentence_id, index.word, index.tag, index.shard, index.offset,
                                                   index.topic, index.score, i))
                        else:
                            combined_indexes[index.sentence_id] = []
                            combined_indexes[index.Sentence_id].append(IndexMatch(index.sentence_id, index.word,
                                                                                  index.tag, index.shard, index.offset,
                                                                                  index.topic, index.score, i))

            elif i > 0:
                # all other rounds are intersection rounds
                new_combined_indexes = dict()
                for index in indexes:
                    if _compatible_tag(token.tag, index.tag):
                        if index.sentence_id in combined_indexes:
                            list =combined_indexes[index.sentence_id]

                            new_combined_indexes[index.sentence_id] = []
                            for item in list:
                                new_combined_indexes[index.sentence_id].append(item)

                            new_combined_indexes[index.sentence_id].append(IndexMatch(index.sentence_id, index.word,
                                                                            index.tag, index.shard, index.offset,
                                                                            index.topic, index.score, i))

                combined_indexes = new_combined_indexes
                if len(combined_indexes) == 0:
                    return dict()  # failed after combining indexes - nothing left

            i += 1

    return combined_indexes


# return the number of search tokens
def get_num_search_tokens(token_list: List[Token]) -> int:
    count = 0
    for token in token_list:
        stemmed = get_stem(token.text)  # unstem it
        if not is_undesirable(stemmed):
            count += 1
    return count
