# -*- coding: utf-8 -*-
#
#    Copyright © 2014, 2015 Simon Forman
#
#    This file is part of joy.py
#
#    joy.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    joy.py is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with joy.py.  If not see <http://www.gnu.org/licenses/>.
#
'''

# Functions

  stack → stack
  note() decorator
  define several functions
  wrap functions from Python operator module


We can catagorize functions into those that rearrange things on the stack
but don't otherwise process them, those that perform some process on
them, and those that call back into the joy() function to execute one or
more quoted programs themselves.  And, of course, there are commands that
do more than one or all three.

Commands that execute quoted programs are called "Combinators" and
they are the key to Joy's expressiveness and power.  The joy()
function by itself wouldn't accomplish much but with the availability of
several combinators it becomes a powerhouse.

Commands that just rearrange things on the stack can be written in python
as simple tuple unpacking and repacking.

Definitions, functions defined by equations, refactoring and how
important it is..
'''
from .btree import get, insert
from .parser import text_to_expression
from .stack import list_to_stack, iter_stack
'''

## ALIASES

We allow for having alternate names for functions by this mapping.
'''
ALIASES = (
  ('add', ['+']),
  ('mul', ['*']),
  ('truediv', ['/']),
  ('mod', ['%', 'rem', 'remainder', 'modulus']),
  ('eq', ['=']),
  ('ge', ['>=']),
  ('gt', ['>']),
  ('le', ['<=']),
  ('lshift', ['<<']),
  ('lt', ['<']),
  ('ne', ['<>', '!=']),
  ('rshift', ['>>']),
  ('sub', ['-']),
  ('xor', ['^']),
  ('succ', ['++']),
  ('pred', ['--']),
  ('rolldown', ['roll<']),
  ('rollup', ['roll>']),
  ('id', ['•']),
  )


def add_aliases(items, A=ALIASES):
  D = dict(items)
  for name, aliases in A:
    try:
      F = D[name]
    except KeyError:
      continue
    for alias in aliases:
      D[alias] = F
  return D.items()


'''
## FunctionWrapper

Right now, this just allows functions to have a nice repr().
'''
class FunctionWrapper(object):
  def __init__(self, f):
    self.f = f
    self.name = f.__name__.rstrip('_')
    self.__doc__ = f.__doc__ or str(f)

  def __call__(self, stack, expression, dictionary):
    return self.f(stack, expression, dictionary)

  def __repr__(self):
    return self.name


class SimpleFunctionWrapper(FunctionWrapper):

  def __call__(self, stack, expression, dictionary):
    return self.f(stack), expression, dictionary


class BinaryBuiltinWrapper(FunctionWrapper):

  def __call__(self, stack, expression, dictionary):
    (a, (b, stack)) = stack
    result = self.f(b, a)
    return (result, stack), expression, dictionary


class UnaryBuiltinWrapper(FunctionWrapper):

  def __call__(self, stack, expression, dictionary):
    (a, stack) = stack
    result = self.f(a)
    return (result, stack), expression, dictionary


class DefinitionWrapper(FunctionWrapper):

  def __init__(self, name, body_text, dictionary, doc=None):
    self.name = self.__name__ = name
    self.body = text_to_expression(body_text, dictionary)
    self._body = tuple(iter_stack(self.body))
    self.__doc__ = doc or body_text

  def __call__(self, stack, expression, dictionary):
    expression = list_to_stack(self._body, expression)
    return stack, expression, dictionary

  '''
  Given some text describing a Joy function definition parse it and
  return a DefinitionWrapper.
  '''
  @classmethod
  def parse_definition(class_, defi, dictionary):
    name, proper, body_text = (n.strip() for n in defi.partition('=='))
    if not proper:
      raise ValueError('Definition %r failed' % (defi,))
    return class_(name, body_text, dictionary)

'''
## generate_definitions()
'''
def generate_definitions(defs, dictionary):
  for definition in defs.splitlines():
    definition = definition.strip()
    if not definition or definition.isspace():
      continue
    F = DefinitionWrapper.parse_definition(definition, dictionary)
    dictionary = insert(dictionary, F.name, F)
  return dictionary
