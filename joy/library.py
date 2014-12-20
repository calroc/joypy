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

from .joy import run
from .stack import list_to_stack, iter_stack
from .functions import note, FUNCTIONS


@note
def cons(S):
  '''
  The cons operator expects a list on top of the stack and the potential
  member below. The effect is to add the potential member into the
  aggregate.
  '''
  (tos, (second, stack)) = S
  return (second, tos), stack


@note
def uncons(S):
  '''
  Inverse of cons, removes an item from the top of the list on the stack
  and places it under the remaining list.
  '''
  (tos, stack) = S
  item, tos = tos
  return tos, (item, stack)


@note
def clear(stack):
  '''Clear everything from the stack.'''
  return ()


@note
def dup(S):
  '''Duplicate the top item on the stack.'''
  (tos, stack) = S
  return tos, (tos, stack)


@note
def swap(S):
  '''Swap the top two items on stack.'''
  (tos, (second, stack)) = S
  return second, (tos, stack)


@note
def stack_(stack):
  '''
  The stack operator pushes onto the stack a list containing all the
  elements of the stack.
  '''
  return stack, stack


@note
def unstack(S):
  '''
  The unstack operator expects a list on top of the stack and makes that
  the stack discarding the rest of the stack.
  '''
  (tos, stack) = S
  return tos


@note
def pop(S):
  '''Pop and discard the top item from the stack.'''
  (tos, stack) = S
  return stack


@note
def popd(S):
  '''Pop and discard the second item from the stack.'''
  (tos, (second, stack)) = S
  return tos, stack


@note
def popop(S):
  '''Pop and discard the first and second items from the stack.'''
  (tos, (second, stack)) = S
  return stack


@note
def dupd(S):
  '''Duplicate the second item on the stack.'''
  (tos, (second, stack)) = S
  return tos, (second, (second, stack))


@note
def reverse(S):
  '''Reverse the list on the top of the stack.'''
  (tos, stack) = S
  res = ()
  for term in iter_stack(tos):
    res = term, res
  return res, stack


@note
def concat(S):
  '''Concatinate the two lists on the top of the stack.'''
  (tos, (second, stack)) = S
  for term in reversed(list(iter_stack(second))):
    tos = term, tos
  return tos, stack


@note
def zip_(S):
  '''
  Replace the two lists on the top of the stack with a list of the pairs
  from each list.  The smallest list sets the length of the result list.
  '''
  (tos, (second, stack)) = S
  accumulator = [
    (a, (b, ()))
    for a, b in zip(iter_stack(tos), iter_stack(second))
    ]
  return list_to_stack(accumulator), stack


@note
def succ(S):
  '''Increment TOS.'''
  (tos, stack) = S
  return tos + 1, stack


@note
def pred(S):
  '''Decrement TOS.'''
  (tos, stack) = S
  return tos - 1, stack


@note
def rollup(S):
  '''a b c -> b c a'''
  (a, (b, (c, stack))) = S
  return b, (c, (a, stack))


@note
def rolldown(S):
  '''a b c -> c a b'''
  (a, (b, (c, stack))) = S
  return c, (a, (b, stack))


@note
def execute(S):
  (text, stack) = S
  if isinstance(text, str):
    return run(text, stack)
  return stack


@note
def id_(stack):
  return stack


##@note
##def first(((head, tail), stack)):
##  return head, stack


##@note
##def rest(((head, tail), stack)):
##  return tail, stack


##  flatten
##  transpose
##  sign
##  at
##  of
##  drop
##  take


@note
def print_words(stack):
  '''Print all the words in alphabetical order.'''
  print(' '.join(sorted(FUNCTIONS)))
  return stack


@note
def simple_manual(stack):
  '''
  Print words and help for each word.
  '''
  for name, f in sorted(FUNCTIONS.items()):
    d = getdoc(f)
    boxline = '+%s+' % ('-' * (len(name) + 2))
    print('\n'.join((
      boxline,
      '| %s |' % (name,),
      boxline,
      d if d else '   ...',
      '',
      '--' * 40,
      '',
      )))
  return stack


@note
def help_(S):
  '''Accepts a quoted word on the top of the stack and prints its docs.'''
  (quote, stack) = S
  word = quote[0]
  print(getdoc(word))
  return stack
