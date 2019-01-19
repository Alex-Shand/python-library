#!/usr/bin/env python3

from pathlib import Path
from argparse import ArgumentParser

parser = ArgumentParser(description='Remove uses of @export in a module and add'
                        ' the appropriate __all__ list')
parser.add_argument('module')
parser.add_argument('-o', '--output', help='Output file, defaults to <module>')
args = parser.parse_args()

module = Path(args.module)
all_list = __import__(module.stem).__all__

with open(module) as file:
    lines = [line for line in file.read().splitlines() if line.strip() != '@export']

lines.append('')
lines.append(f'__all__ = {all_list}')

if args.out:
    outfile = args.out
else:
    outfile = args.module

with open(outfile, 'w') as file:
    file.write('\n'.join(lines))
