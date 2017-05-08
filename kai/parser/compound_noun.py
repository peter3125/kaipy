from typing import List
import logging
import kai.res

from kai.parser.parser_model import Token, Sentence


logging.info("loading compound nouns")
compoundWord = dict()

# add a word as a compound word
def _add_compound(word):
    final_list = []
    parts = word.split(' ')
    for part in parts:
        if "-" in part:  # special double space adding for hyphens for longest word analysis
            sub_parts = part.split('-')
            for i in range(0, len(sub_parts)):
                sub_part = sub_parts[i]
                final_list.append(sub_part)
                if i + 1 < len(sub_parts):
                    final_list.append('-')
        elif "'" in part:  # special double space adding for single quotes for longest word analysis
            sub_parts = part.split("'")
            for i in range(0, len(sub_parts)):
                sub_part = sub_parts[i]
                final_list.append(sub_part)
                if i + 1 < len(sub_parts):
                    final_list.append("'")
        else:
            final_list.append(part)
    if len(final_list) > 0:
        new_word = ' '.join(final_list)
        compoundWord[new_word.lower()] = final_list

with open(kai.res.filename('data/compound-nouns.txt')) as reader:
    for line in reader:
        line = line.strip()
        if len(line) > 0:
            _add_compound(line)

logging.info("compound nouns loaded")


# hold return values of the getLargestMatching system
class MatchingResult:
    # maximum length of a word made up
    maxWordConstituentLength = 10

    def __init__(self, new_index: int, matching_token: Token):
        self.new_index = new_index
        self.matching_token = matching_token


# turn a compound word from a list of strings into a string taking into account hyphens
def to_string(list: List[str]) -> str:
    result_str = ""
    prev = ""
    for i in range(0, len(list)):
        curr = list[i]
        next = ""
        if i + 1 < len(list):
            next = list[i+1]
        if not(next == "-" or prev == "-" or curr == "-"):
            result_str += " "
        result_str += curr
        prev = curr
    return result_str.strip()


# find the longest sequence of words for a compound noun
def get_longest_word_sequence(token_list: List[Token]) -> List[Token]:
    new_token_list = []
    remap = dict()
    i = 0
    while i < len(token_list):
        word = token_list[i].text
        if len(word) > 0:
            result = _get_largest_matching(token_list, i, remap)
            if result.new_index > i:
                new_token_list.append(result.matching_token)
                i = result.new_index
            else:
                new_token_list.append(token_list[i])
                i += 1
        else:
            i += 1
    if len(remap) > 0:
        for token in new_token_list:
            for j in range(0, len(token.ancestor_list)):
                value = token.ancestor_list[j]
                if value in remap:
                    token.ancestor_list[j] = remap[value]
    return new_token_list

# Return the number of differences in case for two identical words
def _diffs_in_case(str1: str, str2: str) -> int:
    if len(str1) == len(str2):  # sanity check
        num_diff = 0
        for i in range(0, len(str1)):
            if str1[i] != str2[i]:
                num_diff += 1
        return num_diff
    return max(len(str1),len(str2))  # return the length of the biggest of the two

# given a word, and items in a list from the lexicon, filter out those items
# (if possible) that do not conform enough to the case wanted
def _filter_by_case(match_list: List[str], word: str, is_start_of_sentence: bool) -> List[str]:
    if len(word) > 0 and len(match_list) > 1:
        new_token_list = []
        check_size = 0  # one difference allowed for words @ start of sentence
        if is_start_of_sentence:  check_size = 1
        if len(word) == 1:  check_size = 0
        right_case_count = 0
        for token in match_list:
            if _diffs_in_case(token, word) <= check_size:
                right_case_count += 1
                new_token_list.append(token)
        if right_case_count == 0 or right_case_count == len(match_list):
            return match_list
        return new_token_list
    return match_list

# get the largest matching item from the lexicon
# remap: for remapping ancestors id_that_no_longer_exists -> correct_id
def _get_largest_matching(token_list: List[Token], index: int, remap: dict) -> MatchingResult:
    size = MatchingResult.maxWordConstituentLength
    if index + size > len(token_list):
        size = len(token_list) - index
    result_list = []
    result_size = 0

    sb = ""
    for i in range(0, size):
        token = token_list[index + i]
        word = token.text
        if len(word) > 0:
            sb += word
            if sb.lower() in compoundWord:
                result_list = compoundWord[sb.lower()]
                result_size = i + 1
            sb += " "

    if result_size > 1 and len(result_list) > 0:
        token = token_list[index]
        # find the noun token if there is one in this set - avoid using adjectives as main markers
        offset = index
        if offset < (index + result_size) and "NN" not in token.tag:
            offset += 1
            token = token_list[offset]
        if "NN" not in token.tag:
            token = token_list[index]
        matching_token = Token(to_string(result_list), token.index, token.tag, token.dep, token.ancestor_list,
                               token.semantic, token.anaphora)
        matching_token.semantic = token.semantic
        for i in range(index + 1, index + result_size):
            remap[i] = index
        return MatchingResult(index + result_size, matching_token)
    return MatchingResult(index, token_list[index])


# find the longest sequence of words for a compound noun for a set of sentences
def get_longest_word_sequence_for_list(sentence_list: List[Sentence]) -> List[Sentence]:
    new_sentence_list = []
    for sentence in sentence_list:
        new_sentence_list.append(Sentence(get_longest_word_sequence(sentence.token_list)))
    return new_sentence_list

