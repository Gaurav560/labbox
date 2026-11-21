# Chapter 7: strings. Pocket tidies up text that people typed.


def clean_name(raw):
    return " ".join(raw.split()).title()


def count_words(text):
    return len(text.split())
