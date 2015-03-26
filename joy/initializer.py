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
'''


Initialize additional functions.

This is a bit of functionality to load up some additional names and
functions in the FUNCTIONS dict.  We grab some mathematical functions
from the math and operator modules, then we add in aliases and definitions.

It's a little rough around the edges but it works.


'''
import operator, math
from inspect import getmembers, isbuiltin
from .functions import (
  ALIASES,
  FUNCTIONS,
  is_unary_math_op,
  is_binary_math_op,
  joyful_1_arg_op,
  joyful_2_arg_op,
  note,
  )
from .definitions import DEFINITIONS, add_definition
from . import combinators as comb


combinators = {
  'app1': FunctionWrapper(comb.app1),
  'app2': FunctionWrapper(comb.app2),
  'app3': FunctionWrapper(comb.app3),
  'b': FunctionWrapper(comb.b),
  'binary': FunctionWrapper(comb.binary),
  'cleave': FunctionWrapper(comb.cleave),
  'dip': FunctionWrapper(comb.dip),
  'dipd': FunctionWrapper(comb.dipd),
  'dipdd': FunctionWrapper(comb.dipdd),
  'i': FunctionWrapper(comb.i),
  'ifte': FunctionWrapper(comb.ifte),
  'infra': FunctionWrapper(comb.infra),
  'map': FunctionWrapper(comb.map_),
  'nullary': FunctionWrapper(comb.nullary),
  'step': FunctionWrapper(comb.step),
  'ternary': FunctionWrapper(comb.ternary),
  'unary': FunctionWrapper(comb.unary),
  'while': FunctionWrapper(comb.while_),
  'x': FunctionWrapper(comb.x),
  })




_non = [] # TODO: look through these later and see about adding them..


def initialize(modules=(operator, math)):
  '''
  Initialize additional functions (from Python modules and DEFINITIONS)
  and enter ALIASES into FUNCTIONS.
  '''

  # Note that the operator module defines a bunch of "in-place" versions of
  # functions that all start with 'i' and that we don't want.
  # Fortunately, the math module only defines two functions that start with
  # 'i' and we don't want either of them either, so the exclusion of names
  # that start with 'i' below is okay for these two modules.  Eventually if
  # we pull Joy functions from more Python modules we should add something
  # to let us properly specify the names of the functions to wrap.

  # Add functions from Python modules.
  for module in modules:
    for name, function in getmembers(module, isbuiltin):
      if name.startswith('_') or name.startswith('i'): continue
      if is_unary_math_op(function): note(joyful_1_arg_op(function))
      elif is_binary_math_op(function): note(joyful_2_arg_op(function))
      else: _non.append(function)

  # Now that all the functions are in the dict, add the aliases.
  for name, aliases in ALIASES:
    for alias in aliases:
      FUNCTIONS[alias] = FUNCTIONS[name]

  # Parse and enter the definitions.
  for definition in DEFINITIONS.split(';'):
    add_definition(definition.strip())
