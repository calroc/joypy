# -*- coding: utf-8 -*-
#
#    Copyright © 2014, 2015 Simon Forman
#
#    This file is part of Joypy.
#
#    Joypy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Joypy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Joypy.  If not see <http://www.gnu.org/licenses/>.
#
import operator, math
from .btree import fill_tree, items
from .functions import (
  add_aliases,
  generate_definitions,
  BinaryBuiltinWrapper,
  FunctionWrapper,
  SimpleFunctionWrapper,
  UnaryBuiltinWrapper,
  )
from . import combinators as comb
from . import library as lib


builtins = (
  BinaryBuiltinWrapper(operator.add),
  BinaryBuiltinWrapper(operator.and_),
  BinaryBuiltinWrapper(operator.div),
  BinaryBuiltinWrapper(operator.eq),
  BinaryBuiltinWrapper(operator.floordiv),
  BinaryBuiltinWrapper(operator.ge),
  BinaryBuiltinWrapper(operator.gt),
  BinaryBuiltinWrapper(operator.le),
  BinaryBuiltinWrapper(operator.lshift),
  BinaryBuiltinWrapper(operator.lt),
  BinaryBuiltinWrapper(operator.mod),
  BinaryBuiltinWrapper(operator.mul),
  BinaryBuiltinWrapper(operator.ne),
  BinaryBuiltinWrapper(operator.or_),
  BinaryBuiltinWrapper(operator.pow),
  BinaryBuiltinWrapper(operator.rshift),
  BinaryBuiltinWrapper(operator.sub),
  BinaryBuiltinWrapper(operator.truediv),
  BinaryBuiltinWrapper(operator.xor),

  UnaryBuiltinWrapper(operator.neg),
  UnaryBuiltinWrapper(operator.not_),
  UnaryBuiltinWrapper(math.sqrt),
  )


combinators = (
  FunctionWrapper(comb.app1),
  FunctionWrapper(comb.app2),
  FunctionWrapper(comb.app3),
  FunctionWrapper(comb.b),
  FunctionWrapper(comb.binary),
  FunctionWrapper(comb.cleave),
  FunctionWrapper(comb.dip),
  FunctionWrapper(comb.dipd),
  FunctionWrapper(comb.dipdd),
  FunctionWrapper(comb.i),
  FunctionWrapper(comb.ifte),
  FunctionWrapper(comb.infra),
  FunctionWrapper(comb.map_),
  FunctionWrapper(comb.nullary),
  FunctionWrapper(comb.step),
  FunctionWrapper(comb.swaack),
  FunctionWrapper(comb.ternary),
  FunctionWrapper(comb.unary),
  FunctionWrapper(comb.while_),
  FunctionWrapper(comb.x),
  FunctionWrapper(lib.print_words),
  )


primitives = (
  SimpleFunctionWrapper(lib.first),
  SimpleFunctionWrapper(lib.truthy),
  SimpleFunctionWrapper(lib.getitem),
  SimpleFunctionWrapper(lib.unstack),
  SimpleFunctionWrapper(lib.clear),
  SimpleFunctionWrapper(lib.concat),
  SimpleFunctionWrapper(lib.cons),
  SimpleFunctionWrapper(lib.dup),
  SimpleFunctionWrapper(lib.dupd),
  SimpleFunctionWrapper(lib.id_),
  SimpleFunctionWrapper(lib.min_),
  SimpleFunctionWrapper(lib.pop),
  SimpleFunctionWrapper(lib.popd),
  SimpleFunctionWrapper(lib.popop),
  SimpleFunctionWrapper(lib.pred),
  SimpleFunctionWrapper(lib.remove),
  SimpleFunctionWrapper(lib.reverse),
  SimpleFunctionWrapper(lib.rolldown),
  SimpleFunctionWrapper(lib.rollup),
  SimpleFunctionWrapper(lib.stack_),
  SimpleFunctionWrapper(lib.succ),
  SimpleFunctionWrapper(lib.sum_),
  SimpleFunctionWrapper(lib.swap),
  SimpleFunctionWrapper(lib.uncons),
  SimpleFunctionWrapper(lib.unstack),
  SimpleFunctionWrapper(lib.void),
  SimpleFunctionWrapper(lib.zip_),
  )


def initialize(dictionary=()):
  B = [(F.name, F) for F in builtins]
  C = [(F.name, F) for F in combinators]
  P = [(F.name, F) for F in primitives]
  D = add_aliases(B + C + P)
  dictionary = fill_tree(dictionary, D)
  dictionary = generate_definitions(lib.definitions, dictionary)
  # Re-balance the dictionary.
  dictionary = fill_tree((), items(dictionary))
  return dictionary
