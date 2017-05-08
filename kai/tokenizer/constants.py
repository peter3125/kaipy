

# whitespace
ws = {' ', '\t', '\n'}
# full stops
fs = {'\u002e', '\u06d4', '\u0701', '\u0702', '\ufe12', '\ufe52', '\uff0e', '\uff61'}
# hyphens
hy = {'\u002d', '\u207b', '\u208b', '\ufe63', '\uff0d'}
# single quotes
sq = {'\'', '\u02bc', '\u055a', '\u07f4', '\u07f5', '\u2019', '\uff07', '\u2018', '\u201a', '\u201b', '\u275b', '\u275c'}
# double quotes
dq = {'\u0022', '\u00ab', '\u00bb', '\u07f4', '\u07f5', '\u2019', '\uff07', '\u201c', '\u201d', '\u201e', '\u201f', '\u2039', '\u203a', '\u275d', '\u276e', '\u2760','\u276f'}
# special characters
special = {'_', '%', '$', '#', '@', '^', '&', '*', '(', ')', '^', '[', '{', ']', '}', '<', '>', '/', '\\', '=', '+', '|'}
# punctuation
punc = {'!', '?', ',', ':' , ';'}
# special a,c,e,i,o, or u
spa = {'\u00c0', '\u00c1', '\u00c2', '\u00c3', '\u00c4', '\u00c5', '\u00c6','\u00e0', '\u00e1', '\u00e2', '\u00e3', '\u00e4', '\u00e5', '\u00e6','\u0100', '\u0101'}
spc = {'\u00c7', '\u00e7', '\u0106', '\u0107', '\u0108', '\u0109', '\u010a', '\u010b', '\u010c', '\u010d'}
spe = {'\u00c8', '\u00c9', '\u00ca', '\u00cb', '\u00d8', '\u00d9', '\u00da', '\u00db', '\u00e8', '\u00e9', '\u00ea', '\u00eb','\u0112', '\u0113'}
spi = {'\u00cc', '\u00cd', '\u00ce', '\u00cf', '\u00ec', '\u00ed', '\u00ee', '\u00ef','\u012a', '\u012b'}
spo = {'\u00d2', '\u00d3', '\u00d4', '\u00d5', '\u00d6', '\u00d7', '\u00d8','\u00f2', '\u00f3', '\u00f4', '\u00f5', '\u00f6', '\u00f7', '\u00f8','\u014c', '\u014d'}
spu = {'\u00d9', '\u00da', '\u00db', '\u00dc', '\u00f9', '\u00fa', '\u00fb', '\u00fc','\u016a', '\u016b'}
# contractions
prefix = {"couldn", "didn", "doesn", "don", "hadn", "hasn", "haven", "he","how", "i", "isn", "it", "might", "mightn", "must", "mustn",
          "she", "we", "weren", "what", "when", "where", "who", "would","wouldn", "you", "should", "shouldn", "won"}
postfix = {"ll", "d", "re", "s", "t", "ve", "m"}

# 0..9
def is_numeric(ch: str) -> bool:
  return '0' <= ch <= '9'

# return true if ch is a full - stop
def is_fullstop(ch: str) -> bool:
  return ch in fs

# whitespace valid characters
def is_whitespace(ch: str) -> bool:
  return ch in ws

# whitespace valid characters
def is_hyphen(ch: str) -> bool:
  return ch in hy

# single quotes
def is_singlequote(ch: str) -> bool:
  return ch in sq

# double quotes
def is_doublequote(ch:str ) -> bool:
  return ch in dq

# special characters
def is_specialcharacter(ch: str) -> bool:
  return ch in special

# punctuation
def is_punctuation(ch: str) -> bool:
  return ch in punc

# valid abc characters
def is_ABC(ch: str) -> bool:
  return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or \
         ch in spa or \
         ch in spc or \
         ch in spe or \
         ch in spi or \
         ch in spo or \
         ch in spu
