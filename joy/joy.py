# -*- coding: utf-8 -*-
'''


A dialect of Joy in Python.


Joy is a programming language created by Manfred von Thun that is easy to
use and understand and has many other nice properties.  This Python script
is an interpreter for a dialect of Joy that attempts to stay very close
to the spirit of Joy but does not precisely match the behaviour of the
original version(s) written in C.  A Tkinter GUI is provided as well.


    Copyright © 2014 Simon Forman

    This file is part of Joypy.

    Joypy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Joypy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Joypy.  If not see <http://www.gnu.org/licenses/>.


§ joy()

The basic joy() function is quite straightforward.  It iterates through a
sequence of terms which are either literals (strings, numbers, sequences)
or functions.  Literals are put onto the stack and functions are
executed.

Every Joy function is an unary mapping from stacks to stacks.  Even
literals are considered to be functions that accept a stack and return a
new stack with the literal value on top.
'''
from __future__ import print_function
try:
  input = raw_input
except NameError:
  pass
from traceback import print_exc
from .parser import text_to_expression
from .stack import strstack, iter_stack, list_to_stack


def print_trace(stack, expression):
  stack = list(iter_stack(stack))
  stack.reverse()
  print(strstack(list_to_stack(stack)), '.', strstack(expression))


def joy(stack, expression, dictionary, viewer=print_trace):
  '''
  Evaluate the Joy expression on the stack.
  '''
  while expression:
    viewer(stack, expression)
    term, expression = expression
    if callable(term):
      stack, expression, dictionary = term(stack, expression, dictionary)
    else:
      stack = term, stack
  viewer(stack, expression)
  return stack, expression, dictionary


def run(text, stack, dictionary):
  '''
  Return the stack resulting from running the Joy code text on the stack.
  '''
  expression = text_to_expression(text, dictionary)
  return joy(stack, expression, dictionary)


def repl(stack=(), dictionary=()):
  '''
  Read-Evaluate-Print Loop

  Accept input and run it on the stack, loop.
  '''
  try:
    while True:
      print()
      print('->', strstack(stack))
      print()
      try:
        text = input('joy? ')
      except (EOFError, KeyboardInterrupt):
        break
      try:
        stack, _, dictionary = run(text, stack, dictionary)
      except:
        print_exc()
  except:
    print_exc()
  print()
  return stack
