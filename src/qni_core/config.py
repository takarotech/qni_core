import json
import pathlib


CONF_FILE_PATH = str(pathlib.Path.home() / 'qni_conf.json')


def add_globals(d):
	globals().update({k.upper(): v for k, v in d.items()})


json_conf = None
with open(CONF_FILE_PATH) as f:
    json_conf = json.load(f)

HW_VERSION = json_conf.pop('hw_version')
hw_value = json_conf.pop('hw_table_values')[HW_VERSION]
hw_table_keys = json_conf.pop('hw_table_keys')

add_globals({k: hw_value[i] for i, k in enumerate(hw_table_keys)})
add_globals(json_conf)

del f, add_globals, json_conf, hw_value, hw_table_keys, json, pathlib
