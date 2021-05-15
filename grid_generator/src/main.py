from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from itertools import product
from operator import attrgetter
from copy import deepcopy
import re
import json
import random


@dataclass
class WordEntry:
    word: str
    lemma: str
    upos: str
    feats: List[str]

    def get_hints_from_word(self):
        return ["TODO HINTS"]


class WordDictionary:
    def __init__(self, words_list):
        self.words: List[WordEntry] = []
        self.hashmap = {}
        for word_dict in words_list:
            word = WordEntry(**word_dict)
            self.words.append(word)
            self.hashmap[word.word] = word

    def to_unique_list(self):
        s = set()
        for word in self.words:
            s.add(word.word)
        return list(s)


class WordPicker:
    def __init__(self, filename):
        with open(filename, "r") as fp:
            self.word_dictionary: WordDictionary = WordDictionary(json.load(fp))
        self.unique_words = self.word_dictionary.to_unique_list()
        self.picked_words = set()

    def pick_n_random_words(self, num_words, max_length=10):
        while len(self.picked_words) < num_words:
            self.pick_random_unique(max_length=max_length)
        return self.picked_words

    def pick_random_unique(self, max_length=10):
        picked = self.unique_words[0]
        while picked in self.picked_words or len(picked) > max_length:
            rand_int = random.randint(0, len(self.unique_words) - 1)
            picked = self.unique_words[rand_int]
        self.picked_words.add(picked)
        return picked

    def pick_word_with_character(self, char, max_length=10):
        picked = self.pick_random_unique(max_length)
        while char not in picked:
            picked = self.pick_random_unique(max_length)
        return picked


class WordOrientation:
    Vertical = "vertical"
    Horizontal = "horizontal"


@dataclass
class WordInGrid:
    x_start: int
    x_end: int
    y_start: int
    y_end: int
    hints: List[str]
    word: Optional[str] = None
    orientation: WordOrientation = WordOrientation.Horizontal


class Grid:
    def __init__(self, x_size=20, y_size=20):
        self.x_size = x_size
        self.y_size = y_size
        self.grid = []
        for y in range(y_size):
            self.grid.append([])
            for _ in range(x_size):
                self.grid[y].append(" ")

    def insert_horizontal_word_at_pos(self, word, x, y):
        row = self.grid[y]
        for idx, w in enumerate(word):
            row[x + idx] = w

    def insert_vertical_word_at_pos(self, word, x, y):
        for idx, w in enumerate(word):
            self.grid[y + idx][x] = w

    def _row_separator(self):
        s = ""
        s += "-" * ((self.x_size * 4) + 1)
        s += "\n"
        return s

    def __repr__(self):
        s = self._row_separator()
        for row in self.grid:
            for cell in row:
                s += f"| {cell} "
            s += "|\n"
            s += self._row_separator()
        return s


class CrossWordGame:
    def __init__(
        self,
        word_picker: WordPicker,
        grid: Grid,
        horizontal_words=10,
        vertical_words=10,
        seed_orientation=WordOrientation.Horizontal,
    ):
        self.word_picker = word_picker
        self.grid = grid
        self.placed_words: List[WordInGrid] = []
        self.num_horizontal_words = horizontal_words
        self.num_vertical_words = vertical_words
        self.words = self.word_picker.pick_n_random_words(
            horizontal_words + vertical_words, max_length=10
        )
        self.word_graph = WordGraph(self.words)
        # print(self.word_graph)

    def to_json(self):
        return json.dumps({})

    def word_path_to_grid(self):
        """Insert a word path into a grid."""

    def find_minimum_grid_size(self):
        """Translade the grid into origin and find minimum rectangular dimensions."""

    # def _seed_word(self, seed_orientation):
    #     if seed_orientation == WordOrientation.Horizontal:
    #         raw_word = self.word_picker.pick_random_unique(self.grid.x_size)
    #         word_in_grid = WordInGrid(
    #             x_start=(self.grid.x_size - len(raw_word)) // 2,
    #             x_end=((self.grid.x_size - len(raw_word)) // 2) + len(raw_word),
    #             y_start=(self.grid.x_size // 2),
    #             y_end=(self.grid.x_size // 2),
    #             hints=[],
    #             word=raw_word,
    #             orientation=WordOrientation.Horizontal
    #         )
    #         self.grid.insert_horizontal_word_at_pos(word=raw_word, x=word_in_grid.x_start, y=word_in_grid.y_start)
    #         self.placed_words.append(word_in_grid)
    #     else:
    #         raise NotImplementedError("TODO!")

    # def _expand_seed_with_backtracking(self):
    #     seeded_word = self.placed_words[0]
    #     y = seeded_word.y_start
    #     i = 0
    #     x = seeded_word.x_start
    #     new_word = self.word_picker.pick_word_with_character(seeded_word.word[i])
    #     match_j = -1
    #     for j, c in enumerate(new_word):
    #         if c == seeded_word.word[i]:
    #             match_j = j
    #             break
    #     self.grid.insert_vertical_word_at_pos(new_word, x, y - match_j)
    #     print("match_j", match_j)
    #     word_in_grid = WordInGrid(
    #         x_start=x,
    #         x_end=x,
    #         y_start=y-match_j,
    #         y_end=(y - match_j) + len(new_word),
    #         word=new_word,
    #         hints=[],
    #         orientation=WordOrientation.Vertical
    #     )
    #     self.placed_words.append(word_in_grid)

    def __repr__(self):
        return self.grid.__repr__()


class WordNode:
    def __init__(self, word):
        self.word: str = word
        self.visited: bool = False
        self.linkable_letters: List[LinkableLetter] = []
        for idx, char in enumerate(self.word):
            self.linkable_letters.append(LinkableLetter(char, idx, self))

    def insert_link(self, link):
        assert "NodeLink" in str(type(link))
        for linkable_letter in self.linkable_letters:
            if link.char == linkable_letter.char:  # Matching letter
                if linkable_letter.index == link.index_a:  # Matching index
                    for existing_link in linkable_letter.links:
                        if existing_link == link:
                            return
                    link.set_parent_letter(linkable_letter)
                    linkable_letter.links.append(link)

    def __eq__(self, node):
        return self.word == node.word

    def __repr__(self):
        s = f"Node ({self.word})\n"
        # for link in self.links:
        #     s += f"-------> {str(link)}\n"
        return s


@dataclass
class NodeLink:
    char: str
    index_a: int
    index_b: int
    origin_node: WordNode
    target_node: WordNode
    used: bool = False
    parent_letter: Optional[any] = None

    def set_parent_letter(self, parent_letter: any):
        self.parent_letter = parent_letter

    def __eq__(self, link):
        return (
            self.char == link.char
            and self.index_a == link.index_a
            and self.index_b == link.index_b
            and self.target_node == link.target_node
        )

    def __str__(self):
        return f"{self.origin_node.word}_{self.index_a}({self.char})__linkedto__{self.index_b}({self.char})_{self.target_node.word}"


class LinkableLetter:
    def __init__(self, char, index, parent_node):
        self.char: str = char
        self.index: int = index
        self.parent_node: WordNode = parent_node
        self.links: List[NodeLink] = []
        self.linked: bool = False

    def __repr__(self):
        return f"LinkableLetter(char={self.char}, index={self.index}, linked={self.linked}"

    def _find_mirrored_links(self):
        target_nodes = []
        mirrored_links = []
        for link in self.links:
            target_nodes.append(link.target_node)
        added_links = set()
        for node in target_nodes:
            for letter in node.linkable_letters:
                if letter.char == self.char:
                    for link in letter.links:
                        if (
                            link.index_b == self.index
                            and link.target_node == self.parent_node
                        ):
                            if str(link) not in added_links:
                                mirrored_links.append((deepcopy(letter), deepcopy(link)))
                                added_links.add(str(link))

        return mirrored_links


    def find_mutually_exclusive_links(self):
        """Finds mutually_exclusive for a given linkable letter."""
        mutually_exclusive = []
        for link in self.links:
            if link.index_a == self.index:
                mutually_exclusive.append(link)
        return mutually_exclusive


    def find_mirrored_links(self) -> List[Tuple[any, NodeLink]]:
        """Find links that are mirrored.

        This returns which links must be set to 'used' to enforce
        that the same letter is not used in multiple links.
        """
        mirrored_links = self._find_mirrored_links()
        return mirrored_links


class WordGraph:
    def __init__(self, word_list):
        self.nodes = [WordNode(word) for word in word_list]

        node_combinations = product(self.nodes, self.nodes)

        for a_node, b_node in node_combinations:
            if a_node == b_node:
                continue

            for a_idx, char in enumerate(a_node.word):
                matches = [m for m in re.finditer(char, b_node.word)]
                for m in matches:
                    a_node.insert_link(
                        NodeLink(
                            char=char,
                            index_a=a_idx,
                            index_b=m.start(),
                            origin_node=a_node,
                            target_node=b_node,
                        )
                    )
                    b_node.insert_link(
                        NodeLink(
                            char=char,
                            index_a=m.start(),
                            index_b=a_idx,
                            origin_node=b_node,
                            target_node=a_node,
                        )
                    )

    def __repr__(self):
        s = ""
        for node in self.nodes:
            s += str(node)
        return s


def generate_all_pathes(input_graph: WordGraph) -> List[List[WordNode]]:
    """
    Should generate all possible pathes.

    Maybe implement as a WordPath
    """

    g = deepcopy(input_graph)
    pathes_matrix = []
    for node_idx, _ in enumerate(input_graph.nodes):
        pathes_for_one_root_node = pathfinder(deepcopy(input_graph), node_idx)
        pathes_matrix.append(pathes_for_one_root_node)
    # TODO: flatten pathes_matrix


def search(
    input_graph,
    input_node_idx: int,
    traversed_path: List[NodeLink],
    path_dict,
    linked_pairs,
):
    graph = deepcopy(input_graph)
    input_node = graph.nodes[input_node_idx]
    # print(linked_pairs)
    # print("On node:", input_node)
    current_path = deepcopy(traversed_path)
    for linkable_letter in input_node.linkable_letters:
        if not linkable_letter.linked:
            # print("FREE", linkable_letter, linkable_letter.links)
            for link in linkable_letter.links:
                pair_to_link = [input_node.word, link.target_node.word]
                pair_to_link.sort()
                hsh = f"{pair_to_link[0]}_{pair_to_link[1]}"
                if not link.used and hsh not in linked_pairs:
                    current_path = deepcopy(traversed_path)
                    current_path.append(link)
                    current_linked_pairs = deepcopy(linked_pairs)
                    current_linked_pairs.add(hsh)
                    input_node.visited = True
                    linkable_letter.linked = True
                    link.used = True
                    link.parent_letter.linked = True
                    mirrored_links = linkable_letter.find_mirrored_links()
                    for letter, link_ in mirrored_links:
                        letter = True
                        link_.used = True
                        # print("Flagging as mirrored", link_)
                    for letter in link.target_node.linkable_letters:
                        if letter.char == link.char and letter.index == link.index_b:
                            links_ = letter.find_mutually_exclusive_links()
                            for link_ in links_:
                                # print("Flagging as mutually exclusive", link_)
                                link_.used = True
                    new_node_idx = -1
                    for idx, node in enumerate(graph.nodes):
                        if node.word == link.target_node.word:
                            new_node_idx = idx
                    # print(new_node_idx)
                    search(
                        graph,
                        new_node_idx,
                        current_path,
                        path_dict,
                        current_linked_pairs,
                    )
                    # Reset state for backtracking
                    input_node.visited = False
                    linkable_letter.linked = False
                    link.used = False
                    link.parent_letter.linked = False
                    for letter, link_ in mirrored_links:
                        letter = False
                        link_.used = False
                        # print("Flagging as mirrored", link_)
                    for letter in link.target_node.linkable_letters:
                        if letter.char == link.char and letter.index == link.index_b:
                            links_ = letter.find_mutually_exclusive_links()
                            for link_ in links_:
                                # print("Flagging as mutually exclusive", link_)
                                link_.used = False
    # print("Out of choices, ended")
    path_to_key = path_to_string(current_path)
    path_dict[path_to_key] = current_path

def path_to_string(path: List[NodeLink]):
    return "--".join([str(p) for p in path])

def pathfinder(graph: WordGraph, root_node_idx: int):
    used_links = []
    pathes_that_were_found = []
    while not all_nodes_are_visited:
        for node in graph.nodes:
            partial_path_dict = []
            search(node, [], partial_path_dict)

    if len(used_links) == len(nodes) - 1:
        return pathes_that_were_found
    return []  # no pathes were found


def generate() -> CrossWordGame:
    word_picker = WordPicker("../dictionary_builder/results/result.txt")
    g = Grid(x_size=30, y_size=30)
    return CrossWordGame(word_picker, g, horizontal_words=10, vertical_words=10)


if __name__ == "__main__":
    generate()
