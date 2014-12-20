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
from inspect import getdoc

from ..functions import FUNCTIONS
from ..stack import strstack
from ..joy import joy, run
from .. import tracer

from .misc import is_numerical


class World(object):

  def __init__(self, stack=(), text_widget=None):
    self.stack = stack
    self.text_widget = text_widget

  def do_lookup(self, name):
    word = FUNCTIONS[name]
    self.stack = word, self.stack
    self.print_stack()

  def do_opendoc(self, name):
    if is_numerical(name):
      print('The number', name)
    else:
      try:
        word = FUNCTIONS[name]
      except KeyError:
        print(repr(name), '???')
      else:
        print(getdoc(word))
    self.text_widget.see('end')

  def pop(self):
    if self.stack:
      self.stack = self.stack[1]
    self.print_stack()

  def push(self, it):
    it = it.encode('utf8')
    self.stack = it, self.stack
    self.print_stack()

  def peek(self):
    if self.stack:
      return self.stack[0]

  def interpret(self, command):
    if tracer.TRACE: joy.reset()
    self.stack = run(command, self.stack)
    self.print_stack()
    if tracer.TRACE: joy.show_trace()

  def has(self, name):
    return name in FUNCTIONS

  def save(self):
    pass

  def print_stack(self):
    stack_out_index = self.text_widget.search('<' 'STACK', 1.0)
    if stack_out_index:
      self.text_widget.see(stack_out_index)
      s = strstack(self.stack) + '\n'
      self.text_widget.insert(stack_out_index, s)
