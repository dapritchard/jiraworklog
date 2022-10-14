#!/usr/bin/env python3

import argparse

# https://docs.python.org/3/howto/argparse.html
# https://docs.python.org/3/library/argparse.html
# https://stackoverflow.com/a/18161115
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-a', '--auto-confirm', action='store_true')
parser.add_argument('-c', '--config-path')
parser.add_argument('-d', '--dry-run', action='store_true')
parser.add_argument('-i', '--init-config', action='store_true')
parser.add_argument('-v', '--verbose', type=int, default=1)
