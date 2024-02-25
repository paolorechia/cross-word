import unittest
from unittest.mock import patch, mock_open
from operator import attrgetter

from copy import deepcopy
import json
from grid_generator.src.grid_generator import (
    generate,
    CrossWordGame,
    WordGraph,
    WordOrientation,
)

sample_json_word_dict = [
    {
        "word": "anel",
        "lemma": "anel",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "anelar",
        "lemma": "anelar",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "animal",
        "lemma": "animal",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "carbono",
        "lemma": "carbono",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "bobo",
        "lemma": "bobo",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "vascular",
        "lemma": "vascular",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "roberto",
        "lemma": "roberto",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "feito",
        "lemma": "fazer",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "palavras",
        "lemma": "palavra",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "dicionario",
        "lemma": "dicionario",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "muito",
        "lemma": "muito",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "legal",
        "lemma": "legal",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "policial",
        "lemma": "policial",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "teste",
        "lemma": "teste",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "poucos",
        "lemma": "pouco",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "reto",
        "lemma": "reto",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "raspado",
        "lemma": "raspado",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "sujo",
        "lemma": "sujo",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "safado",
        "lemma": "safado",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "limpo",
        "lemma": "limpo",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
    {
        "word": "amortizado",
        "lemma": "amortizado",
        "upos": "GENRE",
        "feats": [],
        "syn": [],
        "ant": [],
        "freq": 0,
        "sentences": [],
        "description": [],
    },
]


def test_generate():
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(sample_json_word_dict))
    ) as mock_file:
        game: CrossWordGame = generate()
        print(game)
        # print([w.word for w in game.placed_words])
        assert len(game.grid.placed_words) == len(game.words)
        # assert all words are in grid
        for pword in game.grid.placed_words:
            i = 0
            if pword.orientation == WordOrientation.Horizontal:
                assert pword.y_start == pword.y_end
                for x in range(pword.x_start, pword.x_end):
                    game.grid.grid[pword.y_start][x] == pword.word[i]
                    i += 1
            else:
                assert pword.x_start == pword.x_end
                for y in range(pword.y_start, pword.y_end):
                    assert game.grid.grid[y][pword.x_start] == pword.word[i]
                    i += 1


def test_build_wordgraph():
    input_list = ["anel", "animal", "ato"]
    graph = WordGraph(input_list)

    assert len(graph.nodes) == len(input_list)

    saved_list = [n.word for n in graph.nodes]
    sorted(saved_list) == sorted(input_list)
    for node in graph.nodes:
        if node.word == "anel":
            for linkable_letter in node.linkable_letters:
                if linkable_letter.char == "a":
                    print(linkable_letter)
                    strings = [str(l) for l in linkable_letter.links]
                    assert sorted(strings) == [
                        "anel_0(a)__linkedto__0(a)_animal",
                        "anel_0(a)__linkedto__0(a)_ato",
                        "anel_0(a)__linkedto__4(a)_animal",
                    ]
                if linkable_letter.char == "l":
                    strings = [str(l) for l in linkable_letter.links]
                    assert sorted(strings) == [
                        "anel_3(l)__linkedto__5(l)_animal",
                    ]
                if linkable_letter.char == "n":
                    strings = [str(l) for l in linkable_letter.links]
                    assert sorted(strings) == [
                        "anel_1(n)__linkedto__1(n)_animal",
                    ]

        if node.word == "ato":
            strings = [str(l) for l in node.linkable_letters[0].links]
            assert sorted(strings) == [
                "ato_0(a)__linkedto__0(a)_anel",
                "ato_0(a)__linkedto__0(a)_animal",
                "ato_0(a)__linkedto__4(a)_animal",
            ]

        if node.word == "animal":
            for idx, linkable_letter in enumerate(node.linkable_letters):
                if linkable_letter.char == "a":
                    if linkable_letter.index == 0:
                        strings = [str(l) for l in linkable_letter.links]
                        assert sorted(strings) == [
                            "animal_0(a)__linkedto__0(a)_anel",
                            "animal_0(a)__linkedto__0(a)_ato",
                        ]

                    if linkable_letter.index == 4:
                        strings = [str(l) for l in linkable_letter.links]
                        assert sorted(strings) == [
                            "animal_4(a)__linkedto__0(a)_anel",
                            "animal_4(a)__linkedto__0(a)_ato",
                        ]
                if linkable_letter.char == "l":
                    strings = [str(l) for l in linkable_letter.links]
                    assert sorted(strings) == ["animal_5(l)__linkedto__3(l)_anel"]
                if linkable_letter.char == "n":
                    strings = [str(l) for l in linkable_letter.links]
                    assert sorted(strings) == ["animal_1(n)__linkedto__1(n)_anel"]


def test_wordgraph_deepcopy_works():
    input_list = ["anel", "animal", "ato"]
    graph = WordGraph(input_list)
    graph2 = deepcopy(graph)
    graph2.nodes[0].visited = True
    graph2.nodes[0].linkable_letters[0].linked = True
    graph2.nodes[0].linkable_letters[0].links[0].used = True
    assert not graph.nodes[0].linkable_letters[0].linked
    assert not graph.nodes[0].linkable_letters[0].links[0].used

    graph2.nodes.append("Duh")
    assert len(graph.nodes) != len(graph2.nodes)


def test_node_deepcopy_works():
    input_list = ["anel", "animal", "ato"]
    graph = WordGraph(input_list)
    node = graph.nodes[0]
    node2 = deepcopy(node)
    node2.linkable_letters[0].linked = True
    node2.linkable_letters[0].links[0].used = True
    assert not node.linkable_letters[0].linked
    assert not node.linkable_letters[0].links[0].used


def test_mirrored_links():
    input_list = ["anel", "animal", "ato"]
    graph = WordGraph(input_list)
    for node in graph.nodes:
        if node.word == "anel":
            for letter in node.linkable_letters:
                if letter.char == "a":
                    mirrored_links = [l[1] for l in letter.find_mirrored_links()]
                    mirrored_links.sort(key=attrgetter("target_node.word"))
                    for link in mirrored_links:
                        print(link)
                    assert len(mirrored_links) == 3
                    link = mirrored_links[0]
                    assert link.char == "a"
                    assert link.index_a == 0
                    assert link.index_b == 0
                    assert link.target_node.word == "anel"
                    assert link.origin_node.word == "animal"
                    link = mirrored_links[1]
                    assert link.char == "a"
                    assert link.index_a == 4
                    assert link.index_b == 0
                    assert link.target_node.word == "anel"
                    assert link.origin_node.word == "animal"
                    link = mirrored_links[2]
                    assert link.char == "a"
                    assert link.index_a == 0
                    assert link.index_b == 0
                    assert link.target_node.word == "anel"
                    assert link.origin_node.word == "ato"


def test_find_mutually_exclusive():
    input_list = ["anel", "animal", "ato"]
    graph = WordGraph(input_list)
    for node in graph.nodes:
        if node.word == "anel":
            for letter in node.linkable_letters:
                if letter.char == "a":
                    mirrored_links = [l[1] for l in letter.find_mirrored_links()]
                    mirrored_links.sort(key=attrgetter("target_node.word"))
                    link = mirrored_links[0]
                    origin_node = link.origin_node
                    for letter in origin_node.linkable_letters:
                        if letter.char == "a" and letter.index == 0:
                            mutually_exclusive = letter.find_mutually_exclusive_links()
                            mutually_exclusive.sort(key=attrgetter("target_node.word"))
                            tlink = mutually_exclusive[0]
                            assert tlink.char == "a"
                            assert tlink.index_a == 0
                            assert tlink.index_b == 0
                            assert tlink.target_node.word == "anel"
                            assert tlink.origin_node.word == "animal"
                            tlink = mutually_exclusive[1]
                            assert tlink.char == "a"
                            assert tlink.index_a == 0
                            assert tlink.index_b == 0
                            assert tlink.target_node.word == "ato"
                            assert tlink.origin_node.word == "animal"


def test_randomize_search():
    words = [w["word"] for w in sample_json_word_dict]
    subset = words[:4]
    print(f"Testing subset of {len(subset)} words")
    graph = WordGraph(subset)
    graph.generate_all_pathes(max_pathes=10, randomized=True)
    assert len(graph.pathes) == 10


def test_generate_all_pathes():
    input_list = ["anel", "animal", "ato"]
    graph = WordGraph(input_list)
    pathes = graph.generate_all_pathes(max_pathes=12, ignore_visited=False)
    for key in pathes.keys():
        print(key)
    assert len(pathes) == 12


# def test_generate_all_pathes_bigger_dictionary():
#     input_list = [w["word"] for w in sample_json_word_dict][:4]
#     print(input_list)
#     graph = WordGraph(input_list)
#     graph.generate_all_pathes(max_pathes=12, ignore_visited=False)


if __name__ == "__main__":
    unittest.main()
