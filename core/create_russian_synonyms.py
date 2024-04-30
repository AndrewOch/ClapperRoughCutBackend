import ssl
import pymorphy2

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

morph = pymorphy2.MorphAnalyzer()


def get_normal_form(word):
    parsed_word = morph.parse(word)[0]
    return parsed_word.normal_form


def get_russian_synonyms(word):
    normal_form = get_normal_form(word)
    synonyms = {normal_form}
    return ', '.join(synonyms)


# with open('classes/daytime.txt', 'r') as classes_file, open('classes_ru/daytime.txt', 'r') as classes_ru_file, open(
#         'classes_data_ru/daytime_classes_synonyms.txt', 'w') as synonyms_file:
#     for eng_class, ru_class in zip(classes_file, classes_ru_file):
#         eng_class_name = eng_class.strip()
#         ru_class_name = ru_class.strip()
#         ru_synonyms = get_russian_synonyms(ru_class_name)
#         synonyms_file.write(f'{eng_class_name}: {ru_synonyms}\n')


with open('classes/action_classes.txt', 'r') as classes_file, open('classes_ru/action_classes.txt', 'r') as classes_ru_file, open(
        'classes_data_ru/action_classes_synonyms.txt', 'w') as synonyms_file:
    for eng_class, ru_class in zip(classes_file, classes_ru_file):
        eng_class_name = eng_class.strip()
        ru_class_name = ru_class.strip()
        ru_synonyms = get_russian_synonyms(ru_class_name)
        synonyms_file.write(f'{eng_class_name}: {ru_synonyms}\n')