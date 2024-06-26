import json

from flask import Flask, request, jsonify
from icecream import icecream

from core.actions_matcher import match_actions
from core.json_encoder import object_to_json
from core.phrase_matcher import match_phrases
from project.RoughCutProject import projects_storage, RoughCutProject
from project.ScriptFile import ScriptFile
from project.Subtitle import Subtitle

app = Flask(__name__)


def create_project_if_not_exists(project_id):
    if project_id not in projects_storage:
        projects_storage[project_id] = RoughCutProject()


@app.route('/script', methods=['POST'])
def upload_script():
    data = request.json
    project_id = data['project_id']
    create_project_if_not_exists(project_id)
    if projects_storage[project_id].script_file is not None:
        script_file = projects_storage[project_id].script_file
        script_file.update(script_id=data['script_id'], file_path=data['file_path'], phrases=data['phrases'],
                           actions=data['actions'], character_names=data['character_names'])
        app.logger.info(f'Сценарий обновлён ${script_file}')
    else:
        script_file = ScriptFile(script_id=data['script_id'], file_path=data['file_path'], phrases=data['phrases'],
                                 actions=data['actions'], character_names=data['character_names'])
        projects_storage[project_id].script_file = script_file
        app.logger.info(f'Сценарий загружен ${script_file}')
    return jsonify(
        {'message': 'Сценарий загружен'}), 200


@app.route('/matchPhrases', methods=['POST'])
def match_phrases_handler():
    data = request.json
    project_id = data['project_id']
    create_project_if_not_exists(project_id)
    files = data['files']
    for file in files:
        if 'subtitles' in file:
            file['subtitles'] = [Subtitle.from_dict(subtitle) for subtitle in file['subtitles']]
    result = match_phrases(files, projects_storage[project_id].script_file.phrases)
    converted_data = object_to_json(result)
    json_string = json.dumps(converted_data, ensure_ascii=False, indent=4)
    return json_string, 201


@app.route('/matchActions', methods=['POST'])
def match_actions_handler():
    data = request.json
    project_id = data['project_id']
    create_project_if_not_exists(project_id)
    files = data['files']
    script_file = projects_storage[project_id].script_file
    result = match_actions(files, script_file.actions, script_file.idf_corpus)
    converted_data = object_to_json(result)
    icecream.ic(converted_data)
    json_string = json.dumps(converted_data, ensure_ascii=False, indent=4)
    return json_string, 201


if __name__ == '__main__':
    app.run(debug=False)
