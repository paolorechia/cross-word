import stanza
import re
import json
import sys

from dictionary_builder.builders import english, portuguese


supported_languages = {
     "en": english,
     "pt": portuguese,
}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"""Usage: {sys.argv[0]} [language-code]
    
    Supported languages:
        * en (English)
        * pt (Portugese)               
""")
    
    language = sys.argv[1]
    try:
        dictionary_builder = supported_languages[language]
    except KeyError as exc:
        raise KeyError(f"Unsupported language: {language}") from exc

    dictionary_builder.run()
