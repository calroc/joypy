# -*- coding: utf-8 -*-
#
#    Copyright © 2016 Simon Forman
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
Pretty printing support.

This is what does the formatting, e.g.:

           . 23 18 mul 99 add
        23 . 18 mul 99 add
     23 18 . mul 99 add
       414 . 99 add
    414 99 . add
       513 . 

'''
# (Kinda clunky and hacky.  This should be swapped out in favor of much
# smarter stuff.)
from __future__ import print_function
from traceback import print_exc
from .stack import stack_to_string, iter_stack, list_to_stack


class TracePrinter(object):

  def __init__(self):
    self.history = []

  def viewer(self, stack, expression):
    '''Pass this method as the viewer to joy() function.'''
    self.history.append((stack, expression))

  def __str__(self):
    return '\n'.join(self.go())

  def go(self):
    max_stack_length = 0
    lines = []
    for stack, expression in self.history:
      stack, expression = self.strings_of_trace(stack, expression)
      n = len(stack)
      if n > max_stack_length:
        max_stack_length = n
      lines.append((n, '%s . %s' % (stack, expression)))
    return [
      (' ' * (max_stack_length - n) + line) # Prefix spaces to line up '.'s.
      for n, line in lines
      ]

  @staticmethod
  def strings_of_trace(stack, expression):
    el = list(iter_stack(stack))
    el.reverse()
    return (
      stack_to_string(list_to_stack(el)),
      stack_to_string(expression)
      )

  def print_(self):
    try:
      print(self)
    except:
      print_exc()
      print('Exception while printing viewer.')
