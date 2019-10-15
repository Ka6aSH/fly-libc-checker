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
from typing import Optional, List

from scripts import Header, Function, Config, Type


def parse_header(line: str, config: Optional[Config] = None) -> Header:
    return Header(line[line.index('<') + 1:line.index('>')])


def parse_function(line: str,
                   config: Optional[Config] = None) -> Optional[Function]:
    op = line.find('(')
    cp = line.rfind(')')
    last_space = line.rfind(' ', 0, op)
    if op < 0 or cp < 0 or last_space < 0:
        logging.info('Ignoring line due to absence of parentheses and spaces:\n'
                     '\t{}'.format(line))
        return None

    add = 1 if line[last_space + 1] == '*' else 0
    func = line[last_space + 1 + add:op]

    if config and func in config.ignored_functions:
        logging.info('Ignoring the function "{}" at:\n\t{}'.format(func, line))
        return None
    elif not func:
        logging.warning('Ignoring the function due to unrecognized name at:\n'
                        '\t{}'.format(line))
        return None

    parsed_function = Function(line, func)

    ret = line[:last_space + 1 + add].strip()
    if ret != 'void':
        parsed_function.ret_type = Type(ret)

    args = line[op + 1:cp].split(',')
    for idx, arg in enumerate(args):
        arg = arg.replace(' restrict', '')
        arg = arg.strip()
        if arg == '...':
            if idx != len(args) - 1:
                logging.warning('Ellipsis argument is not the last. '
                                'Probably an error at line:\n\t{}'.format(line))
            continue
        if arg == 'void':
            if idx != 0 or len(args) != 1:
                logging.warning('void argument is not the only and last. '
                                'Probably an error at line:\n\t{}'.format(line))
                return None
            continue
        if '(' in arg or ')' in arg:
            logging.warning('Ignoring function "{}": unsupported function '
                            'pointer argument at line:\n\t{}'
                            .format(parsed_function.symbol, line))
            return None

        an = arg.rindex(' ')
        while arg[an + 1] == '*':
            an += 1

        arg_type = arg[:an + 1].strip()
        if config:
            if arg_type in config.type_substitution:
                arg_type = config.type_substitution[arg_type]
            if arg_type in config.ignored_types:
                logging.info('Ignoring the line due to ignored type "{}" of one'
                             ' of arguments:\n\t{}'.format(arg_type, line))
                return None

        parsed_function.args.append(Type(arg_type))

    return parsed_function


def parse(filename: str, config: Optional[Config] = None) -> List[Header]:
    headers = []
    header = None
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith('<'):
                header = parse_header(line, config)
                headers.append(header)
            elif line.endswith(';'):
                func = parse_function(line, config)
                if func:
                    header.funcs.append(func)
            elif not line or line.startswith('#'):
                continue
            else:
                logging.info('Ignored line:\n\t{}'.format(line))
    return headers
