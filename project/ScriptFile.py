from collections import Counter
from time import time

import pandas as pd
from icecream import icecream

from core.actions_matcher import create_corpus
from core.text_classifier import add_character_names_to_dict
from project.Action import Action
from project.Phrase import Phrase


class ScriptFile:
    def __init__(self, script_id, file_path, phrases, actions, character_names):
        self.script_id = script_id
        self.url = file_path
        self.character_names = character_names
        add_character_names_to_dict(character_names)
        self.phrases = [Phrase(**phrase) for phrase in phrases]
        start_time = time()
        self.actions = [Action(**action) for action in actions]
        icecream.ic(len(self.actions))
        end_time = time()
        print(f"Total processed in {end_time - start_time} seconds.")
        self.idf_corpus = create_corpus(self.actions)
        self.display_classes_statistics()

    def update(self, script_id, file_path, phrases, actions, character_names):
        self.script_id = script_id
        self.url = file_path
        self.phrases = [Phrase(**phrase) for phrase in phrases]
        self.character_names = character_names
        add_character_names_to_dict(character_names)

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
        self.idf_corpus = create_corpus(self.actions)
        self.display_classes_statistics()

    def display_classes_statistics(self):
        if len(self.actions) == 0:
            return
        all_classes = [cls for action in self.actions for cls in action.classes]
        classes_count = Counter(all_classes)
        df_classes = pd.DataFrame(classes_count.items(), columns=['Class', 'Frequency']).sort_values(by='Frequency',
                                                                                                     ascending=False).reset_index(
            drop=True)

        classes_csv_filename = f"stats/{self.script_id}_class_statistics.csv"
        df_classes.to_csv(classes_csv_filename, index=False)
        print(f"Classes statistics saved to {classes_csv_filename}")

        counts_data = []
        for action in self.actions:
            for (class_name, key), count in action.counts.items():
                counts_data.append({'Class_Name': class_name, 'Key': key, 'Count': count})
        df_counts = pd.DataFrame(counts_data).groupby(['Class_Name', 'Key'], as_index=False).sum().sort_values(
            by='Count', ascending=False)

        counts_csv_filename = f"stats/{self.script_id}_counts_statistics.csv"
        df_counts.to_csv(counts_csv_filename, index=False)
        print(f"Counts statistics saved to {counts_csv_filename}")

        unused_words_data = []
        for action in self.actions:
            for word, count in action.unused.items():
                unused_words_data.append({'Word': word, 'Count': count})
        df_unused_words = pd.DataFrame(unused_words_data).groupby('Word', as_index=False).sum().sort_values(by='Count',
                                                                                                            ascending=False)

        unused_words_csv_filename = f"stats/{self.script_id}_unused_words_statistics.csv"
        df_unused_words.to_csv(unused_words_csv_filename, index=False)
        print(f"Unused words statistics saved to {unused_words_csv_filename}")
