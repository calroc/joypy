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


§ Combinators

  functions that call joy()


'''
from .joy import joy
from .stack import list_to_stack, iter_stack


def map_(S):
  '''
  Run the quoted program on TOS on the items in the list under it, push a
  new list with the results (in place of the program and original list.
  '''
  (quote, (aggregate, stack)) = S
  results = list_to_stack([
    joy(quote, (term, stack))[0]
    for term in iter_stack(aggregate)
    ])
  return results, stack


def i(S):
  '''Execute the quoted program on TOS on the rest of the stack.'''
  (quote, stack) = S
  return joy(quote, stack)


def x(S):
  '''
  Like i but don't remove the program first.  In other words the
  program gets itself as its first arg.
  '''
  (quote, stack) = S
  return joy(quote, (quote, stack))


def infra(S):
  '''
  Accept a quoted program and a list on the stack and run the program
  with the list as its stack.
  '''
  (quote, (aggregate, stack)) = S
  return joy(quote, aggregate), stack


def b(S):
  '''
  Given two quoted programs on the stack run the second one then the one
  on TOS.
  '''
  (Q, (P, stack)) = S
  return joy(Q, joy(P, stack))


def cleave(S):
  '''
  The cleave combinator expects two quotations, and below that an item X.
  It first executes [P], with X on top, and saves the top result element.
  Then it executes [Q], again with X, and saves the top result.
  Finally it restores the stack to what it was below X and pushes the two
  results P(X) and Q(X).
  '''
  (Q, (P, (x, stack))) = S
  p = joy(P, (x, stack))[0]
  q = joy(Q, (x, stack))[0]
  return q, (p, stack)


def ifte(S):
  '''[if] [then] [else] ifte'''
  (else_, (then, (if_, stack))) = S
  if_res = joy(if_, stack)[0]
  if if_res:
    result = joy(then, stack)[0]
  else:
    result = joy(else_, stack)[0]
  return result, stack


def dip(S):
  '''
  dip expects a program [P] and below that another item X. It pops both,
  saves X, executes P and then restores X.
  '''
  (quote, (x, stack)) = S
  return x, joy(quote, stack)


def dipd(S):
  '''Like dip but expects two items.'''
  (quote, (x, (y, stack))) = S
  return x, (y, joy(quote, stack))


def dipdd(S):
  '''Like dip but expects three items.'''
  (quote, (x, (y, (z, stack)))) = S
  return x, (y, (z, joy(quote, stack)))


def app1(S):
  '''
  Given a quoted program on TOS and anything as the second stack item run
  the program and replace the two args with the first result of the
  program.
  '''
  (quote, (x, stack)) = S
  result = joy(quote, (x, stack))
  return result[0], stack


def app2(S):
  '''Like app1 with two items.'''
  (quote, (x, (y, stack))) = S
  resultx = joy(quote, (x, stack))[0]
  resulty = joy(quote, (y, stack))[0]
  return resultx, (resulty, stack)


def app3(S):
  '''Like app1 with three items.'''
  (quote, (x, (y, (z, stack)))) = S
  resultx = joy(quote, (x, stack))[0]
  resulty = joy(quote, (y, stack))[0]
  resultz = joy(quote, (z, stack))[0]
  return resultx, (resulty, (resultz, stack))


def step(S):
  '''
  The step combinator removes the aggregate and the quotation, and then
  repeatedly puts the members of the aggregate on top of the remaining
  stack and executes the quotation.
  '''
  (quote, (aggregate, stack)) = S
  for term in iter_stack(aggregate):
    stack = joy(quote, (term, stack))
  return stack


def while_(S):
  '''[if] [body] while'''
  (body, (if_, stack)) = S
  while joy(if_, stack)[0]:
    stack = joy(body, stack)
  return stack


def nullary(S):
  '''
  Run the program on TOS and return its first result without consuming
  any of the stack (except the program on TOS.)
  '''
  (quote, stack) = S
  result = joy(quote, stack)
  return result[0], stack


def unary(S):
  (quote, stack) = S
  _, return_stack = stack
  result = joy(quote, stack)
  return result[0], return_stack


def binary(S):
  (quote, stack) = S
  _, (_, return_stack) = stack
  result = joy(quote, stack)
  return result[0], return_stack


def ternary(S):
  (quote, stack) = S
  _, (_, (_, return_stack)) = stack
  result = joy(quote, stack)
  return result[0], return_stack
