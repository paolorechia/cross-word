
from dataclasses import dataclass
from typing import List, Optional
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

    def pick_random_unique(self, max_length = 10):
        picked = self.unique_words[0]
        while picked not in self.picked_words and len(picked) > max_length:
            rand_int = random.randint(0, len(self.unique_words) - 1)
            picked = self.unique_words[rand_int]
        return picked


class WordOrientation:
    Vertical = 1
    Horizontal = 2

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

    def _row_separator(self):
        s = ""
        s += ("-" * ((self.x_size * 4) + 1))
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
    def __init__(self, 
        word_picker: WordPicker,
        grid: Grid,
        horizontal_words=10,
        vertical_words=10,
        seed_orientation=WordOrientation.Horizontal
    ):
        self.word_picker = word_picker
        self.grid = grid
        self.placed_words: List[WordInGrid] = []
        self.horizontal_words=10
        self.vertical_words=10
        self._seed_word(seed_orientation)

    def to_json(self):
        return json.dumps({})

    def _seed_word(self, seed_orientation):
        word = self.word_picker.pick_random_unique(self.grid.x_size)
        if seed_orientation == WordOrientation.Horizontal:
            self.grid.insert_horizontal_word_at_pos(word, (self.grid.x_size - len(word)) // 2, self.grid.x_size // 2)
        else:
            raise NotImplementedError("TODO")

    def __repr__(self):
        return self.grid.__repr__()


def generate() -> CrossWordGame:
    word_picker = WordPicker("../dictionary_builder/results/result.txt")
    g = Grid(x_size=30, y_size=30)
    return CrossWordGame(word_picker, g, horizontal_words=10, vertical_words=10)

if __name__ == "__main__":
    generate()