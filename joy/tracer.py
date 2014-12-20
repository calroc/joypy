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


§ Tracing a Run.


Machinery for tracing the execution of an expression.

You can ignore this for now.  It's not central to the Joy language and
it more properly should appear lower down in this script, however it is
used as a decorator for the joy() function and therefore must be in scope
when that function is declared (immediately below.)
'''
# We run in Python 2 and Python 3
from __future__ import print_function

from .stack import strstack, iter_stack, list_to_stack
from .functions import note


TRACE = False


class Tracer(object):
  '''
  Wrap the joy() function in an object that keeps track of the execution
  trace of the interpreter.  This trace datastructure contains each stack
  and expression that the joy() function has run during the execution of
  some expression, and it can be useful for exploring and re-running.

  Note that the frame attribute is accumulating the actual stack and
  expression tuples not copies or records.  You can pass these to joy()
  to rerun that expression on that stack.
  '''

  def __init__(self, joy):
    self.joy = joy
    self.reset()

  def reset(self):
    self.frame = []
    self.framestack = [self.frame]

  def __call__(self, expression, stack):
    if TRACE: self._start_call()
    try:
      return self.cycle(self.joy(expression, stack))
    finally:
      if TRACE: self._end_call()

  def cycle(self, J, SE=None):
    while True:
      try:
        stack, expression = SE = J.send(SE)
        if TRACE: self.add_trace(stack, expression)
      except StopIteration:
        break
    return SE[0]

  def add_trace(self, stack, expression):
    self.frame.append((stack, expression))

  def add_message(self, message):
    self.frame.append(message)

  def _start_call(self):
    self.add_message('frame start')
    self.framestack.append(self.frame)
    self.frame = []
    self.framestack[-1].append(self.frame)

  def _end_call(self):
    self.frame = self.framestack.pop()
    self.add_message('frame end')

  def show_trace(self, f=None, indent=0):
    if f is None:
      f = self.frame
    for n in f:
      if isinstance(n, tuple):
        s, e = n
        print(' ' * indent, end=' ')
        self._print_trace(s, e)
      elif isinstance(n, str):
        print('#', '.' * indent, n)
      else:
        self.show_trace(n, indent + 2)

  @staticmethod
  def _print_trace(stack, expression):
    stack = list(iter_stack(stack))
    stack.reverse()
    print(strstack(list_to_stack(stack)), '•', strstack(expression))


@note
def TRACE_(stack):
  '''
  Toggle print-out of execution trace.
  '''
  global TRACE
  TRACE = not TRACE
  return stack
