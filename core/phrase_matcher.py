import re
import string
from fonetika.soundex import RussianSoundex
from icecream import ic
from project.Subtitle import MatchingResult, Subtitle

soundex = RussianSoundex(delete_first_letter=True)
soundex_dictionary = {}


def soundex_transform(text):
    if text in soundex_dictionary:
        return soundex_dictionary[text]
    else:
        result = soundex.transform(text)
        soundex_dictionary[text] = result
        return result


def remove_punctuation(txt):
    punct_set = set(string.punctuation)
    no_punct = "".join(char for char in txt if char not in punct_set)
    return no_punct


def has_russian_letters(text):
    pattern = r'[а-яА-ЯёЁ]'
    return re.search(pattern, text) is not None


def remove_enclosed_text(text: str) -> str:
    result = text
    result = re.sub(r"\[.*?\]", "", result)
    result = re.sub(r"\(.*?\)", "", result)
    result = re.sub(r"<.*?>", "", result)
    result = re.sub(r"\*.*?\*", "", result)
    return result.strip()


def match_phrases(files, phrases, threshold=0.33):
    results = []
    for file in files:
        best_phrase, segments_data, best_cross_length = _match_phrase(file['subtitles'], phrases,
                                                                      file["truePhraseId"])
        if best_phrase:
            new_subtitles = _create_new_subtitles(file['subtitles'], segments_data, best_phrase)
            match_phrase_file_response = {
                "subtitles": new_subtitles,
                "id": file['id']
            }
            accuracy = min(best_cross_length / len(best_phrase.prepared_soundex), 1)
            if best_cross_length < 8 and accuracy < threshold:
                match_phrase_file_response = {
                    "subtitles": [],
                    "id": file['id']
                }
                match_phrase_response = {
                    "file": match_phrase_file_response
                }
                results.append(match_phrase_response)
            else:
                match_phrase_response = {
                    "file": match_phrase_file_response,
                    "best_match": {
                        "phrase_id": str(best_phrase.phrase_id),
                        "accuracy": accuracy
                    }
                }
                results.append(match_phrase_response)
        else:
            match_phrase_file_response = {
                "subtitles": [],
                "id": file['id']
            }
            match_phrase_response = {
                "file": match_phrase_file_response
            }
            results.append(match_phrase_response)
    return results


def _match_phrase(subtitles, phrases, truePhraseId):
    sub_soundex = [soundex_transform(processed_text)
                   for sub in subtitles
                   if (processed_text := remove_punctuation(remove_enclosed_text(sub.text))) and
                   has_russian_letters(processed_text)]
    best_phrase = None
    best_segments = []
    best_cross_length = 0

    for phrase in phrases:
        if len(phrase.prepared_soundex) == 0:
            continue
        matches = []
        start_idx = 0
        phrase_end = -1
        matched_segment_end = -1
        max_cross_length = 0
        cross_length = 0
        while start_idx < len(sub_soundex):
            segment_length, new_start, is_matching, phrase_start = _check_match(sub_soundex,
                                                                                phrase.prepared_soundex,
                                                                                start_idx)
            length = segment_length if is_matching else 0
            if segment_length > 0:
                end_idx = start_idx + segment_length - 1
                matches.append((start_idx, end_idx, length))
                next_matched_segment_start = start_idx
                start_idx = new_start
                if not is_matching:
                    continue
                if phrase_start > phrase_end and (phrase_end < 0 or abs(
                        (phrase_start - phrase_end - 1) - (next_matched_segment_start - matched_segment_end)) < 2):
                    cross_length += length
                    phrase_end = phrase_start + length - 1
                else:
                    if max_cross_length < cross_length:
                        max_cross_length = cross_length
                    cross_length = length
                    phrase_end = phrase_start + length - 1
                matched_segment_end = end_idx
        if max_cross_length < cross_length:
            max_cross_length = cross_length
        acc = (max_cross_length / len(phrase.prepared_soundex))
        if truePhraseId == phrase.phrase_id and acc < 0.33 and max_cross_length < 8:
            segment_texts = []
            for start_idx, end_idx, match_count in matches:
                segment_text = ''.join(sub.text for sub in subtitles[start_idx:end_idx + 1])
                segment_texts.append(f"[{match_count}] {segment_text}")
            ic(f"{acc:.2f} {max_cross_length} {len(phrase.prepared_soundex)}", segment_texts)
        if len(matches) > 0 and max_cross_length > best_cross_length:
            best_cross_length = max_cross_length
            best_phrase = phrase
            best_segments = matches

    return best_phrase, best_segments, best_cross_length


def _check_match(sub_soundex, phrase_soundex, start_idx):
    idx = start_idx
    start = -1
    if sub_soundex[idx] in phrase_soundex:
        is_matching = True
        start = phrase_soundex.index(sub_soundex[idx])
        length = 1
        while (start + length < len(phrase_soundex) and idx + length < len(sub_soundex) and
               sub_soundex[idx + length] == phrase_soundex[start + length]):
            length += 1
        new_start = idx + length
    else:
        is_matching = False
        length = 1
        while idx + length < len(sub_soundex) and sub_soundex[idx + length] not in phrase_soundex:
            length += 1
        new_start = idx + length

    return length, new_start, is_matching, start


def _create_new_subtitles(subtitles, matches, phrase):
    new_subtitles = []
    for start, end, length in matches:
        combined_text = ' '.join(sub.text.strip() for sub in subtitles[start:end + 1])
        combined_start_time = subtitles[start].start_time
        combined_end_time = subtitles[end].end_time
        new_subtitles.append(Subtitle(text=combined_text,
                                      start_time=combined_start_time,
                                      end_time=combined_end_time,
                                      phrase_id=phrase.phrase_id,
                                      match_accuracy=length / len(phrase.prepared_soundex),
                                      best_matches=[MatchingResult(phrase=phrase, matching_count=length)]))
    return new_subtitles
