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

from typing import List, Optional, Dict

from scripts import VarDecl, Header


def generate_zero_decls(types: Optional[List[str]]) -> List[VarDecl]:
    decls = []
    for t in types:
        var_name = t.replace(' ', '_')
        var_name = var_name.replace('*', 'p')
        var_name = 'var_' + var_name

        decl = '{} {} = {{0}};'.format(t, var_name)
        decls.append(VarDecl(var_name, t, decl))
    return decls


def generate_test_file(headers: List[Header],
                       type_idx: Dict[str, VarDecl]) -> str:
    output = []

    for h in headers:
        output.append('#include <{}>'.format(h.name))

    output.append('void main(void) {')
    # To have stable output, traverse sorted keys
    sorted_var_names = sorted(type_idx.keys())
    for name in sorted_var_names:
        output.append('\t{}'.format(type_idx[name].decl))

    for h in headers:
        for f in h.funcs:
            line = '\t'
            if f.ret_type:
                line += '{} = '.format(type_idx[f.ret_type].name)
            line += '{}('.format(f.symbol)

            if f.args:
                for arg in f.args[:-1]:
                    line += '{},'.format(type_idx[arg].name)
                line += type_idx[f.args[-1]].name
            line += ');'
            output.append(line)
    output.append('}')
    return '\n'.join(output)
