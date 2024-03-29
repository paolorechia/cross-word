from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from itertools import product
from operator import attrgetter
from copy import deepcopy
import re
import json
import random

from datetime import datetime
from unidecode import unidecode
import multiprocessing as mp


@dataclass
class WordEntry:
    word: str
    lemma: str
    upos: str
    feats: List[str]
    hint: str

class WordDictionary:
    def __init__(self, words_list):
        self.words: List[WordEntry] = []
        for word_dict in words_list:
            if "status_code" in word_dict:
                del word_dict["status_code"]
            word = WordEntry(**word_dict)
            word.word = unidecode(word.word)
            self.words.append(word)
        # self.words.sort(key=attrgetter("freq"), reverse=True)
        self.hashmap = {}
        for word in self.words:
            self.hashmap[word.word] = word

    def to_unique_list(self):
        s = set()
        for word in self.words:
            s.add(word.word)
        return list(s)
    
    def __getitem__(self, key):
        return self.hashmap[key]


class WordPicker:
    def __init__(self, filename, most_frequents=20000, stop_word_offset=200):
        with open(filename, "r") as fp:
            self.word_dictionary: WordDictionary = WordDictionary(json.load(fp))
        self.unique_words = self.word_dictionary.to_unique_list()
        self.unique_words = self.unique_words[stop_word_offset:most_frequents]
        self.picked_words = set()

    def pick_n_random_words(self, num_words, max_length=10, min_length=4):
        """Reset picked words and pick n words."""
        self.picked_words = set()
        while len(self.picked_words) < num_words:
            self.pick_random_unique(max_length=max_length, min_length=min_length)
        return self.picked_words

    def pick_random_unique(self, max_length=10, min_length=4):
        picked = self.unique_words[0]
        while (
            picked in self.picked_words
            or len(picked) > max_length
            or len(picked) < min_length
        ):
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
    word: str
    order_number: int = None
    orientation: WordOrientation = WordOrientation.Horizontal



class GridConflictingCell(Exception):
    """Exception for flagging inappropriate cell reuse."""


class Grid:
    def __init__(self, x_size=20, y_size=20):
        self.x_size = x_size
        self.y_size = y_size
        self.grid = []
        self.placed_words: List[WordInGrid] = []
        for y in range(y_size):
            self.grid.append([])
            for _ in range(x_size):
                self.grid[y].append(" ")

        self.used_pos = set()

    def insert_word(self, word_in_grid):
        # print("Inserting ", word_in_grid)
        if word_in_grid.orientation == WordOrientation.Horizontal:
            self.insert_horizontal_word(word_in_grid)
        else:
            self.insert_vertical_word(word_in_grid)

    def insert_horizontal_word(self, word_in_grid):
        row = self.grid[word_in_grid.y_start]
        for idx, w in enumerate(word_in_grid.word):
            x = word_in_grid.x_start + idx
            coord = f"({x},{row})"
            if coord in self.used_pos:
                raise GridConflictingCell(f"Cell already used: {coord}")
            self.used_pos.add(coord)
            row[x] = w
        self.placed_words.append(word_in_grid)

    def insert_vertical_word(self, word_in_grid):
        x = word_in_grid.x_start
        for idx, w in enumerate(word_in_grid.word):
            y = word_in_grid.y_start + idx
            coord = f"({x},{y})"
            if coord in self.used_pos:
                raise GridConflictingCell(f"Cell already used: {coord}")
            self.used_pos.add(coord)
            self.grid[y][x] = w
        self.placed_words.append(word_in_grid)

    def resize_to_minimum_size(self):
        min_x = min([min(pword.x_start, pword.x_end) for pword in self.placed_words])
        max_x = max([max(pword.x_start, pword.x_end) for pword in self.placed_words])
        min_y = min([min(pword.y_start, pword.y_end) for pword in self.placed_words])
        max_y = max([max(pword.y_start, pword.y_end) for pword in self.placed_words])
        x_offset = min_x
        y_offset = min_y
        self.x_size = max_x - min_x
        self.y_size = max_y - min_y
        self.grid = []
        # print(self.x_size, self.y_size, x_offset, y_offset)
        for y in range(self.y_size):
            self.grid.append([])
            for _ in range(self.x_size):
                self.grid[y].append(" ")
        new_pwords = self.placed_words[:]
        self.placed_words = []
        for pword in new_pwords:
            pword.x_start -= x_offset
            pword.x_end -= x_offset
            pword.y_start -= y_offset
            pword.y_end -= y_offset
            # print(pword)
            self.insert_word(pword)
        """Resizes to minimum rectangular dimensions."""

    @property
    def area(self):
        return self.x_size * self.y_size

    def is_valid(self):
        for pword in self.placed_words:
            i = 0
            if pword.orientation == WordOrientation.Horizontal:
                # Check that the boundaries are not immediately followed by letters
                if self.grid[pword.y_start][pword.x_start - 1] != " ":
                    return False
                if self.grid[pword.y_start][pword.x_end + 1] != " ":
                    return False
                for x in range(pword.x_start, pword.x_end):
                    if not self.grid[pword.y_start][x] == pword.word[i]:
                        return False
                    i += 1
            else:
                # Check that the boundaries are not immediately followed by letters
                if self.grid[pword.x_start][pword.y_start - 1] != " ":
                    return False
                if self.grid[pword.x_start][pword.y_end + 1] != " ":
                    return False
                for y in range(pword.y_start, pword.y_end):
                    if not self.grid[y][pword.x_start] == pword.word[i]:
                        return False
                    i += 1
        return True

    def get_mask(self):
        mask = []
        for y in range(self.y_size):
            mask.append([])
            for _ in range(self.x_size):
                mask[y].append("*")
        for idx, pword in enumerate(self.placed_words):
            pword.order_number = idx
            if pword.orientation == WordOrientation.Horizontal:
                y = pword.y_start
                for x in range(pword.x_start, pword.x_end):
                    mask[y][x] = str(idx)
            else:
                x = pword.x_start
                for y in range(pword.y_start, pword.y_end):
                    mask[y][x] = str(idx)
        g = Grid(x_size=self.x_size, y_size=self.y_size)
        g.grid = mask
        return g

    def _row_separator(self):
        s = ""
        s += "-" * ((self.x_size * 4) + 1)
        s += "\n"
        return s

    def __repr__(self):
        print(self.x_size, self.y_size)
        s = self._row_separator()
        for row in self.grid:
            for cell in row:
                s += f"| {cell} "
            s += "|\n"
            s += self._row_separator()
        return s


class InvalidWordSetError(Exception):
    """WordSet did not yield a valid grid."""


class CrossWordGame:
    def __init__(
        self,
        word_picker: WordPicker,
        num_words=10,
        max_pathes=100,
        threads=8,
        seed_orientation=WordOrientation.Horizontal,
    ):
        self.grid: Optional[Grid] = None
        self.word_picker = word_picker
        self.num_words = num_words
        self.max_pathes = max_pathes
        self.threads = threads
        self.parallelized_generate_game(threads=self.threads)

    def to_json(self):
        raise NotImplementedError()
        return json.dumps({})

    def get_mask(self):
        return self.grid.get_mask()
    

    def get_hints(self):
        hints = []
        for pword in self.grid.placed_words:
            available_hints = self.word_picker.word_dictionary[pword.word].hint
            chosen_hint = random.choice(available_hints)
            hints.append((pword.order_number, chosen_hint))
        return hints

    def generate_game(self, threads=1):
        self.grid = self._generate_game(self.max_pathes, threads=self.threads)

    def parallelized_generate_game(self, threads=8):
        print("Picking random words...")
        self.words = self.word_picker.pick_n_random_words(
            self.num_words, max_length=8, min_length=4
        )
        print(f"Running with {threads}")
        queues = []
        processes = []

        threads_queue = mp.Queue()
        for i in range(threads):
            queue = mp.Queue()
            queues.append(queue)
            args = (self.max_pathes // threads, queue, 1, threads_queue)
            p = mp.Process(target=self._generate_game, args=args)
            processes.append(p)
            print(f"Starting worker {i}")
            p.start()

        print("Collecting results...")
        results = []
        for i in range(threads):
            result = queues[i].get()
            results.append(result)

        best_result = min(
            [valid for valid in results if valid], key=(attrgetter("area"))
        )
        for i in range(threads):
            processes[i].join()
            print(f"Finished worker {i}")
        self.grid = best_result

    def _generate_game(self, max_pathes, mp_queue=None, threads=1, threads_queue=None):
        max_iterations = 100
        i = 0
        print("Generating game...")
        grid = None
        current_threads = threads
        while i < max_iterations and not grid:
            try:
                i += 1
                if threads_queue:
                    try:

                        is_thread_available = threads_queue.get_nowait()
                        if is_thread_available:
                            print("Break early!!")
                            threads_queue.put_nowait(is_thread_available)
                            mp_queue.put(None)
                            return None
                            current_threads += 1
                    except Exception:
                        pass
                print(f"Iteration: {i}, using threads {current_threads}")
                self.words = self.word_picker.pick_n_random_words(
                    self.num_words, max_length=8, min_length=4
                )
                print("Building word graph...")

                self.word_graph = WordGraph(self.words)
                print("Finding pathes...")
                self.word_graph.parallelized_generate_all_pathes(
                    max_pathes=max_pathes,
                    max_iterations=100000,
                    threads=current_threads,
                )
                print("Generating grid...")
                grid = self._generate_grid()
            except InvalidWordSetError:
                print("Invalid grid :(")
                pass
        if grid:
            print("Generated Successfully!")
            if threads_queue:
                threads_queue.put_nowait(True)
            if mp_queue:
                mp_queue.put(grid)
            return grid
        print(f"Failed to generate game after {max_iterations} tries.")

    def _generate_grid(self):
        current_grid = None
        print("Generating grid...")
        for idx, path in enumerate(self.word_graph.pathes):
            try:
                g = self._node_links_to_grid(path)
                # print(g.placed_words, self.words)
                if len(g.placed_words) == len(self.words) and g.is_valid():
                    print("Valid path!")
                    # print("Pre-resize:", g.x_size, g.y_size)
                    g.resize_to_minimum_size()
                    # print("Resized:", g.x_size, g.y_size)
                    if not current_grid and g:
                        current_grid = g
                    else:
                        if g.area < current_grid.area:
                            current_grid = g
            except GridConflictingCell as e:
                pass
        if current_grid:
            self.grid = current_grid
            return current_grid
        raise InvalidWordSetError("Invalid word set/pathes, could not create a grid.")

    def _node_links_to_grid(self, links: List[any]):
        grid = Grid(1000, 1000)
        # Take first link and use it to seed the Grid
        node_link: NodeLink = links[0]
        raw_word = node_link.origin_node.word
        word_in_grid = WordInGrid(
            x_start=(grid.x_size - len(raw_word)) // 2,
            x_end=((grid.x_size - len(raw_word)) // 2) + len(raw_word),
            y_start=(grid.x_size // 2),
            y_end=(grid.x_size // 2),
            word=raw_word,
            orientation=WordOrientation.Horizontal,
        )
        grid.insert_word(word_in_grid)
        words_in_grid = {node_link.origin_node.word: word_in_grid}
        used_links = set()
        # Insert remainining links.
        j = 0
        while len(used_links) < len(links) and j < len(links):
            # Find a link that was not yet consumed
            # And that is connected to a word that is already in the grid.
            j += 1
            for idx, link in enumerate(links):
                if idx not in used_links:
                    if (
                        link.origin_node.word in words_in_grid
                        and link.target_node.word not in words_in_grid
                    ):
                        # Add link words to grid
                        used_links.add(idx)
                        previous_word = words_in_grid[link.origin_node.word]
                        new_orientation = (
                            WordOrientation.Horizontal
                            if previous_word.orientation == WordOrientation.Vertical
                            else WordOrientation.Vertical
                        )
                        new_word = link.target_node.word
                        if new_orientation == WordOrientation.Vertical:
                            new_x_start = previous_word.x_start + link.index_a
                            new_x_end = new_x_start
                            new_y_start = previous_word.y_start - link.index_b
                            new_y_end = new_y_start + len(new_word)
                        else:
                            new_x_start = previous_word.x_start - link.index_b
                            new_x_end = new_x_start + len(new_word)
                            new_y_start = previous_word.y_start + link.index_a
                            new_y_end = new_y_start

                        new_word_in_grid = WordInGrid(
                            x_start=new_x_start,
                            x_end=new_x_end,
                            y_start=new_y_start,
                            y_end=new_y_end,
                            word=new_word,
                            orientation=new_orientation,
                        )
                        grid.insert_word(new_word_in_grid)
                        words_in_grid[link.target_node.word] = new_word_in_grid
                    elif (
                        link.target_node.word in words_in_grid
                        and link.origin_node.word not in words_in_grid
                    ):
                        used_links.add(idx)
                        previous_word = words_in_grid[link.target_node.word]
                        new_orientation = (
                            WordOrientation.Horizontal
                            if previous_word.orientation == WordOrientation.Vertical
                            else WordOrientation.Vertical
                        )
                        new_word = link.origin_node.word
                        if new_orientation == WordOrientation.Vertical:
                            new_x_start = previous_word.x_start + link.index_b
                            new_x_end = new_x_start
                            new_y_start = previous_word.y_start - link.index_a
                            new_y_end = new_y_start + len(new_word)
                        else:
                            new_x_start = previous_word.x_start - link.index_a
                            new_x_end = new_x_start + len(new_word)
                            new_y_start = previous_word.y_start + link.index_b
                            new_y_end = new_y_start

                        new_word_in_grid = WordInGrid(
                            x_start=new_x_start,
                            x_end=new_x_end,
                            y_start=new_y_start,
                            y_end=new_y_end,
                            word=new_word,
                            orientation=new_orientation,
                        )
                        grid.insert_word(new_word_in_grid)
                        words_in_grid[link.origin_node.word] = new_word_in_grid
        return grid

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
        return (
            f"LinkableLetter(char={self.char}, index={self.index}, linked={self.linked}"
        )

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
                                mirrored_links.append(
                                    (deepcopy(letter), deepcopy(link))
                                )
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

    def parallelized_generate_all_pathes(
        self, max_pathes=100, max_iterations=100, ignore_visited=False, threads=8
    ) -> List[List[NodeLink]]:
        """
        Should generate all possible pathes.

        Maybe implement as a WordPath
        """

        input_graph = deepcopy(self)
        complete_pathes = {}
        incomplete_pathes = {}
        t0 = datetime.now()
        pathes_for_one_root_node: Dict[str, List[NodeLink]] = {}
        print("Starting search!")
        queues = []
        processes = []
        for i in range(threads):
            queue = mp.Queue()
            args = (
                deepcopy(input_graph),
                len(input_graph.nodes) - 1,
                queue,
                max_pathes // threads,
                max_iterations,
            )
            queues.append(queue)
            p = mp.Process(target=parallelized_randomized_search, args=args)
            processes.append(p)
            print(f"Starting worker {i}")
            p.start()

        print("Collecting results...")
        super_result = {}
        for i in range(threads):
            result = queues[i].get()
            super_result.update(result)

        for i in range(threads):
            processes[i].join()
            print(f"Finished worker {i}")

        for key, path in super_result.items():
            if len(path) == len(input_graph.nodes) - 1:
                complete_pathes[key] = path
            else:
                incomplete_pathes[key] = path
        t1 = datetime.now()
        elapsed_time = t1 - t0
        print(f"Elapsed time: {elapsed_time}")
        print("Total complete pathes:", len(complete_pathes))
        self.pathes = []
        for _, item in complete_pathes.items():
            self.pathes.append(item)
        return complete_pathes


def parallelized_randomized_search(
    input_graph,
    target_len,
    mp_queue,
    max_pathes=10,
    max_iterations=1000,
):
    # print("Worker started!")
    result = iterative_randomized_search(
        input_graph,
        target_len,
        max_pathes,
        max_iterations,
    )
    mp_queue.put(result)
    # print("Worker ended!")


def iterative_randomized_search(
    input_graph,
    target_len,
    max_pathes=10,
    max_iterations=1000,
):
    path_dict = {}
    current_iteration = 0
    while len(path_dict) < max_pathes and current_iteration < max_iterations:
        print(
            f"Number of pathes: {len(path_dict)}. Iteration: {current_iteration}",
            end="\r",
        )
        nodes = deepcopy(input_graph.nodes)
        current_path: List[NodeLink] = []
        linked_pairs = set()
        current_iteration += 1
        while len(current_path) < target_len and nodes:
            idx = random.randrange(0, len(nodes))
            input_node = nodes.pop(idx)
            if not input_node.visited and input_node.linkable_letters:
                l_idx = random.randrange(0, len(input_node.linkable_letters))
                linkable_letter = input_node.linkable_letters.pop(l_idx)
                if linkable_letter.links and not linkable_letter.linked:
                    llidx = random.randrange(0, len(linkable_letter.links))
                    link = linkable_letter.links.pop(llidx)
                    pair_to_link = [input_node.word, link.target_node.word]
                    pair_to_link.sort()
                    hsh = f"{pair_to_link[0]}_{pair_to_link[1]}"
                    if not link.used and hsh not in linked_pairs:
                        current_path.append(link)
                        linked_pairs.add(hsh)
                        input_node.visited = True
                        linkable_letter.linked = True
                        link.used = True
                        link.parent_letter.linked = True
                        if len(current_path) == target_len:
                            path_to_key = path_to_string(current_path)
                            path_dict[path_to_key] = current_path
    return path_dict


def path_to_string(path: List[NodeLink]):
    return "--".join([str(p) for p in path])


def generate(num_words=3, max_pathes=10) -> CrossWordGame:
    word_picker = WordPicker(
        "../dictionary_builder/results/result.txt", stop_word_offset=0
    )
    game = CrossWordGame(word_picker, num_words=num_words, max_pathes=max_pathes)
    print(game)
    return game


if __name__ == "__main__":
    generate()
