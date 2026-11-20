# Chapter 5: strings.


def clean_name(raw: str) -> str:
    return " ".join(raw.split()).title()


def count_words(text: str) -> int:
    return len(text.split())
