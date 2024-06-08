from typing import List, Optional, Dict, Any

from project.MatchingResult import MatchingResult


class Subtitle:
    def __init__(self, text: str, start_time: float, end_time: float, phrase_id: Optional[str] = None,
                 match_accuracy: Optional[float] = None, best_matches: Optional[List[MatchingResult]] = None):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.phrase_id = phrase_id
        self.match_accuracy = match_accuracy
        self.best_matches = best_matches

    def to_json(self):
        return {
            "text": self.text,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "phrase_id": str(self.phrase_id) if self.phrase_id else "",
            "match_accuracy": self.match_accuracy,
            "best_matches": [match.to_json() for match in self.best_matches if match] if self.best_matches else ""
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            text=data['text'],
            start_time=data['start_time'],
            end_time=data['end_time']
        )

    @property
    def accuracy(self) -> Optional[float]:
        if self.best_matches:
            return max(match.match_accuracy for match in self.best_matches if match.match_accuracy is not None)
        return None

    @staticmethod
    def merge(subtitles: List['Subtitle']) -> 'Subtitle':
        text = " ".join(sub.text for sub in subtitles)
        start_time = min(sub.start_time for sub in subtitles)
        end_time = max(sub.end_time for sub in subtitles)

        combined_matches_dict = {}
        for sub in subtitles:
            if not sub.best_matches:
                continue
            for match in sub.best_matches:
                if match.phrase.phrase_id not in combined_matches_dict:
                    combined_matches_dict[match.phrase.phrase_id] = match
                    continue
                existing = combined_matches_dict[match.phrase.phrase_id]
                combined_matches_dict[match.phrase.phrase_id] = MatchingResult(
                    phrase=match.phrase,
                    matching_count=existing.matching_count + match.matching_count
                )

        combined_matches = list(combined_matches_dict.values())

        return Subtitle(
            text=text,
            start_time=start_time,
            end_time=end_time,
            best_matches=combined_matches
        )

    @staticmethod
    def generate_matched_combinations(subtitle_matches: Dict['Subtitle', List[MatchingResult]]) -> List[
        List['Subtitle']]:
        subtitles = list(subtitle_matches.keys())

        def recurse(subtitles: List['Subtitle'], index: int, current_combination: List['Subtitle'],
                    all_combinations: List[List['Subtitle']]):
            if index == len(subtitles):
                all_combinations.append(current_combination)
                return

            for end_index in range(index, len(subtitles)):
                range_to_merge = subtitles[index:end_index + 1]
                merged_subtitle = Subtitle.merge(range_to_merge)
                merged_subtitle.best_matches = [
                    max(subtitle_matches[sub], key=lambda x: x.matching_count, default=None) for sub in range_to_merge
                    if sub in subtitle_matches
                ]
                recurse(subtitles, end_index + 1, current_combination + [merged_subtitle], all_combinations)

            if index > 0:
                current_subtitle = subtitles[index]
                current_subtitle.best_matches = sorted(subtitle_matches.get(current_subtitle, []),
                                                       key=lambda x: x.matching_count)
                recurse(subtitles, index + 1, current_combination + [current_subtitle], all_combinations)

        all_combinations = []
        recurse(subtitles, 0, [], all_combinations)

        return [
            [sub for sub in combination if sub.best_matches]
            for combination in all_combinations
        ]
