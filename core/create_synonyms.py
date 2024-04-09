import ssl
import string

import nltk
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn, stopwords, wordnet
from nltk.stem import WordNetLemmatizer

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


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

    tagged_tokens = pos_tag(filtered_tokens)

    lemmatized_tokens = []
    for word, tag in tagged_tokens:
        wn_tag = get_wordnet_pos(tag)
        if wn_tag is None:

            lemma = lemmatizer.lemmatize(word.lower())
        else:
            lemma = lemmatizer.lemmatize(word.lower(), pos=wn_tag)
        lemmatized_tokens.append(lemma)

    return lemmatized_tokens


def get_synonyms(word):
    synonyms = set([' '.join(process_text(word.replace('_', ' ')))])
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            cleaned_lemmatized_word = ' '.join(process_text(lemma.name()))
            if cleaned_lemmatized_word:
                synonyms.add(cleaned_lemmatized_word)
    return ', '.join(synonyms)


with open('classes/daytime.txt', 'r') as classes_file, open('classes_data/daytime_classes_synonyms.txt',
                                                            'w') as synonyms_file:
    for line in classes_file:
        class_name = line.strip()
        synonyms = get_synonyms(class_name)
        synonyms_file.write(f'{class_name}: {synonyms}\n')

with open('classes/video_classes.txt', 'r') as classes_file, open('classes_data/objects_classes_synonyms.txt',
                                                                  'w') as synonyms_file:
    for line in classes_file:
        class_name = line.strip()
        synonyms = get_synonyms(class_name)
        synonyms_file.write(f'{class_name}: {synonyms}\n')

with open('classes/audio_classes.txt', 'r') as classes_file, open('classes_data/audio_classes_synonyms.txt',
                                                                  'w') as synonyms_file:
    for line in classes_file:
        class_name = line.strip()
        synonyms = get_synonyms(class_name)
        synonyms_file.write(f'{class_name}: {synonyms}\n')

with open('classes/action_classes.txt', 'r') as classes_file, open('classes_data/action_classes_synonyms.txt',
                                                                   'w') as synonyms_file:
    for line in classes_file:
        class_name = line.strip()
        synonyms = get_synonyms(class_name)
        synonyms_file.write(f'{class_name}: {synonyms}\n')
