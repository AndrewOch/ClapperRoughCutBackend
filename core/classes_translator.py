# Подключение библиотеки
from fonetika.soundex import RussianSoundex
import re

from icecream import icecream

# Инициализация Soundex с удалением первой буквы
soundex = RussianSoundex(delete_first_letter=True)
soundex_dictionary = {}


def soundex_transform(word):
    """ Преобразует одно слово в его код Soundex, используя кэширование для повышения производительности. """
    if word in soundex_dictionary:
        return soundex_dictionary[word]
    else:
        result = soundex.transform(word)
        soundex_dictionary[word] = result
        return result


def transform_texts_to_soundex(texts):
    """ Преобразует каждый текст в массиве в строку кодов Soundex. """
    transformed_texts = []  # Создаем пустой список для хранения результатов
    for text in texts:
        words = re.findall(r'\w+', text)  # Извлечение слов из текста
        soundex_codes = [soundex_transform(word.lower()) for word in words]  # Преобразование каждого слова
        transformed_texts.append(' '.join(soundex_codes))  # Добавление преобразованного текста в список результатов
    return transformed_texts  # Возвращаем список преобразованных текстов


# Пример использования
# texts = [
#     "Запись идёт? Начали!",
#     "Здорово! Я был",
#     "эээ в лагере научной фантастики",
#     "Не давайте еще раз",
#     "Здорово! Я был в лагере научной фантастики",
#     "мы даже запускали",
#     "модель ракеты",
#     "Стоп снято!"
# ]
# transformed_texts = transform_texts_to_soundex(texts)
# icecream.ic(transformed_texts)
