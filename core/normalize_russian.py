import pymorphy2
import nltk
from nltk.corpus import stopwords
import os

nltk.download('stopwords')
stop_words = set(stopwords.words('russian'))

morph = pymorphy2.MorphAnalyzer()


def process_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = []
    for line in lines:
        if not line.strip():
            continue
        class_name, words = line.split(':')
        words = words.split(',')
        processed_words = []
        for word in words:
            word = word.strip()
            if word not in stop_words:
                normal_form = morph.parse(word)[0].normal_form
                processed_words.append(normal_form)
        processed_line = f"{class_name.strip()}: {', '.join(processed_words)}"
        processed_lines.append(processed_line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(processed_lines))


def process_all_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            process_text_file(file_path)


directory_path = 'classes_data'

process_all_files(directory_path)
