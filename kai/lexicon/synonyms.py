import kai.res
import logging
from typing import List

synonym_set = dict()  # synonym sets


# add a synonym
def _add_syn(p1: str, p2: str):
    if p1 in synonym_set:
        if p2 not in synonym_set[p1]:
            synonym_set[p1].append(p2)
    else:
        synonym_set[p1] = [p2]
    if p2 in synonym_set:
        if p1 not in synonym_set[p2]:
            synonym_set[p2].append(p1)
    else:
        synonym_set[p2] = [p1]

# setup synonyms:  str -> [words]
logging.info("loading synonyms")

with open(kai.res.filename('lexicon/synonyms.txt')) as reader:
    for line in reader:
        if not line.startswith("#"):
            line = line.strip()
            parts = line.split(",")
            for part_1 in parts:
                for part_2 in parts:
                    if part_1 != part_2:
                        _add_syn(part_1, part_2)

logging.info("synonyms loaded")


# get synonyms for word
def get_synonym_list(word: str) -> List[str]:
    if word in synonym_set:
        return synonym_set[word]
    return []

