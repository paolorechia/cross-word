import aiohttp
import asyncio
from typing import List
from scrapy.selector import Selector as scp
from dataclasses import dataclass
import json
from unicodedata import normalize


endpoint_dicio = 'https://www.dicio.com.br/{}/'
endpoint_sinonimos = 'https://www.sinonimos.com.br/{}/'

async def get_word_from_dicio(session, word_object):
    word = norma(word_object["word"])
    print(f"Getting {word}")
    async with session.get(endpoint_dicio.format(word)) as resp:
        content = await resp.text()
        print(resp.status)

        sinonimos = []
        antonimos = []
        frases = []
        meaning = []

        if resp.status == 404:
            print(f"{word} not found!")
        elif resp.status == 200:
            s = scp(text=content)
            meaning = s.css(".significado.textonovo").xpath("span[not(@class)]/text()").getall()

            sinonimos_selectors = s.css(".adicional.sinonimos")
            if len(sinonimos_selectors) >= 1:
                sinonimos = sinonimos_selectors[0].css("span > a::text").getall()
            if len(sinonimos_selectors) >= 2:
                antonimos = sinonimos_selectors[1].css("span > a::text").getall()
            frases = [ f.css("span::text").get() if "span" in f.get() else f.css("::text").get() for f in s.css(".frase") ]
            print(f"Done getting {word}!")
        return {
            **word_object,
            "syn": sinonimos,
            "ant": antonimos,
            "sentences": frases,
            "description": meaning,
            "status_code": resp.status
        }


def norma(word):
    return normalize('NFKD', word).encode('ASCII','ignore').decode('ASCII').lower()

def read_word_list():
    with open("result.txt") as fp:
        return json.load(fp)

async def get_word_slice(word_slice, lower, upper):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for word in word_slice:
            task = asyncio.create_task(get_word_from_dicio(session, word))
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=False)
        with open(f"results/{lower}:{upper}_retrieved_definitions_slice.json", "w") as fp:
            json.dump(results, fp)

async def main():
    words = read_word_list()
    words = words[:8]
    print(words)
    print("CREATING TASKS")
    lower = 0
    slice_size = 3
    upper = slice_size
    for upper in range(slice_size, len(words), slice_size):
        word_slice = words[lower:upper]
        print(f"Slice ({lower}:{upper}): {[w['word'] for w in word_slice]}")
        l = lower
        lower = upper
        await get_word_slice(word_slice, l, upper)

    async with aiohttp.ClientSession() as session:
        remaining_ = words[upper:]
        print(f"Remainder ({upper}:{len(words)-1}) {[w['word'] for w in remaining_]}")
        await get_word_slice(remaining_, upper, len(words) -1)
        
# if __name__ == "__main__":
asyncio.run(main())