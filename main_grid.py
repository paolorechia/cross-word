from grid_generator.src.main import WordPicker, CrossWordGame

if __name__ == "__main__":
    word_picker = WordPicker("dictionary_builder/results/consolidated.json")
    game = CrossWordGame(word_picker, num_words=4, max_pathes=400)
    print("Got game...")
    print(game)
