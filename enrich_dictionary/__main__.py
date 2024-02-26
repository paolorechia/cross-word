import sys

from enrich_dictionary.enrichers import english


supported_languages = {
     "en": english,
}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"""Usage: {sys.argv[0]} [language-code]
    
    Supported languages: {supported_languages.keys()}
""")