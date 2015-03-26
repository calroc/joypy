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


'''
from .joy import joy
from .btree import get
from .stack import list_to_stack, iter_stack


def i(stack, expression, dictionary):
  (quote, stack) = stack
  accumulator = list(iter_stack(quote))
  expression = list_to_stack(accumulator, expression)
  return stack, expression, dictionary


def x(stack, expression, dictionary):
  '''
  x == dup i

  ... [Q] x = ... [Q] dup i
  ... [Q] x = ... [Q] [Q] i
  ... [Q] x = ... [Q]  Q

  '''
  quote = stack[0]
  accumulator = list(iter_stack(quote))
  expression = list_to_stack(accumulator, expression)
  return stack, expression, dictionary


def b(stack, expression, dictionary):
  i = get(dictionary, 'i')
  (q, (p, (stack))) = stack
  expression = (p, (i, (q, (i, expression))))
  return stack, expression, dictionary


def infra(stack, expression, dictionary):
  '''
  Accept a quoted program and a list on the stack and run the program
  with the list as its stack.
  '''
  i = get(dictionary, 'i')
  swaack = get(dictionary, 'swaack')
  (quote, (aggregate, stack)) = stack
  Q = (i, (stack, (swaack, expression)))
  return (quote, aggregate), Q, dictionary


def swaack(stack, expression, dictionary):
  old_stack, stack = stack
  stack = stack, old_stack
  return stack, expression, dictionary


def map_(S, expression, dictionary):
  '''
  Run the quoted program on TOS on the items in the list under it, push a
  new list with the results (in place of the program and original list.
  '''
  (quote, (aggregate, stack)) = S
  results = list_to_stack([
    joy((term, stack), quote, dictionary)[0][0]
    for term in iter_stack(aggregate)
    ])
  return (results, stack), expression, dictionary


##def i(S):
##  '''Execute the quoted program on TOS on the rest of the stack.'''
##  (quote, stack) = S
##  return joy(quote, stack)


##def x(S):
##  '''
##  Like i but don't remove the program first.  In other words the
##  program gets itself as its first arg.
##  '''
##  (quote, stack) = S
##  return joy(quote, (quote, stack))


##def infra(S):
##  '''
##  Accept a quoted program and a list on the stack and run the program
##  with the list as its stack.
##  '''
##  (quote, (aggregate, stack)) = S
##  return joy(quote, aggregate), stack


##def b(S):
##  '''
##  Given two quoted programs on the stack run the second one then the one
##  on TOS.
##  '''
##  (Q, (P, stack)) = S
##  return joy(Q, joy(P, stack))


def cleave(S, expression, dictionary):
  '''
  The cleave combinator expects two quotations, and below that an item X.
  It first executes [P], with X on top, and saves the top result element.
  Then it executes [Q], again with X, and saves the top result.
  Finally it restores the stack to what it was below X and pushes the two
  results P(X) and Q(X).
  '''
  (Q, (P, (x, stack))) = S
  p = joy((x, stack), P, dictionary)[0][0]
  q = joy((x, stack), Q, dictionary)[0][0]
  return (q, (p, stack)), expression, dictionary


def ifte(stack, expression, dictionary):
  i = get(dictionary, 'i')
  infra = get(dictionary, 'infra')
  first = get(dictionary, 'first')
  truthy = get(dictionary, 'truthy')
  getitem = get(dictionary, 'getitem')
  unstack = get(dictionary, 'unstack')
  (else_, (then, (if_, stack))) = stack
  ii = (( (stack, (else_, (infra, ()))) , (
      (stack, (then,  (infra, ()))) , ())), ())
  stack = (if_, (stack, ii))
  expression = (infra, (first, (truthy, (getitem, (i, (unstack, ()))))))
  return stack, expression, dictionary


##def ifte(S):
##  '''[if] [then] [else] ifte'''
##  (else_, (then, (if_, stack))) = S
##  if_res = joy(if_, stack)[0]
##  if if_res:
##    result = joy(then, stack)[0]
##  else:
##    result = joy(else_, stack)[0]
##  return result, stack


def dip(stack, expression, dictionary):
  i = get(dictionary, 'i')
  x = get(dictionary, 'x')
  (quote, (x, stack)) = stack
  expression = i, (x, expression)
  return (quote, stack), expression, dictionary


##def dip(S):
##  '''
##  dip expects a program [P] and below that another item X. It pops both,
##  saves X, executes P and then restores X.
##  '''
##  (quote, (x, stack)) = S
##  return x, joy(quote, stack)


def dipd(S, expression, dictionary):
  '''Like dip but expects two items.'''
  (quote, (x, (y, stack))) = S
  stack = joy(stack, quote, dictionary)[0]
  return (x, (y, stack)), expression, dictionary


def dipdd(S, expression, dictionary):
  '''Like dip but expects three items.'''
  (quote, (x, (y, (z, stack)))) = S
  stack = joy(stack, quote, dictionary)[0]
  return (x, (y, (z, stack))), expression, dictionary


def app1(S, expression, dictionary):
  '''
  Given a quoted program on TOS and anything as the second stack item run
  the program and replace the two args with the first result of the
  program.
  '''
  (quote, (x, stack)) = S
  result = joy((x, stack), quote, dictionary)[0]
  return (result[0], stack), expression, dictionary


def app2(S, expression, dictionary):
  '''Like app1 with two items.'''
  (quote, (x, (y, stack))) = S
  resultx = joy((x, stack), quote, dictionary)[0][0]
  resulty = joy((y, stack), quote, dictionary)[0][0]
  return (resultx, (resulty, stack)), expression, dictionary


def app3(S, expression, dictionary):
  '''Like app1 with three items.'''
  (quote, (x, (y, (z, stack)))) = S
  resultx = joy((x, stack), quote, dictionary)[0][0]
  resulty = joy((y, stack), quote, dictionary)[0][0]
  resultz = joy((z, stack), quote, dictionary)[0][0]
  return (resultx, (resulty, (resultz, stack))), expression, dictionary


def step(S, expression, dictionary):
  '''
  The step combinator removes the aggregate and the quotation, and then
  repeatedly puts the members of the aggregate on top of the remaining
  stack and executes the quotation.
  '''
  (quote, (aggregate, stack)) = S
  for term in iter_stack(aggregate):
    stack = joy((term, stack), quote, dictionary)[0]
  return stack, expression, dictionary


def while_(S, expression, dictionary):
  '''[if] [body] while'''
  (body, (if_, stack)) = S
  while joy(stack, if_, dictionary)[0][0]:
    stack = joy(stack, body, dictionary)[0]
  return stack, expression, dictionary


def nullary(S, expression, dictionary):
  '''
  Run the program on TOS and return its first result without consuming
  any of the stack (except the program on TOS.)
  '''
  (quote, stack) = S
  result = joy(stack, quote, dictionary)
  return (result[0][0], stack), expression, dictionary


def unary(S, expression, dictionary):
  (quote, stack) = S
  _, return_stack = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary


def binary(S, expression, dictionary):
  (quote, stack) = S
  _, (_, return_stack) = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary


def ternary(S, expression, dictionary):
  (quote, stack) = S
  _, (_, (_, return_stack)) = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary
