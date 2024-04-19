import math
from collections import defaultdict, Counter


def match_action(file, actions):
    pass


def match_actions(files, actions):
    result = []
    for file in files:
        result.append(match_action(file, actions))
    return result


def create_corpus(actions):
    doc_freq = defaultdict(int)
    total_docs = len(actions)

    for action in actions:

        unique_tokens = set(action.classes)
        for token in unique_tokens:
            doc_freq[token] += 1

    idf = {token: math.log(total_docs / freq) for token, freq in doc_freq.items()}

    for action in actions:
        tf = Counter(action.classes)
        total_tokens = len(action.classes)
        tfidf = {token: (count / total_tokens) * idf[token] for token, count in tf.items()}

        action.tfidf_vector = tfidf
