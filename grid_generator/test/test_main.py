
import unittest

from grid_generator.src.main import generate, CrossWordGame

def test_generate():
    game : CrossWordGame = generate()
    print(game)
    assert len(game.placed_words) == game.vertical_words + game.horizontal_words



if __name__ == "__main__":
    unittest.main()