import string
from collections import defaultdict
from time import time

import icecream
import nltk
from nltk import pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from core.translator import translator_pool
import ssl
import re

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')


def read_words_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            words = file.readlines()
            words = [word.strip() for word in words]
            return words
    except FileNotFoundError:
        print(f"Файл '{file_path}' не найден.")
        return []


def load_dict_from_file(filename):
    data_dict = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            class_name, keywords = line.strip().split(': ')
            for keyword in keywords.split(', '):
                if keyword in data_dict:
                    print('CONFLICT', keyword, class_name, data_dict[keyword])
                data_dict[keyword] = class_name
    return data_dict


object_classes_dict = load_dict_from_file('core/classes_data/objects_classes_synonyms.txt')
location_classes_dict = load_dict_from_file('core/classes_data/location_classes_synonyms.txt')
audio_classes_dict = load_dict_from_file('core/classes_data/audio_classes_synonyms.txt')
action_classes_dict = load_dict_from_file('core/classes_data/action_classes_synonyms.txt')
daytime_classes_dict = load_dict_from_file('core/classes_data/daytime_classes_synonyms.txt')

natures = read_words_from_file("core/classes/natures.txt")
interiors = read_words_from_file("core/classes/interiors.txt")


def classify_object(tokens):
    classes_synonyms_counts = defaultdict(int)
    counted_classes = {}
    used_words = set()

    for key, class_name in object_classes_dict.items():
        key_words = set(key.split())
        if key_words.issubset(tokens):
            classes_synonyms_counts[(class_name, key)] += 1
            if class_name in counted_classes:
                counted_classes[class_name] += 1
            else:
                counted_classes[class_name] = 1
            used_words.update(key_words)

    classes = set()
    for class_name, count in counted_classes.items():
        classes.add(class_name)
        for i in range(2, count + 1):
            classes.add(f"{i} {class_name}")

    return classes, classes_synonyms_counts, used_words


def classify_location(tokens):
    classes, classes_synonyms_counts, used_words = _classify_from_dict(tokens, object_classes_dict)
    for class_name in list(classes):
        if class_name in natures:
            classes.add('nature')
        if class_name in interiors:
            classes.add('interior')
    return classes, classes_synonyms_counts, used_words


def classify_audio(tokens):
    return _classify_from_dict(tokens, audio_classes_dict)


def classify_action(tokens):
    return _classify_from_dict(tokens, action_classes_dict)


def classify_daytime(tokens, text):
    classes, classes_synonyms_counts, used_words = _classify_from_dict(tokens, daytime_classes_dict)

    time_matches = re.findall(r'\b(?:[01]?\d|2[0-3]):[0-5]\d\b', text)

    for match in time_matches:
        hours, minutes = map(int, match.split(':'))
        if 6 <= hours <= 11:
            classes.add('morning')
        elif 12 <= hours <= 17:
            classes.add('day')
        elif 18 <= hours <= 23:
            classes.add('evening')
        else:
            classes.add('night')

    return classes, classes_synonyms_counts, used_words


def _classify_from_dict(tokens, classes_dict):
    classes = set()
    classes_synonyms_counts = defaultdict(int)
    used_words = set()

    for key, class_name in classes_dict.items():
        key_words = set(key.split())
        if key_words.issubset(tokens):
            classes.add(class_name)
            classes_synonyms_counts[(class_name, key)] += 1
            used_words.update(key_words)

    return classes, classes_synonyms_counts, used_words


def classify_text(full_text):
    start_time = time()
    translated_text = translator_pool.translate_text(full_text)
    tokens = process_text(translated_text)

    classes = set()
    classes_synonyms_counts = defaultdict(int)
    all_used_words = set()

    classification_functions = [
        (classify_object, (tokens,)),
        (classify_location, (tokens,)),
        (classify_audio, (tokens,)),
        (classify_action, (tokens,)),
        (classify_daytime, (tokens, full_text)),
    ]

    for func, args in classification_functions:
        result_classes, result_counts, result_used_words = func(*args)
        classes.update(result_classes)
        for key, count in result_counts.items():
            classes_synonyms_counts[key] += count
        all_used_words.update(result_used_words)

    unused_words_counts = defaultdict(int)
    used_words_list = list(all_used_words)
    for token in tokens:
        if token not in used_words_list:
            unused_words_counts[token] += 1
    icecream.ic(full_text, tokens, classes)
    end_time = time()
    print(f"Action processed in {end_time - start_time} seconds.")
    return list(classes), classes_synonyms_counts, unused_words_counts


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def process_text(text):
    text_nopunct = ''.join([char for char in text if char not in string.punctuation])

    tokens = word_tokenize(text_nopunct)

    filtered_tokens = [word for word in tokens if word.lower() not in stopwords.words('english')]
    filtered_tokens = [word for word in filtered_tokens if re.match(r'^[A-Za-z]{1,15}$', word)]

    tagged_tokens = pos_tag(filtered_tokens)

    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = []
    for word, tag in tagged_tokens:
        wn_tag = get_wordnet_pos(tag)
        if wn_tag is None:

            lemma = lemmatizer.lemmatize(word.lower())
        else:
            lemma = lemmatizer.lemmatize(word.lower(), pos=wn_tag)
        lemmatized_tokens.append(lemma)

    return lemmatized_tokens
