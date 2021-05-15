import unittest
from copy import deepcopy

from grid_generator.src.main import (
    generate,
    CrossWordGame,
    WordGraph,
    WordOrientation,
    search,
)


def test_generate():
    game: CrossWordGame = generate()
    # print(game)
    # print([w.word for w in game.placed_words])
    assert len(game.placed_words) == game.num_vertical_words + game.num_horizontal_words
    # assert all words are in grid
    for pword in game.placed_words:
        i = 0
        if pword.orientation == WordOrientation.Horizontal:
            assert pword.y_start == pword.y_end
            for x in range(pword.x_start, pword.x_end):
                game.grid[pword.y_start][x] == pword.word[i]
                i += 1
        else:
            assert pword.x_start == pword.x_end
            for y in range(pword.y_start, pword.y_end):
                assert game.grid[y][pword.x_start] == pword.word[i]
                i += 1


def test_build_wordgraph():
    # TODO:
    # Update these tests with new model for v2
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
                        "a_0_0_linkedto_animal",
                        "a_0_0_linkedto_ato",
                        "a_0_4_linkedto_animal",
                    ]
                if linkable_letter.char == "l":
                    strings = [str(l) for l in linkable_letter.links]
                    assert sorted(strings) == [
                        "l_3_5_linkedto_animal",
                    ]
                if linkable_letter.char == "n":
                    strings = [str(l) for l in linkable_letter.links]
                    assert sorted(strings) == [
                        "n_1_1_linkedto_animal",
                    ]
        if node.word == "ato":
            strings = [str(l) for l in node.linkable_letters[0].links]
            assert sorted(strings) == [
                "a_0_0_linkedto_anel",
                "a_0_0_linkedto_animal",
                "a_0_4_linkedto_animal",
            ]

        if node.word == "animal":
            for idx, linkable_letter in enumerate(node.linkable_letters):
                if linkable_letter.char == "a":
                    if linkable_letter.index == 0:
                        strings = [str(l) for l in linkable_letter.links]
                        assert sorted(strings) == [
                            "a_0_0_linkedto_anel",
                            "a_0_0_linkedto_ato",
                        ]

                    if linkable_letter.index == 4:
                        strings = [str(l) for l in linkable_letter.links]
                        assert sorted(strings) == [
                            "a_4_0_linkedto_anel",
                            "a_4_0_linkedto_ato",
                        ]
                if linkable_letter.char == "l":
                    strings = [str(l) for l in linkable_letter.links]
                    assert sorted(strings) == [
                        "l_5_3_linkedto_anel",
                    ]
                if linkable_letter.char == "n":
                    strings = [str(l) for l in linkable_letter.links]
                    assert sorted(strings) == [
                        "n_1_1_linkedto_anel",
                    ]


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


def test_search_on_graph():
    input_list = ["anel", "animal", "ato"]
    graph = WordGraph(input_list)
    path_matrix = []
    search(graph.nodes[0], [], path_matrix, set())
    print(path_matrix)
    print(len(path_matrix))
    print(len(path_matrix[0]))
    assert path_matrix
    assert False


if __name__ == "__main__":
    unittest.main()
