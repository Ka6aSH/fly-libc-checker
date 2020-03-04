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


def parse_function_pointer(line: str) -> Optional[Type]:
    if line.count('(') != line.count(')'):
        logging.error('Unbalanced parentheses in: ' + line)
        return None
    fcp = line.index(')')
    la = line.rindex('*', 0, fcp)
    var_name = line[la + 1:fcp]
    type = line.replace(var_name, '')
    decl_format = line.replace(var_name, '{}')
    decl_func = lambda x: decl_format.format(x)
    return Type(type, decl_func)


def split_args(line: str) -> List[str]:
    begin = 0
    end = 0
    state = 0
    res = []
    for c in line:
        if c == ',' and state == 0 and end > begin:
            res.append(line[begin:end])
            begin = end + 1
        elif c == '(':
            state += 1
        elif c == ')':
            state -= 1

        end += 1
    if end > begin:
        res.append(line[begin:])
    return res


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
        if ret in config.ignored_types:
            logging.info('Ignoring the line due to ignored return type "{}":'
                         '\n\t{}'.format(ret, line))
            return None

        ret_type = Type(ret)
        for k, v in config.type_substitution.items():
            if k in ret_type.name:
                # TODO several spaces in the middle
                ret_type = Type(ret_type.name.replace(k, v).strip())

        parsed_function.ret_type = ret_type

    args = split_args(line[op + 1:cp])
    for idx, arg in enumerate(args):
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
            arg_type = parse_function_pointer(arg)
            if not arg_type:
                logging.warning('Ignoring function "{}": unrecognized argument '
                                'type:\n\t{}'.format(parsed_function.symbol,
                                                     line))
                return None
        else:
            an = arg.rindex(' ')
            while arg[an + 1] == '*':
                an += 1

            arg_type = Type(arg[:an + 1].strip())

        if config:
            if arg_type.name in config.ignored_types:
                logging.info('Ignoring the line due to ignored type "{}" of one'
                             ' of arguments:\n\t{}'.format(arg_type, line))
                return None

            for k, v in config.type_substitution.items():
                if k in arg_type.name:
                    # TODO several spaces in the middle
                    arg_type = Type(arg_type.name.replace(k, v).strip())

        parsed_function.args.append(arg_type)

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
