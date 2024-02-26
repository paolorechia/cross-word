from tqdm import tqdm
import json

def run():
    from transformers import AutoTokenizer, MistralForCausalLM
    import pathlib
    import guidance

    model = "mistralai/Mistral-7B-Instruct-v0.2"

    tokenizer = AutoTokenizer.from_pretrained(model, load_in_8bit=True)
    model = MistralForCausalLM.from_pretrained(model, load_in_8bit=True)
    llama = guidance.llms.Transformers(model, tokenizer)
    guidance.llm = llama

    program = guidance("""<s>[INST] You're an AI assistant help me build a cross-word puzzle.
To make a good game, we need to give good hints to the player.
For instance, given the word "horse", one might return the hint "Four-legged animal used throughly history as a mount".
Help me by creating more hints, hints should be separated by a newline.
For example:

horse=Four-legged animal used throughly history as a mount.
sun=Mass of glowing hot gases, the center of our solar system.
                       
[/INST]
{{word}}={{gen 'description' stop="\n" max_tokens=32}}
""")
    input_dictionary_path = (pathlib.Path.cwd() / "data" / "dictionary_en.json")
    with open(input_dictionary_path, "r") as fp:
        input_dictionary = json.load(fp)

    output_path = (pathlib.Path.cwd() / "data" / "hints.txt")
    print("Beginning generation loop")
    with open(output_path, "w") as fp:
        for word_obj in tqdm(input_dictionary):
            key = word_obj["word"]
            executed_program = program(
                word=key,
            )
            output = key + "=" + executed_program["description"] + "\n"
            print("Appending... ", output)
            fp.write(output)
            fp.flush()