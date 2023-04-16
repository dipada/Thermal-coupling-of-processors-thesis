# python script to generate configuration json for rt-app

import json
import os

CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
RES_DIR = os.path.join(BASE_DIR, "resources/configuration/")

final_json = {
    "prova": {
        "nested": {
            "nested2": {
                "key2": "value2"
            },
        "nested3": {
            "key3": "value3"
            }
        }
    }
}



with open(f'{RES_DIR}/test.json', 'w') as outfile:
    json.dump(final_json, indent=4, fp=outfile)