#!/usr/bin/env python3

import os.path
import yaml

def read_conf():
    with open(os.path.expanduser('~/.jwconfig.yaml'), 'r') as yaml_file:
        contents = yaml.safe_load(yaml_file.read())
    return contents
