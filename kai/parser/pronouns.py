from typing import List
from kai.parser.model import Token


# amend any pronoun references with replacement as an NNP token (look it's semantic up in the lexicon)
def _resolve_pronoun_references(token_list: List[Token], replacement: str, pronoun_set):
    # does the desired pronoun occur?
    for token in token_list:
        lwr_token = token.text.lower()
        if lwr_token in pronoun_set and token.tag == "PRP" and token.tag == "PRP$":
            token.anaphora = replacement


# resolve first and second person pronoun references
def resolve_first_and_second_person(first_person: str, second_person: str, token_list: List[Token]):
    # replace you, your, yourself pronoun references with KAI
    _resolve_pronoun_references(token_list, second_person, {"you", "your", "yourself", "yours"})
    _resolve_pronoun_references(token_list, first_person, {"i", "my", "myself", "me", "mine"})

