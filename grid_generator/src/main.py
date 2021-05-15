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
            self.linkable_letters.append(LinkableLetter(char, idx))

    def insert_link(self, link):
        assert "NodeLink" in str(type(link))
        for linkable_letter in self.linkable_letters:
            if link.char == linkable_letter.char:  # Matching letter
                if linkable_letter.index == link.index_a:  # Matching index
                    for existing_link in linkable_letter.links:
                        if existing_link == link:
                            return
                    linkable_letter.links.append(link)

    def __eq__(self, node):
        return self.word == node.word

    def __repr__(self):
        s = f"Node ({self.word})\nLinks:\n"
        # for link in self.links:
        #     s += f"-------> {str(link)}\n"
        return s


@dataclass
class NodeLink:
    char: chr
    index_a: int
    index_b: int
    origin_node: WordNode
    linked_node: WordNode
    used: bool = False

    def __eq__(self, link):
        return (
            self.char == link.char
            and self.index_a == link.index_a
            and self.index_b == link.index_b
            and self.linked_node == link.linked_node
        )

    def __str__(self):
        return f"{self.char}_{self.index_a}_{self.index_b}_linkedto_{self.linked_node.word}"


@dataclass
class LinkableLetter:
    char: chr
    index: int
    links: List[NodeLink] = field(default_factory=list)
    linked: bool = False


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
                            linked_node=b_node,
                        )
                    )
                    b_node.insert_link(
                        NodeLink(
                            char=char,
                            index_a=m.start(),
                            index_b=a_idx,
                            origin_node=b_node,
                            linked_node=a_node,
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
    input_node: WordNode,
    traversed_path: List[Tuple[WordNode, NodeLink]],
    path_matrix,
    linked_pairs,
):
    print(input_node)
    if input_node.visited:
        path_matrix.append(traversed_path)
        return
    for l_idx, linkable_letter in enumerate(input_node.linkable_letters):
        if not linkable_letter.linked:
            for idx, link in enumerate(linkable_letter.links):
                pair_to_link = [input_node.word, link.linked_node.word]
                pair_to_link.sort()
                hsh = f"{pair_to_link[0]}_{pair_to_link[1]}"
                if not link.used and hsh not in linked_pairs:
                    linked_pairs.add(hsh)
                    origin_node = deepcopy(input_node)
                    current_letter = origin_node.linkable_letters[l_idx]
                    current_letter.linked = True
                    current_letter.links[idx].used = True
                    origin_node.visited = True
                    current_path = deepcopy(traversed_path)
                    current_path.append((origin_node, current_letter.links[idx]))
                    next_node = current_letter.links[idx].linked_node
                    search(next_node, current_path, path_matrix, linked_pairs)


def pathfinder(graph: WordGraph, root_node_idx: int):
    used_links = []
    pathes_that_were_found = []
    while not all_nodes_are_visited:
        for node in graph.nodes:
            partial_path_matrix = []
            search(node, [], partial_path_matrix)

    if len(used_links) == len(nodes) - 1:
        return pathes_that_were_found
    return []  # no pathes were found


def generate() -> CrossWordGame:
    word_picker = WordPicker("../dictionary_builder/results/result.txt")
    g = Grid(x_size=30, y_size=30)
    return CrossWordGame(word_picker, g, horizontal_words=10, vertical_words=10)


if __name__ == "__main__":
    generate()
