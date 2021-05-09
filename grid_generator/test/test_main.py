
import unittest

from grid_generator.src.main import (
    generate,
    CrossWordGame,
    WordGraph,
    WordOrientation
)

def test_generate():
    game : CrossWordGame = generate()
    print(game)
    print([w.word for w in game.placed_words])
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
    input_list = ["anel", "animal", "ato"]
    graph = WordGraph(input_list)

    assert len(graph.nodes) == len(input_list)

    saved_list = [n.word for n in graph.nodes]
    sorted(saved_list) == sorted(input_list)
    for node in graph.nodes:
        if node.word == "anel":
            strings = [str(l) for l in node.links]
            assert sorted(strings) == [
                'a_0_0_linkedto_animal',
                'a_0_0_linkedto_ato',
                'a_0_4_linkedto_animal',
                'l_3_5_linkedto_animal',
                'n_1_1_linkedto_animal',
            ]

        if node.word == "ato":
            strings = [str(l) for l in node.links]
            assert sorted(strings) == [
                'a_0_0_linkedto_anel',
                'a_0_0_linkedto_animal',
                "a_0_4_linkedto_animal"
            ]

        if node.word == "animal":
            strings = [str(l) for l in node.links]
            assert sorted(strings) == [
                'a_0_0_linkedto_anel',
                'a_0_0_linkedto_ato',
                'a_4_0_linkedto_anel',
                'a_4_0_linkedto_ato',
                'l_5_3_linkedto_anel',
                'n_1_1_linkedto_anel',
            ]


if __name__ == "__main__":
    unittest.main()