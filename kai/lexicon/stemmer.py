import kai.res
import logging


stem_set = dict()  #  unstemmed -> stem if exists

# setup plural -> singular
logging.info("loading stems")
with open(kai.res.filename('lexicon/plurals.txt')) as reader:
    for line in reader:
        if not line.startswith("#"):
            line = line.strip()
            parts = line.split(",")
            if len(parts) > 1:
                parent = parts[0].strip()
                for i in range(1, len(parts)):
                    stem_set[parts[i].strip()] = parent

# setup conjugated verb -> base verb
with open(kai.res.filename('lexicon/verbs.txt')) as reader:
    for line in reader:
        if not line.startswith("#"):
            line = line.strip()
            parts = line.split(",")
            if len(parts) > 1:
                parent = parts[0].strip()
                for i in range(1, len(parts)):
                    stem_set[parts[i].strip()] = parent
logging.info("stems loaded")


# get the stem for a word if it exists, otherwise return the word itself
def get_stem(word: str) -> str:
    if word in stem_set:
        return stem_set[word]
    return word
