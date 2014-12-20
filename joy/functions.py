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

§ Functions

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
from __future__ import print_function
from sys import stderr
from functools import wraps
from collections import Callable


FUNCTIONS = {}


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
#  ('', ['']),
  )


class FunctionWrapper(object):
  '''
  Allow functions to have a nice repr().
  '''

  def __init__(self, f):
    self.f = f
    self.name = f.__name__.rstrip('_')

  def __call__(self, stack):
    return self.f(stack)

  def __repr__(self):
    return self.name


def note(f):
  '''Decorator to enter functions into the function map.'''
  F = wraps(f)(FunctionWrapper(f))
  FUNCTIONS[F.name] = F
  return F


def convert(token):
  '''Look up symbols in the functions dict.'''
  try:
    return FUNCTIONS[token]
  except KeyError:
    print('unknown word', token, file=stderr)
    return token


def is_function(term):
  '''
  Return a Boolean value indicating whether or not a term is a function.
  '''
  # In Python the tuple type is callable so we have to check for that.
  # We could also just check isinstance(term, FunctionWrapper), but this
  # way we can use any old callable as a function if we like.
  return isinstance(term, Callable) and not isinstance(term, tuple)


# Helper functions tp auto-generate Joy functions from Python builtins.


def joyful_1_arg_op(f):
  '''
  Return a Joy function that pops the top argument from the stack and
  pushes f(tos) back.
  '''
# return wraps(f)(lambda ((tos, stack)): (f(tos), stack))
  return wraps(f)(lambda tos_stack: (f(tos_stack[0]), tos_stack[1]))


def joyful_2_arg_op(f):
  '''
  Return a Joy function that pops the top two arguments from the stack
  and pushes f(second, tos) back.
  '''
# return wraps(f)(lambda ((tos, (second, stack))): (f(second, tos), stack))
  return wraps(f)(lambda tos_second_stack: (f(tos_second_stack[1][0], tos_second_stack[0]), tos_second_stack[1][1]))


def is_unary_math_op(op):
  try:
    op(1)
  except:
    return False
  return True


def is_binary_math_op(op):
  try:
    op(1, 1)
  except:
    return False
  return True
