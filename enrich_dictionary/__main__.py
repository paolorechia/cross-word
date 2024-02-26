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
    language = sys.argv[1]
    try:
        enricher = supported_languages[language]
    except KeyError as exc:
        raise KeyError(f"Unsupported language: {language}") from exc

    enricher.run()
