from collections import Counter
import random
import os
import string
import sys

stopWordsList = [
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "her",
    "hers",
    "herself",
    "it",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "should",
    "now",
]

DELIMITERS = " \t,;.?!-:@[](){}_*/"
TRANSLATOR = str.maketrans({d: " " for d in DELIMITERS})


def getIndexes(seed: str) -> list[int]:
    random.seed(seed)
    n = 10000
    number_of_lines = 50000
    ret = []
    for i in range(0, n):
        ret.append(random.randint(0, 50000 - 1))
    return ret


def process(userID: str):
    indexes = getIndexes(userID)
    ret = []
    # TODO
    word_lists: list[list[str]] = []

    try:
        while sentence := input().translate(TRANSLATOR):
            word_lists.append(
                [
                    word.strip()
                    for word in sentence.casefold().split()
                    if word not in stopWordsList
                ]
            )
    except EOFError:
        pass

    # count the occurrence
    word_counts: Counter[str] = Counter()
    for i in indexes:
        word_counts.update(word_lists[i])

    top20 = sorted(
        word_counts.items(),
        key=lambda x: (-x[1], x[0]),
    )[:20]

    for word, _ in top20:
        print(word)


process(sys.argv[1])
