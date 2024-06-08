import math
from collections import defaultdict, Counter

import icecream


def read_words_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            words = file.readlines()
            words = [word.strip() for word in words]
            return words
    except FileNotFoundError:
        print(f"Файл '{file_path}' не найден.")
        return []


daytime_classes = read_words_from_file('core/classes/daytime.txt')
macro_locations = read_words_from_file('core/classes/macro_locations.txt')
locations = read_words_from_file('core/classes/locations.txt')


def create_corpus(actions):
    doc_freq = defaultdict(int)
    total_docs = len(actions)

    for action in actions:
        unique_tokens = set(action.classes)
        for token in unique_tokens:
            if token not in macro_locations and token not in locations and token not in daytime_classes:
                doc_freq[token] += 1

    idf = {token: math.log(total_docs / freq) for token, freq in doc_freq.items()}

    for action in actions:
        tf = Counter(action.classes)
        total_tokens = len(action.classes)
        tfidf = {token: (count / total_tokens) * idf[token] for token, count in tf.items() if token in idf}
        action.tfidf_vector = tfidf
    return idf


def vectorize_text(texts, idf):
    vectors = []
    for text in texts:
        tf = Counter(text)
        total_tokens = len(text)
        tfidf = {token: (count / total_tokens) * idf[token] for token, count in tf.items() if token in idf}
        vectors.append(tfidf)
    return vectors


def calculate_cosine_similarity(vector1, vector2):
    all_items = set(vector1.keys()).union(vector2.keys())
    vec1 = [vector1.get(item, 0) for item in all_items]
    vec2 = [vector2.get(item, 0) for item in all_items]

    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    norm1 = math.sqrt(sum(v1 * v1 for v1 in vec1))
    norm2 = math.sqrt(sum(v2 * v2 for v2 in vec2))

    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0


def match_action(file, actions, idf_corpus):
    file_vector = vectorize_text([file['classes']], idf_corpus)[0]
    icecream.ic(file_vector)
    max_similarity = 0
    best_action = None

    for action in actions:
        similarity = calculate_cosine_similarity(file_vector, action.tfidf_vector)
        if similarity > max_similarity:
            max_similarity = similarity
            best_action = action

    return best_action, max_similarity


def match_actions(files, actions, idf_corpus):
    result = []

    for file in files:
        file_classes = file['classes']
        file_daytime_classes = set(file_classes).intersection(set(daytime_classes))
        file_location_classes = set(file_classes).intersection(set(locations))
        file_macro_location_classes = set(file_classes).intersection(set(macro_locations))

        filtered_actions = []
        for action in actions:
            action_classes = set(action.classes)
            if (not daytime_classes or file_daytime_classes.intersection(action_classes) or not any(
                    cls in action_classes for cls in daytime_classes)) and \
                    (not locations or file_location_classes.intersection(action_classes) or not any(
                        cls in action_classes for cls in locations)):
                filtered_actions.append(action)

        if not filtered_actions:
            for action in actions:
                action_classes = set(action.classes)
                if (not daytime_classes or file_daytime_classes.intersection(action_classes) or not any(
                        cls in action_classes for cls in daytime_classes)) and \
                        (not macro_locations or file_macro_location_classes.intersection(action_classes) or not any(
                            cls in action_classes for cls in macro_locations)):
                    filtered_actions.append(action)

        best_action, max_similarity = None, 0
        for action in filtered_actions:
            similarity = calculate_cosine_similarity(vectorize_text([file_classes], idf_corpus)[0], action.tfidf_vector)
            if similarity > max_similarity:
                max_similarity = similarity
                best_action = action

        if best_action:
            result.append((file['id'], best_action.action_id, max_similarity))

    return result
