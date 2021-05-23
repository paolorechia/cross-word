from grid_generator.src.main import WordPicker, CrossWordGame

if __name__ == "__main__":
    word_picker = WordPicker(
        "dictionary_builder/results/consolidated_with_freq.json",
        stop_word_offset=0,
        most_frequents=100,
    )
    game = CrossWordGame(word_picker, num_words=4, max_pathes=10)
    print("Got game...")
    print("Answer:")
    print(game)

    print("Masked game")
    print(game.get_mask())

    print("Hints")
    hints = game.get_hints()
    for h in hints:
        coord = h[0]
        print(coord)
        actual_hints = h[1]
        for hint in actual_hints:
            print(">>>> ", hint)
