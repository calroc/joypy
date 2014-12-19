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


§ joy()

The basic joy() function is quite straightforward.  It iterates through a
sequence of terms which are either literals (strings, numbers, sequences)
or functions.  Literals are put onto the stack and functions are
executed.

Every Joy function is an unary mapping from stacks to stacks.  Even
literals are considered to be functions that accept a stack and return a
new stack with the literal value on top.
'''
from functions import is_function
from parser import text_to_expression
import tracer


@tracer.Tracer
def joy(expression, stack):
  '''
  Evaluate the Joy expression on the stack.
  '''
  while expression:

    if tracer.TRACE:
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
