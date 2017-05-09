import uuid
import os

from typing import List
from kai.parser.model import Sentence

#
# parse tree with dependencies
#


# the parse tree structure showing relationships
class Tree:
    def __init__(self, sentence: Sentence, dep: str, offset: int):
        self.sentence = sentence
        self.dep = dep
        self.offset = offset
        self.left = None
        self.right = None

    # add a child into this tree at the right part of the tree
    def add_child(self, child):
        if child.offset < self.offset:
            if self.left is None:
                self.left = child
            else:
                self.left.add_child(child)
        elif child.offset > self.offset:
            if self.right is None:
                self.right = child
            else:
                self.right.add_child(child)

    # to string
    def __repr__(self):
        str = ""
        if self.left is not None:
            str += self.left.__repr__()
        semantic = self.sentence.get_first_semantic()
        str += " [" + self.sentence.__repr__()
        if len(semantic) > 0:
            str += "/" + semantic
        str += ":" + self.dep + "]"
        if self.right is not None:
            str += self.right.__repr__()
        return str

    # to graph viz dot description
    def to_graph_viz_dot(self) -> str:
        tree_str = "digraph G {\n"
        tree_str += to_graph_viz_dot_helper(self)
        tree_str += "}\n"
        return tree_str


# convert a sentence to a new tree item
def sentence_to_tree(sentence: Sentence) -> Tree:
    root = Tree(Sentence([]), "ROOT", -1)
    if sentence.len() > 0:
        lookup = dict()  # create a lookup for index -> tree
        for token in sentence.token_list:
            lookup[token.index] = Tree(Sentence([token]), token.dep, token.index)

        # hook the items into the tree using the lookup map for parentage using the AncestorList
        for token in sentence.token_list:
            if len(token.ancestor_list) == 0:  # root has no parents
                if root.offset == -1:  # only if not yet set
                    if not token.index in lookup:
                        raise ValueError("error: root not found in lookup")
                    root = lookup[token.index]
                else:
                    raise ValueError("error: tree has more than one root")
            elif token.index in lookup:  # must have a value
                current = lookup[token.index]
                anc = token.ancestor_list[0]  # find my ancestor that isn't "me"
                i = 0
                while i < len(token.ancestor_list) and anc == token.index:
                    anc = token.ancestor_list[i]
                    i += 1
                if anc != token.index:  # found it?
                    if anc in lookup:
                        lookup[anc].add_child(current)
                else:
                    raise ValueError("error: tree ancestors are recursive/self referencing")
            else:
                raise ValueError("error: token.index not in lookup for tree-builder: " + str(token.index))
        # check we have a root
        if root.offset == -1:
            raise ValueError("error: root not found")
    return root


# convert a forrest to a graph viz dot string
def tree_list_to_graph_viz_dot(tree_list: List[Tree]) -> str:
    tree_str = "digraph G {\n"
    for tree in tree_list:
        tree_str += to_graph_viz_dot_helper(tree)
    tree_str += "}\n"
    return tree_str


# convert a list of sentences to a list of trees
def sentence_list_to_tree_list(sentence_list: List[Sentence]) -> List[Tree]:
    tree_list = []
    for sentence in sentence_list:
        tree = sentence_to_tree(sentence)
        if tree.sentence.len() > 0:
            tree_list.append(tree)
    return tree_list


# convert a tree to graph items, helper
def to_graph_viz_dot_helper(tree: Tree) -> str:
    indent = " " * 4
    tree_str = ""
    node = ""
    if tree.sentence.len() == 1 and "VB" in tree.sentence.token_list[0].tag:
        label = tree.sentence.__str__() + ", " + tree.sentence.token_list[0].tag
        node = "node" + str(tree.sentence.token_list[0].index)
        tree_str += indent + node + " [shape=box,label=\"" + label + "\"];\n"
    else:
        if tree.sentence.len() > 0:
            tt = tree.sentence.token_list[0]
            label = tree.sentence.__str__()
            extra = ""
            if len(tt.tag) > 0 and ('a' <= tt.tag.lower()[0] <= 'z'):
                extra += ", " + tt.tag
            if len(tt.anaphora) > 0 and tt.anaphora != tt.text:
                extra += ", ref:" + tt.anaphora
            if len(tt.semantic) > 0:
                extra += ", semantic:" + tt.semantic
            label += extra
            label = label.replace('"', '\\"')  # escape double quotes

            node = "node" + str(tt.index)
            tree_str += indent + node + " [label=\"" + label + "\"];\n"

    if tree.left is not None:
        node_left = "node" + str(tree.left.sentence.token_list[0].index)
        tree_str += indent + node + " -> " + node_left + ";\n"
        tree_str += to_graph_viz_dot_helper(tree.left)
    if tree.right is not None:
        node_right = "node" + str(tree.right.sentence.token_list[0].index)
        tree_str += indent + node + " -> " + node_right + ";\n"
        tree_str += to_graph_viz_dot_helper(tree.right)

    return tree_str


# convert a dot file to a PNG image
# this requires DOT to be installed like so: sudo apt install graphviz
def dot_to_png(dot: str):
    if len(dot) > 0:
        uuid_str = uuid.uuid4().__str__()
        dot_temp = "/tmp/bt_dot_" + uuid_str + ".dot"
        png_temp = "/tmp/bt_png_" + uuid_str + ".png"

        try:
            with open(dot_temp, 'w') as writer:
                writer.write(dot)

            cmd_str = "dot -Tpng " + dot_temp + " -o " + png_temp
            os.system(cmd_str)
            if os.path.isfile(png_temp):
                with open(png_temp, mode='rb') as file:
                    return file.read()
            else:
                return None

        finally:
            if os.path.isfile(dot_temp):
                os.remove(dot_temp)
            if os.path.isfile(png_temp):
                os.remove(png_temp)
