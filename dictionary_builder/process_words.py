import stanza
import re
import json

# stanza.download('pt')
nlp = stanza.Pipeline('pt')

with open("Downloads/br-utf8.txt", "r") as fp:
        lines = fp.readlines()

processed = []
lines = [re.sub("\s", "", line) for line in lines]
for line in lines:
    doc = nlp(line)
    for sentence in doc.sentences:
        for word in sentence.words:
            obj = {
                "word": line,
                "lemma": word.lemma,
                "upos": word.upos,
                "feats": word.feats,
            }
            print(obj)
            processed.append(obj)

print(processed)
with open("result.txt", "w", encoding="utf-8") as fp:
    json.dump(processed, fp)