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
  tokens = tokenize(text)
  expression = parse(tokens)
  return joy(expression, stack)




FUNCTIONS = {}


class FunctionWrapper(object):
  '''
  Allow functions to have a nice repr().
  '''
  def __init__(self, f):
    self.f = f
    self.name = f.__name__.rstrip('_')
  def __call__(self, stack):
    return self.f(stack)
  def __repr__(self):
    return self.name


def note(f):
  '''Decorator to enter functions into the function map.'''
  F = wraps(f)(FunctionWrapper(f))
  FUNCTIONS[F.name] = F
  return F


def combinator(funcwrapper):
  '''
  Let combinators have special handling.

  So far we just let them add messages to the trace.
  '''
  _exit_message = funcwrapper.name + ' done.'
  f = funcwrapper.f
  @wraps(f)
  def F(stack):
    try:
      return f(stack)
    finally:
      if TRACE: joy.add_message(_exit_message)
  funcwrapper.f = F
  return funcwrapper


def is_function(term):
  '''
  Return a Boolean value indicating whether or not a term is a function.
  '''
  # In Python the tuple type is callable so we have to check for that.
  # We could also just check isinstance(term, FunctionWrapper), but this
  # way we can use any old callable as a function if we like.
  return isinstance(term, collections.Callable) and not isinstance(term, tuple)


ALIASES = (
  ('add', ['+']),
  ('mul', ['*']),
  ('truediv', ['/']),
  ('mod', ['%', 'rem', 'remainder', 'modulus']),
  ('eq', ['=']),
  ('ge', ['>=']),
  ('gt', ['>']),
  ('le', ['<=']),
  ('lshift', ['<<']),
  ('lt', ['<']),
  ('ne', ['<>', '!=']),
  ('rshift', ['>>']),
  ('sub', ['-']),
  ('xor', ['^']),
  ('succ', ['++']),
  ('pred', ['--']),
  ('rolldown', ['roll<']),
  ('rollup', ['roll>']),
  ('id', ['•']),
#  ('', ['']),
  )


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


'''


§ Combinators

  functions that call joy()


'''


@combinator
@note
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


@combinator
@note
def i(S):
  '''Execute the quoted program on TOS on the rest of the stack.'''
  (quote, stack) = S
  return joy(quote, stack)


@combinator
@note
def x(S):
  '''
  Like i but don't remove the program first.  In other words the
  program gets itself as its first arg.
  '''
  (quote, stack) = S
  return joy(quote, (quote, stack))


@combinator
@note
def infra(S):
  '''
  Accept a quoted program and a list on the stack and run the program
  with the list as its stack.
  '''
  (quote, (aggregate, stack)) = S
  return joy(quote, aggregate), stack


@combinator
@note
def b(S):
  '''
  Given two quoted programs on the stack run the second one then the one
  on TOS.
  '''
  (Q, (P, stack)) = S
  return joy(Q, joy(P, stack))


@combinator
@note
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


@combinator
@note
def ifte(S):
  '''[if] [then] [else] ifte'''
  (else_, (then, (if_, stack))) = S
  if_res = joy(if_, stack)[0]
  if if_res:
    result = joy(then, stack)[0]
  else:
    result = joy(else_, stack)[0]
  return result, stack


@combinator
@note
def dip(S):
  '''
  dip expects a program [P] and below that another item X. It pops both,
  saves X, executes P and then restores X.
  '''
  (quote, (x, stack)) = S
  return x, joy(quote, stack)


@combinator
@note
def dipd(S):
  '''Like dip but expects two items.'''
  (quote, (x, (y, stack))) = S
  return x, (y, joy(quote, stack))


@combinator
@note
def dipdd(S):
  '''Like dip but expects three items.'''
  (quote, (x, (y, (z, stack)))) = S
  return x, (y, (z, joy(quote, stack)))


@combinator
@note
def app1(S):
  '''
  Given a quoted program on TOS and anything as the second stack item run
  the program and replace the two args with the first result of the
  program.
  '''
  (quote, (x, stack)) = S
  result = joy(quote, (x, stack))
  return result[0], stack


@combinator
@note
def app2(S):
  '''Like app1 with two items.'''
  (quote, (x, (y, stack))) = S
  resultx = joy(quote, (x, stack))[0]
  resulty = joy(quote, (y, stack))[0]
  return resultx, (resulty, stack)


@combinator
@note
def app3(S):
  '''Like app1 with three items.'''
  (quote, (x, (y, (z, stack)))) = S
  resultx = joy(quote, (x, stack))[0]
  resulty = joy(quote, (y, stack))[0]
  resultz = joy(quote, (z, stack))[0]
  return resultx, (resulty, (resultz, stack))


@combinator
@note
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


@combinator
@note
def while_(S):
  '''[if] [body] while'''
  (body, (if_, stack)) = S
  while joy(if_, stack)[0]:
    stack = joy(body, stack)
  return stack


@combinator
@note
def nullary(S):
  '''
  Run the program on TOS and return its first result without consuming
  any of the stack (except the program on TOS.)
  '''
  (quote, stack) = S
  result = joy(quote, stack)
  return result[0], stack


@combinator
@note
def unary(S):
  (quote, stack) = S
  _, return_stack = stack
  result = joy(quote, stack)
  return result[0], return_stack


@combinator
@note
def binary(S):
  (quote, stack) = S
  _, (_, return_stack) = stack
  result = joy(quote, stack)
  return result[0], return_stack


@combinator
@note
def ternary(S):
  (quote, stack) = S
  _, (_, (_, return_stack)) = stack
  result = joy(quote, stack)
  return result[0], return_stack


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

