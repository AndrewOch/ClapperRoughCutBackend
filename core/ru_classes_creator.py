import os

from core.translator import translator_pool

if not os.path.exists('classes_ru'):
    os.makedirs('classes_ru')

# with open('classes/video_classes.txt', 'r', encoding='utf-8') as file:
#     lines = file.readlines()
#
# translated_lines = []
#
# for line in lines:
#     translated_line = translator_pool.translate_text(line.strip())
#     translated_lines.append(translated_line.lower() + '\n')
#
# with open('classes_ru/video_classes.txt', 'w', encoding='utf-8') as file:
#     file.writelines(translated_lines)
#
# print("Перевод завершен и сохранен в 'classes_ru/daytime.txt'")
