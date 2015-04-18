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

TODO: Brief description of combinators (as contrasted with "normal" functions.)

Note: the combinators that have calls to joy() in them haven't been
rewritten to be in Continuation-Passing Style yet.
'''
from .joy import joy
from .btree import get
from .stack import list_to_stack, iter_stack

'''
## i

The most straightforward combinator is called "i".  It just executes the
quoted program on the stack.

In the Continuation-Passing Style (CSP) it works by transferring the
terms from the quoted list on TOS into the pending expression before
returning back to the main joy() loop.
'''
def i(stack, expression, dictionary):
  (quote, stack) = stack
  accumulator = list(iter_stack(quote))
  expression = list_to_stack(accumulator, expression)
  return stack, expression, dictionary


'''
## x

Given a quoted program on the stack, the "x" combinator duplicates it and
then runs it.

    ... [Q] x = ... [Q] Q

It could be defined like so:

    x == dup i

    ... [Q] x = ... [Q] dup i
    ... [Q] x = ... [Q] [Q] i
    ... [Q] x = ... [Q]  Q

But rather than implement "x" as a definition, we write a Python function
that is almost exactly like the "i" combinator.
'''
def x(stack, expression, dictionary):
  i = get(dictionary, 'i')
  quote = stack[0]
  expression = (i, (quote, expression))
  return stack, expression, dictionary


'''
## b

The "b" combinator...

    ... [P] [Q] b = ... P Q

This combinator is slightly more involved than the "x" combinator, so
we look up the current "i" combinator and use it to make things simpler.
The "i" combinator is interleaved with the [P] and [Q] quoted programs:

    b == [i] dip i

    ... [P] [Q] b = ... [P] [Q] [i] dip i
    ... [P] [Q] b = ... [P] i [Q] i
    ... [P] [Q] b = ... P [Q] i
    ... [P] [Q] b = ... P Q

The implementation is straightforward:
'''
def b(stack, expression, dictionary):
  i = get(dictionary, 'i')
  (q, (p, (stack))) = stack
  expression = (p, (i, (q, (i, expression))))
  return stack, expression, dictionary


'''
## infra

Accept a quoted program and a list on the stack and run the program
with the list as its stack.
'''
def infra(stack, expression, dictionary):
  i = get(dictionary, 'i')
  swaack = get(dictionary, 'swaack')
  (quote, (aggregate, stack)) = stack
  Q = (i, (stack, (swaack, expression)))
  return (quote, aggregate), Q, dictionary


'''
## swaack

The name comes from "SWAp stACK".  I am considering dropping the extra a.

This is a weird combinator that takes a quoted literal and swaps the
existing stack contents with the contents of the quoted literal:

    c b a [x y z] swaack = z y x [a b c]

It is very useful (you can write a function much like call/cc with it for
example.)

The Python implementation is delightful:
'''
def swaack(stack, expression, dictionary):
  old_stack, stack = stack
  stack = stack, old_stack
  return stack, expression, dictionary


'''
## map

Run the quoted program on TOS on the items in the list under it, push a
new list with the results (in place of the program and original list.
'''
def map_(S, expression, dictionary):
  (quote, (aggregate, stack)) = S
  results = list_to_stack([
    joy((term, stack), quote, dictionary)[0][0]
    for term in iter_stack(aggregate)
    ])
  return (results, stack), expression, dictionary


'''
## cleave
 
The cleave combinator expects two quotations, and below that an item X.
It first executes [P], with X on top, and saves the top result element.
Then it executes [Q], again with X, and saves the top result.
Finally it restores the stack to what it was below X and pushes the two
results P(X) and Q(X).
'''
def cleave(S, expression, dictionary):
  (Q, (P, (x, stack))) = S
  p = joy((x, stack), P, dictionary)[0][0]
  q = joy((x, stack), Q, dictionary)[0][0]
  return (q, (p, stack)), expression, dictionary


'''
## ifte

    [if] [then] [else] ifte

    ... [if] [then] [else] . ifte

    [
      [[...] [else] infra]
      [[...] [then] infra]
    ]
    [...] [if] infra
    first truthy getitem
    i
    unstack

'''
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


'''
## dip
 
The dip combinator expects a program [P] and below that another item X. It pops both,
saves X, executes P and then restores X.
'''
def dip(stack, expression, dictionary):
  i = get(dictionary, 'i')
  (quote, (x, stack)) = stack
  stack = (quote, stack)
  expression = i, (x, expression)
  return stack, expression, dictionary


'''
## dipd
 
Like dip but expects two items.
'''
def dipd(S, expression, dictionary):
  '''Like dip but expects two items.'''
  (quote, (x, (y, stack))) = S
  stack = joy(stack, quote, dictionary)[0]
  return (x, (y, stack)), expression, dictionary


'''
## dipdd

Like dip but expects three items.
'''
def dipdd(S, expression, dictionary):
  '''Like dip but expects three items.'''
  (quote, (x, (y, (z, stack)))) = S
  stack = joy(stack, quote, dictionary)[0]
  return (x, (y, (z, stack))), expression, dictionary


'''
## app1

Given a quoted program on TOS and anything as the second stack item run
the program and replace the two args with the first result of the
program.
'''
def app1(S, expression, dictionary):
  '''
  Given a quoted program on TOS and anything as the second stack item run
  the program and replace the two args with the first result of the
  program.
  '''
  (quote, (x, stack)) = S
  result = joy((x, stack), quote, dictionary)[0]
  return (result[0], stack), expression, dictionary


'''
## app2

Like app1 with two items.
'''
def app2(S, expression, dictionary):
  '''Like app1 with two items.'''
  (quote, (x, (y, stack))) = S
  resultx = joy((x, stack), quote, dictionary)[0][0]
  resulty = joy((y, stack), quote, dictionary)[0][0]
  return (resultx, (resulty, stack)), expression, dictionary


'''
## app3

Like app1 with three items.
'''
def app3(S, expression, dictionary):
  '''Like app1 with three items.'''
  (quote, (x, (y, (z, stack)))) = S
  resultx = joy((x, stack), quote, dictionary)[0][0]
  resulty = joy((y, stack), quote, dictionary)[0][0]
  resultz = joy((z, stack), quote, dictionary)[0][0]
  return (resultx, (resulty, (resultz, stack))), expression, dictionary


'''
## step

The step combinator removes the aggregate and the quotation, and then
repeatedly puts the members of the aggregate on top of the remaining
stack and executes the quotation.
'''
def step(S, expression, dictionary):
  (quote, (aggregate, stack)) = S
  for term in iter_stack(aggregate):
    stack = joy((term, stack), quote, dictionary)[0]
  return stack, expression, dictionary


'''
## while

    [if] [body] while

'''
def while_(S, expression, dictionary):
  (body, (if_, stack)) = S
  while joy(stack, if_, dictionary)[0][0]:
    stack = joy(stack, body, dictionary)[0]
  return stack, expression, dictionary


'''
## nullary

Run the program on TOS and return its first result without consuming
any of the stack (except the program on TOS.)
'''
def nullary(S, expression, dictionary):
  (quote, stack) = S
  result = joy(stack, quote, dictionary)
  return (result[0][0], stack), expression, dictionary


'''
## unary

Run the program on TOS and return its first result, consuming exactly one
item from the stack (in addition to the program on TOS.)
'''
def unary(S, expression, dictionary):
  (quote, stack) = S
  _, return_stack = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary


'''
## binary

Run the program on TOS and return its first result, consuming exactly two
items from the stack (in addition to the program on TOS.)
'''
def binary(S, expression, dictionary):
  (quote, stack) = S
  _, (_, return_stack) = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary


'''
## ternary

Run the program on TOS and return its first result, consuming exactly
three items from the stack (in addition to the program on TOS.)
'''
def ternary(S, expression, dictionary):
  (quote, stack) = S
  _, (_, (_, return_stack)) = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary


'''
### Miscellaneous Commented-out Code
'''
##def dip(S):
##  (quote, (x, stack)) = S
##  return x, joy(quote, stack)


##def ifte(S):
##  '''[if] [then] [else] ifte'''
##  (else_, (then, (if_, stack))) = S
##  if_res = joy(if_, stack)[0]
##  if if_res:
##    result = joy(then, stack)[0]
##  else:
##    result = joy(else_, stack)[0]
##  return result, stack


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
