
from grid_generator.src.main import WordGraph
from grid_generator.test.test_main import sample_json_word_dict

if __name__ == "__main__":
    words = [ w["word"] for w in sample_json_word_dict ]
    lower_bound = 10
    upper_bound = 11
    for bound in range(lower_bound, upper_bound):
        subset = words[:bound]
        print(f"Testing subset of {len(subset)} words")
        graph = WordGraph(subset)
        graph.generate_all_pathes(max_pathes=100, max_iterations=1000, randomized=True)
    # print(graph.pathes)
