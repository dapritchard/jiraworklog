#!/usr/bin/env python3

import argparse

# https://docs.python.org/3/howto/argparse.html
# https://docs.python.org/3/library/argparse.html
# https://stackoverflow.com/a/18161115
parser = argparse.ArgumentParser()
parser.add_argument('file')
parser.add_argument('--config-path')
