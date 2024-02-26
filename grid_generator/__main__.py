import sys
from grid_generator.src.grid_generator import WordPicker, CrossWordGame

available_languages = {"en"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"""Usage: {sys.argv[0]} lang

    Available languages: {available_languages}
""")

    lang = sys.argv[1]
    assert lang in available_languages, f"{lang} not in {available_languages}"

    word_picker = WordPicker(
        f"data/enriched_dictionary_{lang}.json",
        stop_word_offset=0,
        most_frequents=1000,
    )
    game = CrossWordGame(word_picker, num_words=6, max_pathes=100, threads=1)
    print("Got game...")
    print("Answer:")
    print(game)

    print("Masked game")
    print(game.get_mask())

    print("Hints")
    hints = game.get_hints()
    for hint in hints:
        print(">>>> ", hint)
