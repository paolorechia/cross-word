from tqdm import tqdm

def run():
    import json
    import nltk
    import stanza
    from collections import Counter
    import pathlib


    data_dir = (pathlib.Path.cwd() / "data").resolve()
    print("Data dir: ", data_dir)


    dictionary = Counter()
    for file_ in nltk.corpus.gutenberg.fileids():
        words = nltk.corpus.gutenberg.words(file_)
        print(type(words), len(words))
        for word in words:
            if len(str(word)) >= 5 and str(word).isalpha() and str(word.lower()) == str(word):
                dictionary[str(word).lower()] += 1


    stopwords = nltk.corpus.stopwords.words('english')
    frequent_words = {}
    for key, item in dictionary.items():
        if item > 3 and item not in stopwords:
            frequent_words[key] = item
    
    print(len(frequent_words))

    output_filepath = (pathlib.Path(data_dir) / "gutenberg.json").resolve() 
    with open(output_filepath, "w") as fp:
        json.dump(frequent_words, fp, indent=4)

    nlp = stanza.Pipeline('en')

    processed = []
    for key, freq in tqdm(frequent_words.items()):
        doc = nlp(key)
        for sentence in doc.sentences:
            for word in sentence.words:
                obj = {
                    "word": key,
                    "lemma": word.lemma,
                    "upos": word.upos,
                    "feats": word.feats,
                    "freq": freq,
                }
                processed.append(obj)

    output_filepath = (pathlib.Path(data_dir) / "dictionary_en.json").resolve() 
    with open(output_filepath, "w", encoding="utf-8") as fp:
        json.dump(processed, fp)
