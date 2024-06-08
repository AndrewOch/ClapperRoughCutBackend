import core


class Phrase:
    def __init__(self, phrase_id, text, phrase_text=""):
        self.phrase_id = phrase_id
        self.full_text = text
        self.phrase_text = phrase_text
        self.prepared_soundex, self.words_count = self.prepare()

    def prepare(self):
        text = self.phrase_text.lower()
        text = core.phrase_matcher.remove_enclosed_text(text)
        words = core.phrase_matcher.remove_punctuation(text).split()
        soundex_array = [core.phrase_matcher.soundex_transform(word) for word in words]
        return soundex_array, len(words)

    def to_json(self):
        return {
            "phrase_id": str(self.phrase_id),
        }
