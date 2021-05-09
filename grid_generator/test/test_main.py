
import unittest

from grid_generator.src.main import generate, CrossWordGame, WordOrientation

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


if __name__ == "__main__":
    unittest.main()