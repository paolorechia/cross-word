from grid_generator.src.main import WordPicker, CrossWordGame

if __name__ == "__main__":
    word_picker = WordPicker("dictionary_builder/results/consolidated_with_freq.json", stop_word_offset=0, most_frequents=100)
    game = CrossWordGame(word_picker, num_words=4, max_pathes=10)
    print("Got game...")
    print(game)
    hints = game.get_hints()
