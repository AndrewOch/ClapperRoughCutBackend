import re
import string

import icecream
from fonetika.soundex import RussianSoundex

from project.subtitle import MatchingResult, Subtitle

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


def remove_enclosed_text(text: str) -> str:
    result = text
    result = re.sub(r"\[.*?\]", "", result)
    result = re.sub(r"\(.*?\)", "", result)
    result = re.sub(r"<.*?>", "", result)
    result = re.sub(r"\*.*?\*", "", result)
    return result.strip()


def matching_sequence_lengths(text1, text2):
    words1 = remove_punctuation(text1).split()
    words2 = remove_punctuation(text2).split()
    sequences = []
    current_sequence_length = 0
    last_index = 0
    for word1 in words1:
        i = last_index
        for word2 in words2[last_index:]:
            i += 1
            soundex1 = soundex_transform(word1)
            soundex2 = soundex_transform(word2)
            if soundex1 == soundex2:
                if current_sequence_length > 0:
                    last_index = i
                    current_sequence_length += 1
                    break
                else:
                    if len(soundex1) > 7:
                        last_index = i
                        current_sequence_length += 1
                        break
            else:
                if current_sequence_length > 1:
                    sequences.append(current_sequence_length)
                current_sequence_length = 0
    if current_sequence_length > 1:
        sequences.append(current_sequence_length)
    return sequences


def longest_matching_sequence_length1(text1, text2):
    words1 = remove_punctuation(text1).split()
    words2 = remove_punctuation(text2).split()
    max_sequence_length = 0
    current_sequence_length = 0
    last_index = 0
    for word1 in words1:
        for i, word2 in enumerate(words2[last_index:]):
            soundex1 = soundex_transform(word1)
            soundex2 = soundex_transform(word2)
            if soundex1 == soundex2:
                current_sequence_length += 1
                last_index += i + 1
                break
            else:
                max_sequence_length = max(max_sequence_length, current_sequence_length)
                current_sequence_length = 0

    max_sequence_length = max(max_sequence_length, current_sequence_length)
    return max_sequence_length


def longest_matching_sequence_length(text, phrase_soundex):
    words = remove_punctuation(text).split()
    max_sequence_length = 0
    current_sequence_length = 0
    last_index = 0
    for word in words:
        for i, soundex2 in enumerate(phrase_soundex[last_index:]):
            soundex1 = soundex_transform(word)
            if soundex1 == soundex2:
                current_sequence_length += 1
                last_index += i + 1
                break
            else:
                max_sequence_length = max(max_sequence_length, current_sequence_length)
                current_sequence_length = 0

    max_sequence_length = max(max_sequence_length, current_sequence_length)
    return max_sequence_length


def match_phrases(files, phrases):
    result = []
    for file in files:
        icecream.ic(file)
        result.append(match_phrase(file, phrases))
    return result


def match_phrase(file, phrases):
    res = {}
    for subtitle in file['subtitles']:
        results = []
        for phrase in phrases:
            length = longest_matching_sequence_length(subtitle.text, phrase.prepared_soundex)
            if length == 0:
                continue
            results.append(MatchingResult(phrase=phrase, matching_count=length))
        res[subtitle] = results
    combinations = Subtitle.generate_matched_combinations(res)
    best_match = get_best_combination(combinations, phrases)
    if best_match is None:
        return {}
    file['subtitles'] = best_match[0]
    return {'file': file, 'best_match': best_match[1]}


def get_best_combination(combinations, phrases):
    best_accuracy = 0
    best_combination = []
    best_phrase = None

    for combination in combinations:
        accuracies = [
            subtitle.best_matches[0].match_accuracy
            for subtitle in combination
            if subtitle.best_matches is not None and subtitle.best_matches[0] is not None and subtitle.best_matches[
                0].match_accuracy is not None
        ]
        if accuracies:
            max_accuracy = max(accuracies)
            if max_accuracy > best_accuracy:
                best_accuracy = max_accuracy
                best_combination = combination
                index = accuracies.index(max_accuracy)
                if combination[index].best_matches[0] is None:
                    continue
                best_phrase = combination[index].best_matches[0].phrase
                best_phrase = next((phrase for phrase in phrases if phrase.phrase_id == best_phrase.phrase_id), None)

    if not best_phrase or not best_phrase.phrase_text:
        return None

    cleaned_phrase_text = remove_enclosed_text(best_phrase.phrase_text).strip()
    if not cleaned_phrase_text or cleaned_phrase_text.isspace():
        return None

    for subtitle in best_combination:
        length = longest_matching_sequence_length(subtitle.text.lower(), cleaned_phrase_text.lower())
        matching_result = MatchingResult(phrase=best_phrase, matching_count=length)
        subtitle.best_matches.append(matching_result)
        subtitle.phrase_id = best_phrase.phrase_id
        subtitle.match_accuracy = matching_result.match_accuracy

    return best_combination, best_phrase
