#!/usr/bin/python3

# Copyright 2019 Evgeny A. Kudryashov.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys
from typing import Set, List

from scripts import Config, Header
from scripts.generators import generate_zero_decls, generate_test_file
from scripts.parser import parse


def collect_types(headers_list: List[Header]) -> Set[str]:
    acc = set()
    for header in headers_list:
        for func in header.funcs:
            if func.ret_type:
                acc.add(func.ret_type)
            for arg_type in func.args:
                acc.add(arg_type)
    return acc


if len(sys.argv) < 2:
    print('Usage: ./fly-gen.py standards/c99.std main.c')
    exit(0)

logging.basicConfig(level=logging.WARNING)

ignored_types = ['void']
ignored_funcs = ['va_arg', 'va_start']
conditional_funcs = ['longjmp', 'abort', 'exit', '_Exit']
# TODO expand into something more meaningful
type_subs = {'real-floating': 'float', 'scalar': 'int'}

config = Config(ignored_funcs, ignored_types, type_subs, conditional_funcs)

headers = parse(sys.argv[1], config)
all_types = collect_types(headers)
var_decls = generate_zero_decls(list(all_types))
type_idx = {v.type: v for v in var_decls}

with open(sys.argv[2], 'w') as f:
    f.write(generate_test_file(headers, type_idx, config))
