from core import text_classifier


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
