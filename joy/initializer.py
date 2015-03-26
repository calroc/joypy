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
from .btree import fill_tree
from .functions import FunctionWrapper, SimpleFunctionWrapper
from . import combinators as comb
from . import library as lib


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
  )


primitives = (
  SimpleFunctionWrapper(lib.first),
  SimpleFunctionWrapper(lib.truthy),
  SimpleFunctionWrapper(lib.getitem),
  SimpleFunctionWrapper(lib.unstack),
  )


def initialize(dictionary=()):
  C = [(F.name, F) for F in combinators]
  P = [(F.name, F) for F in primitives]
  dictionary = fill_tree(dictionary, C + P)
  return dictionary
