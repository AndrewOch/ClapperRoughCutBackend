from transformers import MarianMTModel, MarianTokenizer, pipeline
import os
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading


class Translator:
    def __init__(self, model_name='Helsinki-NLP/opus-mt-ru-en', model_dir='../models/opus-mt-ru-en'):
        self.model_name = model_name
        self.model_dir = model_dir
        self.translator = None
        self.ensure_model()

    def ensure_model(self):
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            print(f'Загружаем и сохраняем модель {self.model_name}...')
            tokenizer = MarianTokenizer.from_pretrained(self.model_name)
            model = MarianMTModel.from_pretrained(self.model_name)
            tokenizer.save_pretrained(self.model_dir)
            model.save_pretrained(self.model_dir)
            print('Модель успешно сохранена.')
        else:
            print(f'Используется локальная модель из {self.model_dir}')
        self.translator = pipeline("translation_ru_to_en", model=self.model_dir, tokenizer=self.model_dir)

    def translate(self, text):
        if self.translator:
            translated_text = self.translator(text, max_length=512)
            return translated_text[0]['translation_text']
        else:
            raise Exception("Модель перевода не инициализирована.")


class TranslatorPool:
    def __init__(self, size, model_name='Helsinki-NLP/opus-mt-ru-en', model_dir='models/opus-mt-ru-en'):
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.translators = [Translator(model_name, model_dir) for _ in range(size)]
        self.executor = ThreadPoolExecutor(max_workers=size)
        self._start_workers()

    def _worker(self, translator):
        while True:
            task_id, text = self.input_queue.get()
            if text is None:
                self.input_queue.task_done()
                break
            try:
                translated_text = translator.translate(text)
                self.output_queue.put((task_id, translated_text))
            except Exception as exc:
                self.output_queue.put((task_id, None))
            finally:
                self.input_queue.task_done()

    def _start_workers(self):
        for translator in self.translators:
            self.executor.submit(self._worker, translator)

    def translate_text(self, text):
        task_id = threading.get_ident()
        self.input_queue.put((task_id, text))
        result = None
        while result is None:
            output_task_id, output_text = self.output_queue.get()
            if output_task_id == task_id:
                result = output_text
            else:
                self.output_queue.put(
                    (output_task_id, output_text))
        return result

    def shutdown(self):
        for _ in self.translators:
            self.input_queue.put((None, None))
        self.executor.shutdown(wait=True)


translator_pool = TranslatorPool(4)
