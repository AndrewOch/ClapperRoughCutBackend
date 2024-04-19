import json
from multiprocessing import freeze_support

from flask import Flask, request, jsonify
from icecream import icecream

from core.json_encoder import object_to_json
from core.phrases_matcher import match_phrases
from project.project import projects_storage, RoughCutProject
from project.script_file import ScriptFile
from project.subtitle import Subtitle

app = Flask(__name__)


def create_project_if_not_exists(id):
    if id not in projects_storage:
        projects_storage[id] = RoughCutProject()


@app.route('/script', methods=['POST'])
def upload_script():
    data = request.json
    project_id = data['project_id']
    create_project_if_not_exists(project_id)
    if projects_storage[project_id].script_file is not None:
        script_file = projects_storage[project_id].script_file
        script_file.update(script_id=data['script_id'], file_path=data['file_path'], phrases=data['phrases'],
                           actions=data['actions'])
        app.logger.info(f'Сценарий обновлён ${script_file}')
    else:
        script_file = ScriptFile(script_id=data['script_id'], file_path=data['file_path'], phrases=data['phrases'],
                                 actions=data['actions'])
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
    for file in files:
        if 'subtitles' in file:
            file['subtitles'] = [Subtitle.from_dict(subtitle) for subtitle in file['subtitles']]
    result = match_actions(files, projects_storage[project_id].script_file.actions)
    converted_data = object_to_json(result)
    json_string = json.dumps(converted_data, ensure_ascii=False, indent=4)
    return json_string, 201


@app.route('/sync', methods=['POST'])
def sync_files():
    data = request.json
    project_id = data['project_id']
    create_project_if_not_exists(project_id)
    # TODO
    return jsonify({'message': 'Файлы синхронизированы'}), 200


if __name__ == '__main__':
    app.run(debug=False)
