from typing import List

from kai.tokenizer.constants import is_whitespace, is_fullstop, is_hyphen
from kai.tokenizer.constants import is_singlequote, is_doublequote, is_specialcharacter
from kai.tokenizer.constants import is_punctuation, is_numeric, is_ABC


class Tokenizer:
    def __init__(self):
        self.punc = {}
        for ch in "!@#$%^&*(){}[],.<>?":
            self.punc[ch] = True

    # turn a string into a list of tokens using pre-defined constants
    def tokenize_string(self, in_str: str) -> List[str]:
        token_list = []
        length = len(in_str)
        i = 0
        tokenIndex = 0
        while i < length:

            tokenHandled = False  # stop when we have the token done
            ch = in_str[i]
            while is_whitespace(ch) and i < length:
                tokenHandled = True
                i = i + 1
                if i < length:
                    ch = in_str[i]

            if tokenHandled:  # single whitespace
                token_list.append(" ")

            # add full-stops?
            while is_fullstop(ch) and i < length:
                tokenHandled = True
                token_list.append(".")
                tokenIndex += 1
                i += 1
                if i < length:
                    ch = in_str[i]

            # add hyphens?
            while is_hyphen(ch) and i < length:
                tokenHandled = True
                token_list.append("-")
                tokenIndex += 1
                i += 1
                if i < length:
                    ch = in_str[i]

            # add single quotes?
            while is_singlequote(ch) and i < length:
                tokenHandled = True
                token_list.append("'")
                tokenIndex += 1
                i += 1
                if i < length:
                    ch = in_str[i]

            # add single quotes?
            while is_doublequote(ch) and i < length:
                tokenHandled = True
                token_list.append("\"")
                tokenIndex += 1
                i += 1
                if i < length:
                    ch = in_str[i]

            # add special characters ( ) etc.
            while is_specialcharacter(ch) and i < length:
                tokenHandled = True
                token_list.append("" + ch)
                tokenIndex += 1
                i += 1
                if i < length:
                    ch = in_str[i]

            # add punctuation ! ? etc.
            while is_punctuation(ch) and i < length:
                tokenHandled = True
                token_list.append("" + ch)
                tokenIndex += 1
                i += 1
                if i < length:
                    ch = in_str[i]

            # numeric processor
            helper = []
            while is_numeric(ch) and i < length:
                tokenHandled = True
                helper.append(ch)
                i += 1
                if i < length:
                    ch = in_str[i]

            if len(helper) > 0:
                token_list.append(''.join(helper))
                tokenIndex += 1

            # text processor
            helper = []
            while is_ABC(ch) and i < length:
                tokenHandled = True
                helper.append(ch)
                i += 1
                if i < length:
                    ch = in_str[i]

            if len(helper) > 0:
                token_list.append(''.join(helper))
                tokenIndex += 1

            # discard unknown token?
            if not tokenHandled:
                token_list.append(ch)
                i += 1  # skip

        return token_list

    # remove spaces from a list of tokens
    def filter_spaces(self, token_list: List[str]) -> List[str]:
        new_token_list = []
        for token in token_list:
            if token != " ":
                new_token_list.append(token)
        return new_token_list

    # remove punctuation from a set
    def filter_punctuation(self, token_list: List[str]) -> List[str]:
        new_token_list = []
        for token in token_list:
            if token not in self.punc:
                new_token_list.append(token)
        return new_token_list
