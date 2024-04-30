from time import time

import core
from core import text_classifier
from collections import Counter
import pandas as pd


class Phrase:
    def __init__(self, phrase_id, text, phrase_text=""):
        self.phrase_id = phrase_id
        self.full_text = text
        self.phrase_text = phrase_text
        self.prepared_soundex, self.words_count = self.prepare()

    def prepare(self):
        text = self.phrase_text.lower()
        text = core.phrases_matcher.remove_enclosed_text(text)
        words = core.phrases_matcher.remove_punctuation(text).split()
        soundex_array = [core.phrases_matcher.soundex_transform(word) for word in words]
        return soundex_array, len(words)

    def to_json(self):
        return {
            "phrase_id": str(self.phrase_id),
        }


class Action:
    def __init__(self, action_id, text, last_update):
        self.action_id = action_id
        self.full_text = text
        self.last_update = last_update
        self.classes = []
        self.counts = {}
        self.unused = {}
        self.process_text()

    def to_json(self):
        return {
            "action_id": str(self.action_id),
        }

    def process_text(self):
        self.classes, self.counts, self.unused = text_classifier.classify_text(self.full_text)


class ScriptFile:
    def __init__(self, script_id, file_path, phrases, actions):
        self.script_id = script_id
        self.url = file_path
        self.phrases = [Phrase(**phrase) for phrase in phrases]
        start_time = time()
        self.actions = [Action(**action) for action in actions]
        end_time = time()
        print(f"Total processed in {end_time - start_time} seconds.")
        # self.display_classes_statistics()

    def update(self, script_id, file_path, phrases, actions):
        self.script_id = script_id
        self.url = file_path
        self.phrases = [Phrase(**phrase) for phrase in phrases]

        existing_actions_dict = {action.action_id: action for action in self.actions}

        new_action_ids = {action['action_id'] for action in actions}

        for new_action in actions:
            action_id = new_action['action_id']
            if action_id in existing_actions_dict:
                existing_action = existing_actions_dict[action_id]
                if new_action['last_update'] > existing_action.last_update:
                    existing_actions_dict[action_id] = Action(**new_action)
            else:

                existing_actions_dict[action_id] = Action(**new_action)

        for action_id in list(existing_actions_dict.keys()):
            if action_id not in new_action_ids:
                del existing_actions_dict[action_id]

        self.actions = list(existing_actions_dict.values())
        # self.display_classes_statistics()

    def display_classes_statistics(self):
        if len(self.actions) == 0:
            return
        all_classes = [cls for action in self.actions for cls in action.classes]
        classes_count = Counter(all_classes)
        df_classes = pd.DataFrame(classes_count.items(), columns=['Class', 'Frequency']).sort_values(by='Frequency', ascending=False).reset_index(drop=True)
        print("Classes Frequency Statistics:")
        print(df_classes)
        classes_csv_filename = f"stats/{self.script_id}_class_statistics.csv"
        df_classes.to_csv(classes_csv_filename, index=False)
        print(f"Classes statistics saved to {classes_csv_filename}")

        counts_data = []
        for action in self.actions:
            for (class_name, key), count in action.counts.items():
                counts_data.append({'Class_Name': class_name, 'Key': key, 'Count': count})
        df_counts = pd.DataFrame(counts_data).groupby(['Class_Name', 'Key'], as_index=False).sum().sort_values(by='Count', ascending=False)
        print("Classes Synonyms Counts Statistics:")
        print(df_counts)
        counts_csv_filename = f"stats/{self.script_id}_counts_statistics.csv"
        df_counts.to_csv(counts_csv_filename, index=False)
        print(f"Counts statistics saved to {counts_csv_filename}")

        unused_words_data = []
        for action in self.actions:
            for word, count in action.unused.items():
                unused_words_data.append({'Word': word, 'Count': count})
        df_unused_words = pd.DataFrame(unused_words_data).groupby('Word', as_index=False).sum().sort_values(by='Count',
                                                                                                            ascending=False)
        print("Unused Words Statistics:")
        print(df_unused_words)
        unused_words_csv_filename = f"stats/{self.script_id}_unused_words_statistics.csv"
        df_unused_words.to_csv(unused_words_csv_filename, index=False)
        print(f"Unused words statistics saved to {unused_words_csv_filename}")
