from typing import Optional

from project.Phrase import Phrase


class MatchingResult:
    def __init__(self, phrase: Phrase, matching_count: int):
        self.phrase = phrase
        self.matching_count = matching_count

    @property
    def match_accuracy(self) -> Optional[float]:
        return self.matching_count / self.phrase.words_count

    def to_json(self):
        return {
            "phrase_id": self.phrase.phrase_id,
            "matching_count": self.matching_count,
        }
