#!/usr/bin/env python

import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--readme', type=str, required=True)
parser.add_argument('--tests-output', type=str, required=True)
args = parser.parse_args()

with open(args.readme) as f:
    readme = f.read()

with open(args.tests_output) as f:
    tests_output = f.read().strip()

lines = list()
skip = False

for line in readme.split('\n'):
    if line == '<!-- END TEST OUTPUT -->':
        skip = False
    if not skip:
        lines.append(line)
    if line == '<!-- BEGIN TEST OUTPUT -->':
        skip = True
        lines.append(tests_output)

with open(args.readme, 'w') as f:
    f.write('\n'.join(lines))
