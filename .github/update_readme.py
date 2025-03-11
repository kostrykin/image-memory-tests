#!/usr/bin/env python

import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--readme', type=str, required=True)
parser.add_argument('--tests-output', type=str, required=True)
parser.add_argument('--benchmark-output', type=str, required=True)
args = parser.parse_args()

with open(args.readme) as f:
    readme = f.read()

with open(args.tests_output) as f:
    tests_output = f.read().strip()

lines = list()
skip = False

for line in readme.split('\n'):
    if line == '<!-- END OUTPUT -->':
        skip = False
    if not skip:
        lines.append(line)
    if line == '<!-- BEGIN TEST OUTPUT -->':
        skip = True
        lines.append('```')
        lines.append(tests_output)
        lines.append('```')
    if line == '<!-- BEGIN BENCHMARK OUTPUT -->':
        skip = True
        lines.append('```')
        lines.append(benchmark_output)
        lines.append('```')

with open(args.readme, 'w') as f:
    f.write('\n'.join(lines))
