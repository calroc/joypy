#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''


A dialect of Joy in Python.


Joy is a programming language created by Manfred von Thun that is easy to
use and understand and has many other nice properties.  This Python script
is an interpreter for a dialect of Joy that attempts to stay very close
to the spirit of Joy but does not precisely match the behaviour of the
original version(s) written in C.  A Tkinter GUI is provided as well.


    Copyright © 2014 Simon Forman

    This file is joy.py

    joy.py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    joy.py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with joy.py.  If not see <http://www.gnu.org/licenses/>.


'''
# We run in Python 2 and Python 3
from __future__ import print_function
try:
  input = raw_input
except NameError:
  pass


from sys import stderr, modules
from time import time
from inspect import getmembers, isbuiltin, getdoc, getsource
from traceback import print_exc
from functools import wraps
import os
import operator, math
import collections

from functions import is_function
from parser import text_to_expression

'''


§ joy()

The basic joy() function is quite straightforward.  It iterates through a
sequence of terms which are either literals (strings, numbers, sequences)
or functions.  Literals are put onto the stack and functions are
executed.

Every Joy function is an unary mapping from stacks to stacks.  Even
literals are considered to be functions that accept a stack and return a
new stack with the literal value on top.


'''



def joy(expression, stack):
  '''
  Evaluate the Joy expression on the stack.
  '''
  while expression:

    if TRACE:
      stack, expression = yield stack, expression

    term, expression = expression

    if is_function(term):
      stack = term(stack)
    else:
      stack = term, stack

  yield stack, expression


def run(text, stack):
  '''
  Return the stack resulting from running the Joy code text on the stack.
  '''
  expression = text_to_expression(text)
  return joy(expression, stack)


'''


Definitions
  functions as equations


'''


DEFINITIONS = '''


  rest == uncons popd ;
  first == uncons pop ;
  second == rest first ;
  third == rest rest first ;

  sum == 0 swap [+] step ;
  product == 1 swap [*] step ;

  swons == swap cons ;
  swoncat == swap concat ;
  shunt == [swons] step ;
  reverse == [] swap shunt ;
  flatten == [] swap [concat] step ;

  unit == [] cons ;
  quoted == [unit] dip ;
  unquoted == [i] dip ;

  enstacken == stack [clear] dip ;
  disenstacken == [truth] [uncons] while pop ;

  pam == [i] map ;
  run == [] swap infra ;
  size == [1] map sum ;
  size == 0 swap [pop ++] step ;

  average == [sum 1.0 *] [size] cleave / ;

  gcd == [0 >] [dup rollup modulus] while pop ;

  least_fraction == dup [gcd] infra [/] concat map ;


  divisor == popop 2 * ;
  minusb == pop neg ;
  radical == swap dup * rollup * 4 * - sqrt ;
  root1 == + swap / ;
  root2 == - swap / ;

  quadratic ==
    [[[divisor] [minusb] [radical]] pam] ternary i
    [[[root1] [root2]] pam] ternary ;


  *fraction ==
    [uncons] dip uncons
    [swap] dip concat
    [*] infra [*] dip cons ;

  *fraction0 == concat [[swap] dip * [*] dip] infra ;


  down_to_zero == [0 >] [dup --] while ;
  range_to_zero == unit [down_to_zero] infra ;

  times == [-- dip] cons [swap] infra [0 >] swap while pop ;


''' # End of DEFINITIONS


def partition_definition(d):
  name, proper, body_text = (n.strip() for n in d.partition('=='))
  if not proper and d:
    raise ValueError('Definition %r failed' % (d,))
  return name, body_text


def add_definition(d):
  '''
  Given the text of a definition such as "sum == 0 swap [+] step" add the
  parsed body expression to FUNCTIONS under that name.
  '''
  name, body_text = partition_definition(d)
  body = parse(tokenize(body_text))
  strbody = strstack(body) # Normalized body_text.
  _enter_message = '%s == %s' % (name, strbody)
  _exit_message = '%s done.' % name

  def f(stack):
    if TRACE: joy.add_message(_enter_message)
    try:
      return joy(body, stack)
    finally:
      if TRACE: joy.add_message(_exit_message)

  f.__name__ = name
  f.__doc__ = strbody
  f.__body__ = body
  return note(f)


'''


Initialize additional functions.

This is a bit of functionality to load up some additional names and
functions in the FUNCTIONS dict.  We grab some mathematical functions
from the math and operator modules, then we add in aliases and definitions.

It's a little rough around the edges but it works.


'''


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
  try: op(1)
  except: return False
  else: return True


def is_binary_math_op(op):
  try: op(1, 1)
  except: return False
  else: return True


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


'''


REPL (Read-Evaluate-Print Loop)


'''


def repl(stack=()):
  '''
  Read-Evaluate-Print Loop

  Accept input and run it on the stack, loop.
  '''
  try:
    print_words(None)
    while 'HALT' not in stack:

      print()
      print('->', strstack(stack))
      print()

      try:
        text = input('joy? ')
      except (EOFError, KeyboardInterrupt):
        break

      if TRACE: joy.reset()

      try:
        stack = run(text, stack)
      except:
        print_exc()

      if TRACE: joy.show_trace()

  except:
    print_exc()
  print()
  return stack


'''


--------------------------------------------------


Part III - The GUI

  See gui.py.


--------------------------------------------------


References


Wikipedia entry for Joy:
https://en.wikipedia.org/wiki/Joy_%28programming_language%29


Homepage at La Trobe University:
http://www.latrobe.edu.au/humanities/research/research-projects/past-projects/joy-programming-language


'''

