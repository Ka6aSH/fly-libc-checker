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


class Config:
    def __init__(self, ignored_functions: Optional[List[str]] = None,
                 ignored_types: Optional[List[str]] = None,
                 type_substitution: Optional[Dict[str, str]] = None,
                 conditioned_functions: Optional[List[str]] = None) -> None:
        self.ignored_functions = ignored_functions
        self.ignored_types = ignored_types
        self.type_substitution = type_substitution
        self.conditioned_functions = conditioned_functions


class Header:
    def __init__(self, name: str) -> None:
        self.name = name
        self.funcs = []


class Function:
    def __init__(self, orig: str, symbol: str) -> None:
        self.orig = orig
        self.symbol = symbol
        self.ret_type = None
        self.args = []


class VarDecl:
    def __init__(self, name: str, type: str, decl: str) -> None:
        self.name = name
        self.type = type
        self.decl = decl
