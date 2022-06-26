#!/usr/bin/env python3

import yaml
import csv

def read_conf():
    with open('../config.yaml', 'r') as yaml_file:
        contents = yaml.safe_load(yaml_file.read())
    return contents

def read_worklogs():
    with open('../worklogs/test-worklog.csv', mode='r') as csv_file:
        entries = []
        reader = csv.DictReader(csv_file)
        for row in reader:
            entries.append(row)
    return entries
