import json
import pathlib

def run():
    data_dir = (pathlib.Path.cwd() / "data").resolve()
    input_dictionary_path = (pathlib.Path(data_dir) / "dictionary_en.json").resolve() 
    hints_path = (pathlib.Path(data_dir) / "hints.txt").resolve()
    output_path = (pathlib.Path(data_dir) / "enriched_dictionary_en.json").resolve()
    

    enriched = []

    with open(hints_path, "r", encoding="utf-8") as fp:
        hints = fp.readlines()

    with open(input_dictionary_path, "r", encoding="utf-8") as fp:
        en_dictionary = {word["word"]: word for word in json.load(fp)}


    for line in hints:
        if "=" not in line:
            continue
        tmp = line.split("=")
        word = tmp[0]
        hint = tmp[1]

        if word in en_dictionary:
            enriched.append({**en_dictionary[word], "hint": [hint.strip("\n")]})


    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(enriched, fp, indent=4)
