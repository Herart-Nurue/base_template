import zipfile
import json
import os
import shutil
from uuid import uuid4

def convert_json_to_sb3(json_path, base_sb3_path, output_sb3_path):
    temp_dir = "temp_sb3"

    with zipfile.ZipFile(base_sb3_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    with open(json_path, 'r') as f:
        test_data = json.load(f)['tests'][0]  

    project_json_path = os.path.join(temp_dir, "project.json")
    with open(project_json_path, 'r') as f:
        project = json.load(f)

    sprite = next(target for target in project['targets'] if not target['isStage'])

    stage_vars = project['targets'][0]['variables']
    var_ids = {v[0]: k for k, v in stage_vars.items() if v[0] in ['a', 'b', 'result']}

    block_ids = {name: str(uuid4()) for name in [
        'when_flag', 'set_a', 'set_b', 'set_result', 'if_check',
        'equals', 'say_pass', 'say_fail', 'operator_add']}

    blocks = {
        block_ids['when_flag']: {
            "opcode": "event_whenflagclicked",
            "next": block_ids['set_a'],
            "parent": None,
            "inputs": {},
            "fields": {},
            "shadow": False,
            "topLevel": True,
            "x": 100,
            "y": 100
        },
        block_ids['set_a']: {
            "opcode": "data_setvariableto",
            "next": block_ids['set_b'],
            "parent": block_ids['when_flag'],
            "inputs": {"VALUE": [1, [10, str(test_data['setup']['a'])]]},
            "fields": {"VARIABLE": ["a", var_ids['a']]},
            "shadow": False
        },
        block_ids['set_b']: {
            "opcode": "data_setvariableto",
            "next": block_ids['set_result'],
            "parent": block_ids['set_a'],
            "inputs": {"VALUE": [1, [10, str(test_data['setup']['b'])]]},
            "fields": {"VARIABLE": ["b", var_ids['b']]},
            "shadow": False
        },
        block_ids['set_result']: {
            "opcode": "data_setvariableto",
            "next": block_ids['if_check'],
            "parent": block_ids['set_b'],
            "inputs": {"VALUE": [3, block_ids['operator_add']]},
            "fields": {"VARIABLE": ["result", var_ids['result']]},
            "shadow": False
        },
        block_ids['operator_add']: {
            "opcode": "operator_add",
            "next": None,
            "parent": block_ids['set_result'],
            "inputs": {
                "NUM1": [1, [12, "a", var_ids['a']]],
                "NUM2": [1, [12, "b", var_ids['b']]]
            },
            "fields": {},
            "shadow": False
        },
        block_ids['if_check']: {
            "opcode": "control_if_else",
            "next": None,
            "parent": block_ids['set_result'],
            "inputs": {
                "CONDITION": [2, block_ids['equals']],
                "SUBSTACK": [2, block_ids['say_pass']],
                "SUBSTACK2": [2, block_ids['say_fail']]
            },
            "fields": {},
            "shadow": False
        },
        block_ids['equals']: {
            "opcode": "operator_equals",
            "next": None,
            "parent": block_ids['if_check'],
            "inputs": {
                "OPERAND1": [3, [12, "result", var_ids['result']]],
                "OPERAND2": [1, [10, str(test_data['expected']['result'])]]
            },
            "fields": {},
            "shadow": False
        },
        block_ids['say_pass']: {
            "opcode": "looks_say",
            "next": None,
            "parent": block_ids['if_check'],
            "inputs": {"MESSAGE": [1, [10, "Test Passed"]]},
            "fields": {},
            "shadow": False
        },
        block_ids['say_fail']: {
            "opcode": "looks_say",
            "next": None,
            "parent": block_ids['if_check'],
            "inputs": {"MESSAGE": [1, [10, "Test Failed"]]},
            "fields": {},
            "shadow": False
        }
    }

    sprite['blocks'] = blocks

    with open(project_json_path, 'w') as f:
        json.dump(project, f)

    shutil.make_archive(output_sb3_path.replace(".sb3", ""), 'zip', temp_dir)
    shutil.move(output_sb3_path.replace(".sb3", ".zip"), output_sb3_path)

    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    convert_json_to_sb3(
        json_path="test.json",
        base_sb3_path="base_template.sb3",
        output_sb3_path="test_generated.sb3"
    )
