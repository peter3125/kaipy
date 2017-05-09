import logging
import math
from typing import List

from kai.parser.model import Token, Sentence


# TODO:  pleonastic pronoun detection
# see:  https:#code.google.com/archive/p/nada-nonref-pronoun-detector/

#
# Anaphora Resolution
#
# see: https:#www.cl.cam.ac.uk/teaching/1011/L104/lec12-2x2.pdf
# Two different operations are performed:
#
# Maintaining and updating a discourse model consisting of a set of co-reference classes:
# * Each co-reference class corresponds to one entity that has been evoked in the discourse
# * Each co-reference class has an updated salience value
#
# Resolving each Pronoun from left to right
# * Collect potential referents from up to 4 sentences back
# * Filter out coreference classes that don’t satisfy  agreement/syntax constraints
# * Select remaining co-reference class with the highest salience value; add pronoun to class.
#
# The salience of a referent is calculated on the basis of recency and grammatical function.
# Salience Factor        Example                          Weight
# Current sentence                                          100
# Subject emphasis       John opened the door                80
# Existential emphasis   There was a dog standing outside    70
# Accusative emphasis    John liked the dog                  50
# Indirect object        John gave a biscuit to the dog      40
# Adverbial emphasis     Inside the house, the cat looked on 50
# Head Noun emphasis     The cat in the house looked on      80

# The salience of a referent is the sum of all applicable weights
# The salience of a referent is halved each time a sentence  boundary is crossed
# This, along with the weight for being in the current sentence,  makes more recent referents more salient
# Weights are calculated for each member of the salience class
# Previous mentions can boost the salience of a coreference class
# This accounts for the repetition effect
# Lappin and Leass report 86% accuracy for their algorithm on a corpus of Computer manuals


# referent class for storing temp linkages
class LLReferent:
    def __init__(self, anaphora: str, salience: float):
        self.anaphora = anaphora
        self.salience = salience


# a pronoun capture structure
class LLPronoun:
    def __init__(self, text: str, semantics: List[str], number: str):
        self.text = text                # the pronoun's text (e.g. "he")
        self.semantics = semantics      # specific semantics, one of {"man', "woman", "person", or "other"}, where other will match anything
        self.number = number            # the pronoun's pluraity, one of {"s", "p"}  (singular/plural)

    # does this item contain semantic?
    def contains_semantic(self, semantic: str) -> bool:
        return semantic in self.semantics


logging.info("setup Lappin-Leass")
pronoun_set_map = dict()  # list of pronouns to look for in the text (ones we can resolve)

pronoun_set_map["he"] = LLPronoun("he", ["male", "person"], "s")
pronoun_set_map["she"] = LLPronoun("she", ["female", "person"], "s")
pronoun_set_map["it"] = LLPronoun("it", ["other"], "s")

pronoun_set_map["him"] = LLPronoun("him", ["male", "person"], "s")
pronoun_set_map["her"] = LLPronoun("her", ["female", "person"], "s")

pronoun_set_map["himself"] = LLPronoun("himself", ["male", "person"], "s")
pronoun_set_map["herself"] = LLPronoun("herself", ["female", "person"], "s")
pronoun_set_map["itself"] = LLPronoun("itself", ["other"], "s")

pronoun_set_map["his"] = LLPronoun("his", ["male", "person"], "s")
pronoun_set_map["her"] = LLPronoun("her", ["female", "person"], "s")
pronoun_set_map["hers"] = LLPronoun("hers", ["female", "person"], "s")
pronoun_set_map["its"] = LLPronoun("its", ["other"], "s")

pronoun_set_map["they"] = LLPronoun("they", ["other"], "p")
pronoun_set_map["them"] = LLPronoun("them", ["person", "female", "male", "other"], "p")
pronoun_set_map["themselves"] = LLPronoun("themselves", ["male", "female", "person"], "p")
logging.info("Lappin-Leass done")


# the Lappin Leass anaphora resolution algorithm
class LappinLeass:
    def __init__(self):
        self.n_back = 4  # go back up to n-sentences in the list for resolution

    # check the sentence @ index has head noun emphasis
    def _has_head_noun_emphasis(self, index: int, sentence: Sentence) -> bool:
        for i in range(index + 1, sentence.len()):
            token = sentence.get(i)
            if token.tag == "IN" or token.tag == "DET":
                return True
            if "VB" in token.tag:
                return False
        return False

    # is the current "nsubj" Noun preceeded by another np? (a DET or IN, no verb)
    def _has_adverbial_emphasis(self, index: int, sentence: Sentence) -> bool:
        found_det_or_in = False
        for i in range(index - 1, 0, -1):
            token = sentence.get(i)
            if token.tag == "IN" or token.tag == "DET":  # mark the start of a new np
                found_det_or_in = True
            if "NN" in token.tag and found_det_or_in:  # found another np?
                return True
            if "VB" in token.tag:
                return False
        return False

    # calculate the salience value using grammatical constructs for a noun
    # is_last_sentence:  true if this sentence is the one with the pronoun
    # seen_existential:  true if this sentence thusfar has seen an EX tag
    # token: the noun token under investigation
    # index: its index into sentence
    # sentence: the sentence of this token
    def _calculate_salience(self, seen_ex: bool, token: Token, index: int, sentence: Sentence) -> float:
        salience = 100.0  # basic score, adjusted by multiplication factor later

        # have we seen an existential marker?
        if seen_ex:
            salience += 70.0

        # subject?
        if token.dep == "nsubj":
            salience += 80

        # accusative emphasis
        if token.dep == "dobj":
            salience += 50

        # indirect object
        if token.dep == "pobj":
            salience += 40

        # Adverbial emphasis (head verb (nsubj) is preceeded by another np)
        if token.dep == "nsubj" and self._has_adverbial_emphasis(index, sentence):
            salience += 50

        # head noun emphases (head verb (nsubj is followed by another np)
        if token.dep == "nsubj" and self._has_head_noun_emphasis(index, sentence):
            salience += 80
        return salience

    # is this token semantically compatible with the pronoun?
    def _is_semtic_match(self, token: Token, pronoun: LLPronoun) -> bool:
        if pronoun.contains_semantic(token.semantic):  # otherwise - it must be one of its semantics
            return True
        if token.semantic in ["male", "female", "person"]:  # cannot match other
            return False
        if pronoun.contains_semantic("other"):
            return True
        return False

    # is this token number compatible with the pronoun
    def _matches_number(self, token: Token, pronoun: LLPronoun) -> bool:
        if pronoun.number == "p":  # plural
            return token.tag == "NNS" or token.tag == "NNPS"
        return True

    # find suitable references to resolve pronoun
    # pronoun: the pronoun that needs resolving
    # s_index: the sentence index for the sentence to process
    # t_index: the pronoun's offset into sentence_list[s_index]
    # sentence_list: a window of sentences to use for pronoun resolution if possible
    # returns a sorted list of LLReferent with the most likely referent at position [0] (highest score)
    def _find_pronouns(self, pronoun: LLPronoun, s_index: int, t_index: int, sentence_list: List[Sentence]) -> List[LLReferent]:
        # collect noun phrases that might match
        referent_array = []
        num_sentences_back = max(s_index - self.n_back, 0)
        for sentence_id in range(num_sentences_back, s_index + 1):
            salient_dropoff = math.pow(2.0, float(sentence_id - s_index))
            sentence = sentence_list[sentence_id]
            is_last = sentence_id == s_index
            seen_ex = False
            i = 0
            for token in sentence.token_list:
                if (is_last and i < t_index) or not is_last:  # restrict to anything before the part in the last sentence
                    if token.tag == "EX":
                        seen_ex = True
                    if "NN" in token.tag:  # noun
                        # is this of the right semantic for the pronoun?
                        if self._is_semtic_match(token, pronoun) and self._matches_number(token, pronoun):
                            # calculate its salience
                            salience = self._calculate_salience(seen_ex, token, i, sentence)
                            # multiply with dropoff for farther away sentences
                            salience *= salient_dropoff
                            # add new referent
                            if len(token.anaphora) > 0:  # use a previously set name resolution?
                                obj = LLReferent(token.anaphora, salience)
                            else:  # or just the text of the token
                                obj = LLReferent(token.text, salience)
                            referent_array.append(obj)
                i += 1

        referent_array.sort(key=lambda x: x.salience, reverse=True)
        return referent_array

    # resolve pronouns in a sentence list - it is assumed that the last sentence
    # sentence_list: the last sentence is assumed to have a pronoun reference
    # return the number of pronouns that did get resolved in this sentence
    def resolve_pronouns(self, sentence_list: List[Sentence]) -> int:
        num_pronouns_resolved = 0
        for s_index in range(0, len(sentence_list)):
            # find the pronoun(s) to be resolved, from left to right
            index = 0
            for t_token in sentence_list[s_index].token_list:
                if t_token.tag == "PRP" or t_token.tag == "PRP$":
                    if t_token.text.lower() in pronoun_set_map:
                        prp = pronoun_set_map[t_token.text.lower()]
                        referent_list = self._find_pronouns(prp, s_index, index, sentence_list)
                        if len(referent_list) > 0:
                            num_pronouns_resolved += 1
                            sentence_list[s_index].token_list[index].anaphora = referent_list[0].anaphora
                        else:
                            sentence_list[s_index].token_list[index].anaphora = "?"  # not found marker
                index += 1

        return num_pronouns_resolved

    # does a sentence have a pronoun in it we can try and resolve?
    def has_pronoun(self, sentence: Sentence) -> bool:
        for t_token in sentence.token_list:
            if t_token.tag == "PRP" or t_token.tag == "PRP$":
                if t_token.text.lower() in pronoun_set_map:
                    return True
        return False

