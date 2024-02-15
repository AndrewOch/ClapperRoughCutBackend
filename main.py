from flask import Flask, request, jsonify
import MFCC
import text_matcher
import os

app = Flask(__name__)


@app.route('/extract_mfcc', methods=['POST'])
def extract_mfcc():
    file = request.files['file']
    temp_path = os.path.join('temp', file.filename)
    file.save(temp_path)
    mfccs = MFCC.get_normalized_mfcc(audio_file=temp_path)
    os.remove(temp_path)  # Удаляем файл после обработки
    return jsonify(mfccs)


@app.route('/distance_dtw', methods=['POST'])
def distance_dtw():
    data = request.json
    mfccs1 = data['mfccs1']
    mfccs2 = data['mfccs2']
    distance = MFCC.get_dtw(mfccs1=mfccs1, mfccs2=mfccs2)
    return jsonify([distance])


@app.route('/matching_sequence_lengths', methods=['POST'])
def matching_sequence_lengths():
    data = request.json
    text1 = data['text1']
    text2 = data['text2']
    sequence_lengths = text_matcher.matching_sequence_lengths(text1=text1, text2=text2)
    return jsonify(sequence_lengths)


@app.route('/longest_matching_sequence_length', methods=['POST'])
def longest_matching_sequence_length():
    data = request.json
    text1 = data['text1']
    text2 = data['text2']
    sequence_length = text_matcher.longest_matching_sequence_length(text1=text1, text2=text2)
    return jsonify(sequence_length)


if __name__ == '__main__':
    app.run(debug=True)
