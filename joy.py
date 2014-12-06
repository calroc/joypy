#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''


A dialect of Joy in Python.


--------------------------------------------------


Joy is a programming language created by Manfred von Thun that is easy to
use and understand and has many other nice properties.  This Python script
is an interpreter for a dialect of Joy that attempts to stay very close
to the spirit of Joy but does not precisely match the behaviour of the
original version(s) written in C.  A Tkinter GUI is provided as well.


--------------------------------------------------


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


--------------------------------------------------


Table of Contents

  Introduction

  Part I - Joy
    Manfred von Thun, Appreciation
    Simplicity
    Basics of Joy
    Literals and Simple Functions
    Simple Combinators
    Definitions and More Elaborate Functions
    Programming and Metaprogramming
    Further Reading

  Part II - This Implementation

    joy()

    Converting text to a joy expression.
      parse()
      tokenize()
      convert()

    Stack
      list_to_stack()
      iter_stack()
      stack_to_string()

    Functions
      stack → stack
      note() decorator
      define several functions

    Combinators
      functions that call joy()

    Definitions
      functions as equations

    Initialize
      add functions from Python operator module
      add aliases
      add definitions

    REPL (Read, Eval, Print Loop)

  Part III - The GUI

    History
    Structure
    Commands
      Mouse Chords
      Keyboard
    Output from Joy

  References


--------------------------------------------------


§ Introduction

I don't recall exactly how or when I first heard of the Joy programming
language, or even what it was that recently prompted me to investigate
it and write this interpreter.  I am glad it happened though because as
I study Joy I find that it is very aptly named.  It is clear, concise,
and ameniable to advanced techniques for constructing bug-free
software.

Backus' Turing award paper - Functional programming - Notation for
mathematical programming

Exploring the system using this Python implementation - Pickling system
state - The GUI


--------------------------------------------------


Part I - Joy

Developed by Manfred von Thun, don't know much about him, not much on
the web about Joy and von Thun (Von Thun?) Several other people have
played with it.  Other languages (Factor, Cat, Kont, etc?) I wish I had
known of it a decade ago when it was the subject of active work.

Stack based - literals (as functions) - functions - combinators -
Refactoring and making new definitions - traces and comparing
performance - metaprogramming as programming, even the lowly integer
range function can be expressed in two phases: building a specialized
program and then executing it with a combinator - ?Partial evaluation?
- ?memoized dynamic dependency graphs? - algebra

Because it has desirable properties (concise, highly factored) the
programming process changes, the ratio of designing to writing code
shifts in favor of design.  The documentation becomes extensive while
the code shrinks to stable bodies of small well-factored incantations
that are highly expressive, much like mathematical papers consist of
large bodies of exposition interlaced with mathematical formula that
concisely and precisely express the meaning of the text.

The time and attention of the programmer shifts from thinking about the
language to thinking in the language, and the development process feels
more like deriving mathematical truths than like writing ad-hoc
solitions.

I hope that this script is useful in the sense that it provides an
additional joy interpreter (the binary in the archive from La Trobe
seems to run just fine on my modern Linux machine!)  But I also hope
that you can read and understand the Python code if you want to and
play with the implementation itself.

The best source (no pun intended) for learning about Joy is the
information made available at the website of La Trobe University (see
the references section at the end of this script for the URL) which
contains source code for the original C interpreter, Joy language source
code for various functions, and a great deal of fascinating material
mostly written by Von Thun on Joy and its deeper facets as well as how
to program in it and several interesting aspects.  It's quite a
treasure trove.

§ Basics of Joy

Joy is stack-based.  There is a main stack that holds data items:
numbers, strings, functions, and sequences which hold data items
themselves.  All functions are considered to be unary, accepting a
stack and returning a stack (including technically number, string, and
sequence literals which are considered functions that return stacks
with their value on the top.)

A Joy expression is just a sequence of items.  The evaluation proceeds
by putting all literals onto the main stack and executing functions as
they are encountered, passing them the current main stack and replacing
the main stack with the result returned.

The main loop is very simple as most of the action happens through what
are called "Combinators", which accept sequences on the stack and run
them (using the joy() function) in various ways.  These combinators
factor specific patterns that provide the effect of control-flow in
other languages (such as ifte which is like if..then..else..) and
strange and wonderful effects (such as cleave which is a simple
concurrency combinator.)

**Mention that sequences intended as programs are called "quoted
programs".

§ Literals and Simple Functions

    joy? 1 2 3
    -> 3 2 1

    joy? +
    -> 5 1

    joy? +
    -> 6

    joy? 7
    -> 7 6

    joy? *
    -> 42

    joy?


§ Simple Combinators

    joy? 23 [0 >] [dup --] while

    -> 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23


§ Definitions and More Elaborate Functions
  Refactoring

§ Programming and Metaprogramming

§ Further Reading


--------------------------------------------------


Part II - This Implementation


'''
from sys import stderr, modules
from time import time
from inspect import getmembers, isbuiltin, getdoc, getsource
from traceback import print_exc
from functools import wraps
from re import Scanner
import os
import operator, math


TRACE = False


class TraceWrapper(object):
  '''
  Wrap the joy() function in an object that keeps track of the execution
  trace of the interpreter.  This trace datastructure contains each stack
  and expression that the joy() function has run during the execution of
  some expression, and it can be useful for exploring and re-running.

  Note that the frame attribute is accumulating the actual stack and
  expression tuples not copies or records.
  '''

  def __init__(self, J):
    self.joy = J
    self.frame = []
    self.stack = []

  def __call__(self, expression, stack):
    global _print_trace
    _print_trace, pt = self._print_trace, _print_trace
    self._start_call()
    try:
      return self.joy(expression, stack)
    finally:
      _print_trace = pt
      self._end_call()

  def _print_trace(self, stack, expression):
    self.frame.append((stack, expression))

  def _start_call(self):
    self.stack.append(self.frame)
    self.frame = []
    self.stack[-1].append(self.frame)

  def _end_call(self):
    self.frame = self.stack.pop()
    self.frame[-1] = self.frame[-1]

  def show_trace(self, f=None, indent=0):
    if f is None:
      f = self.frame
    for n in f:
      if isinstance(n, tuple):
        s, e = n
        print ' ' * indent,
        _print_trace(s, e)
      else:
        self.show_trace(n, indent + 2)


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



@TraceWrapper
def joy(expression, stack):
  '''
  Evaluate the Joy expression on the stack.
  '''
  while expression:

    if TRACE:
      _print_trace(stack, expression)

    term, expression = expression

    if is_function(term):
      stack = term(stack)
    else:
      stack = term, stack

  return stack


'''


§ Converting text to a joy expression.

  parse()
  tokenize()
  convert()


'''


def run(text, stack):
  '''
  Return the stack resulting from running the Joy code text on the stack.
  '''
  tokens = tokenize(text)
  expression = parse(tokens)
  return joy(expression, stack)


def parse(tokens):
  '''
  Return a stack/list expression of the tokens.
  '''
  frame = []
  stack = []
  for tok in tokens:
    if tok == '[':
      stack.append(frame)
      frame = []
      stack[-1].append(frame)
    elif tok == ']':
      frame = stack.pop()
      frame[-1] = list_to_stack(frame[-1])
    else:
      frame.append(tok)
  return list_to_stack(frame)


def tokenize(text):
  '''
  Convert a text into a stream of tokens, look up command symbols and
  warn if any are unknown (the string symbols are left in place.)

  Raises ValueError if the scan fails along with some of the failing
  text.
  '''
  tokens, rest = scanner.scan(text)
  if rest:
    raise ValueError('Scan failed at position %i, %r'
                     % (len(text) - len(rest), rest[:10]))
  return tokens


def _scan_identifier(scanner, token): return convert(token)
def _scan_bracket(scanner, token): return token
def _scan_float(scanner, token): return float(token)
def _scan_int(scanner, token): return int(token)
def _scan_str(scanner, token): return token[1:-1].replace('\\"', '"')


scanner = Scanner([
  (r'-?\d+\.\d*', _scan_float),
  (r'-?\d+', _scan_int),
  (r'[•\w!@$%^&*()_+<>?|\/;:`~,.=-]+', _scan_identifier),
  (r'\[|\]', _scan_bracket),
  (r'"(?:[^"\\]|\\.)*"', _scan_str),
  (r'\s+', None),
  ])


def convert(token):
  '''Look up symbols in the functions dict.'''
  try:
    return FUNCTIONS[token]
  except KeyError:
    print >> stderr, 'unknown word', token
    return token


'''


§ Stack

When talking about Joy we use the terms "stack", "list", "sequence" and
"aggregate" to mean the same thing: a simple datatype that permits
certain operations such as iterating through it and pushing and popping
values from (at least) one end.

We use the venerable two-tuple recursive form of sequences where the
empty tuple () is the empty stack and (head, rest) gives the recursive
form of a stack with one or more items on it.

  ()
  (1, ())
  (1, (2, ()))
  (1, (2, (3, ())))
  ...

And so on.

We have two very simple functions to build up a stack from a Python
iterable and also to iterate through a stack and yield its items
one-by-one in order, and two functions to generate string representations
of stacks:

  list_to_stack()

  iter_stack()

  stack_to_string()

  strstack()


'''


def list_to_stack(el, stack=()):
  '''Convert a list (or other sequence) to a stack.'''
  for item in reversed(el):
    stack = item, stack
  return stack


def iter_stack(stack):
  '''Iterate through the items on the stack.'''
  while stack:
    item, stack = stack
    yield item


def stack_to_string(expression):
  '''
  Return a "pretty print" string for a stack.

  Ideally the output of this should result in the same expression if
  passed through tokenize() and parse(), but not yet.
  '''
  if not isinstance(expression, tuple):
    return repr(expression)
  return '[%s]' % strstack(expression)


def strstack(stack):
  if not isinstance(stack, tuple):
    return repr(stack)
  if not stack: # shortcut
    return ''
  return ' '.join(map(stack_to_string, iter_stack(stack)))


'''

A word about the stack data structure.

Python has very nice "tuple packing and unpacking" built into it in
several places in its syntax, including (delightfully) function argument
specifiers.  This means we can directly "unpack" the expected arguments
to a Joy function right in the definition.

For example:

  def dup(stack):
    head, tail = stack
    return head, (head, tail)

Becomes:

  def dup((head, tail)):
    return head, (head, tail)

We replace the argument "stack" by the expected structure of the stack,
in this case "(head, tail)", and Python takes care of de-structuring the
incoming argument and assigning values to the names.  Note that Python
syntax doesn't require parentheses around tuples used in expressions
where they would be redundant but they are not redundant around the tuple
appearing in the argspec.

Consider:

  def f((a, b)): ...

  def g(a, b): ...

Function f() expects one thing made of (a, b) while function g() expects
two separate things.  The two argspecs are not equivalent.

With stacks out of the way let's talk about functions.


§ Functions

  stack → stack
  note() decorator
  define several functions
  wrap functions from Python operator module


We can catagorize functions into those that rearrange things on the stack
but don't otherwise process them, those that perform some process on
them, and those that call back into the joy() function to execute one or
more quoted programs themselves.  And, of course, there are commands that
do more than one or all three.

Commands that execute quoted programs are called "Combinators" and
they are the key to Joy's expressiveness and power.  The joy()
function by itself wouldn't accomplish much but with the availability of
several combinators it becomes a powerhouse.

Commands that just rearrange things on the stack can be written in python
as simple tuple unpacking and repacking.

Definitions, functions defined by equations, refactoring and how
important it is..


'''


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


def is_function(term):
  '''
  Return a Boolean value indicating whether or not a term is a function.
  '''
  # In Python the tuple type is callable so we have to check for that.
  # We could also just check isinstance(term, FunctionWrapper), but this
  # way we can use any old callable as a function if we like.
  return callable(term) and not isinstance(term, tuple)


ALIASES = (
  ('add', ['+']),
  ('mul', ['*']),
  ('div', ['/']),
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
def cons((tos, (second, stack))):
  '''
  The cons operator expects a list on top of the stack and the potential
  member below. The effect is to add the potential member into the
  aggregate.
  '''
  return (second, tos), stack


@note
def uncons((tos, stack)):
  '''
  Inverse of cons, removes an item from the top of the list on the stack
  and places it under the remaining list.
  '''
  item, tos = tos
  return tos, (item, stack)


@note
def clear(stack):
  '''Clear everything from the stack.'''
  return ()


@note
def dup((tos, stack)):
  '''Duplicate the top item on the stack.'''
  return tos, (tos, stack)


@note
def swap((tos, (second, stack))):
  '''Swap the top two items on stack.'''
  return second, (tos, stack)


@note
def stack_(stack):
  '''
  The stack operator pushes onto the stack a list containing all the
  elements of the stack.
  '''
  return stack, stack


@note
def unstack((tos, stack)):
  '''
  The unstack operator expects a list on top of the stack and makes that
  the stack discarding the rest of the stack.
  '''
  return tos


@note
def pop((tos, stack)):
  '''Pop and discard the top item from the stack.'''
  return stack


@note
def popd((tos, (second, stack))):
  '''Pop and discard the second item from the stack.'''
  return tos, stack


@note
def popop((tos, (second, stack))):
  '''Pop and discard the first and second items from the stack.'''
  return stack


@note
def dupd((tos, (second, stack))):
  '''Duplicate the second item on the stack.'''
  return tos, (second, (second, stack))


@note
def reverse((tos, stack)):
  '''Reverse the list on the top of the stack.'''
  res = ()
  for term in iter_stack(tos):
    res = term, res
  return res, stack


@note
def concat((tos, (second, stack))):
  '''Concatinate the two lists on the top of the stack.'''
  for term in reversed(list(iter_stack(second))):
    tos = term, tos
  return tos, stack


@note
def zip_((tos, (second, stack))):
  '''
  Replace the two lists on the top of the stack with a list of the pairs
  from each list.  The smallest list sets the length of the result list.
  '''
  accumulator = [
    (a, (b, ()))
    for a, b in zip(iter_stack(tos), iter_stack(second))
    ]
  return list_to_stack(accumulator), stack


@note
def succ((tos, stack)):
  '''Increment TOS.'''
  return tos + 1, stack


@note
def pred((tos, stack)):
  '''Decrement TOS.'''
  return tos - 1, stack


@note
def rollup((a, (b, (c, stack)))):
  '''a b c -> b c a'''
  return b, (c, (a, stack))


@note
def rolldown((a, (b, (c, stack)))):
  '''a b c -> c a b'''
  return c, (a, (b, stack))


@note
def execute((text, stack)):
  if isinstance(text, basestring):
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
  print ' '.join(sorted(FUNCTIONS))
  return stack


@note
def simple_manual(stack):
  '''
  Print words and help for each word.
  '''
  for name, f in sorted(FUNCTIONS.items()):
    d = getdoc(f)
    boxline = '+%s+' % ('-' * (len(name) + 2))
    print '\n'.join((
      boxline,
      '| %s |' % (name,),
      boxline,
      d if d else '   ...',
      '',
      '--' * 40,
      '',
      ))
  return stack


@note
def help_((quote, stack)):
  '''Accepts a quoted word on the top of the stack and prints its docs.'''
  word = quote[0]
  print getdoc(word)
  return stack


@note
def TRACE_(stack):
  '''Toggle print out of execution trace.'''
  global TRACE
  TRACE = not TRACE
  return stack


'''


§ Combinators

  functions that call joy()


'''


@note
def map_((quote, (aggregate, stack))):
  '''
  Run the quoted program on TOS on the items in the list under it, push a
  new list with the results (in place of the program and original list.
  '''
  results = list_to_stack([
    joy(quote, (term, stack))[0]
    for term in iter_stack(aggregate)
    ])
  return results, stack


@note
def i((quote, stack)):
  '''Execute the quoted program on TOS on the rest of the stack.'''
  return joy(quote, stack)


@note
def x((quote, stack)):
  '''
  Like i but don't remove the program first.  In other words the
  program gets itself as its first arg.
  '''
  return joy(quote, (quote, stack))


@note
def infra((quote, (aggregate, stack))):
  '''
  Accept a quoted program and a list on the stack and run the program
  with the list as its stack.
  '''
  return joy(quote, aggregate), stack


@note
def b((Q, (P, stack))):
  '''
  Given two quoted programs on the stack run the second one then the one
  on TOS.
  '''
  return joy(Q, joy(P, stack))


@note
def cleave((Q, (P, (x, stack)))):
  '''
  The cleave combinator expects two quotations, and below that an item X.
  It first executes [P], with X on top, and saves the top result element.
  Then it executes [Q], again with X, and saves the top result.
  Finally it restores the stack to what it was below X and pushes the two
  results P(X) and Q(X).
  '''
  p = joy(P, (x, stack))[0]
  q = joy(Q, (x, stack))[0]
  return q, (p, stack)


@note
def ifte((else_, (then, (if_, stack)))):
  '''[if] [then] [else] ifte'''
  if_res = joy(if_, stack)[0]
  if if_res:
    result = joy(then, stack)[0]
  else:
    result = joy(else_, stack)[0]
  return result, stack


@note
def dip((quote, (x, stack))):
  '''
  dip expects a program [P] and below that another item X. It pops both,
  saves X, executes P and then restores X.
  '''
  return x, joy(quote, stack)


@note
def dipd((quote, (x, (y, stack)))):
  '''Like dip but expects two items.'''
  return x, (y, joy(quote, stack))


@note
def dipdd((quote, (x, (y, (z, stack))))):
  '''Like dip but expects three items.'''
  return x, (y, (z, joy(quote, stack)))


@note
def app1((quote, (x, stack))):
  '''
  Given a quoted program on TOS and anything as the second stack item run
  the program and replace the two args with the first result of the
  program.
  '''
  result = joy(quote, (x, stack))
  return result[0], stack


@note
def app2((quote, (x, (y, stack)))):
  '''Like app1 with two items.'''
  resultx = joy(quote, (x, stack))[0]
  resulty = joy(quote, (y, stack))[0]
  return resultx, (resulty, stack)


@note
def app3((quote, (x, (y, (z, stack))))):
  '''Like app1 with three items.'''
  resultx = joy(quote, (x, stack))[0]
  resulty = joy(quote, (y, stack))[0]
  resultz = joy(quote, (z, stack))[0]
  return resultx, (resulty, (resultz, stack))


@note
def step((quote, (aggregate, stack))):
  '''
  The step combinator removes the aggregate and the quotation, and then
  repeatedly puts the members of the aggregate on top of the remaining
  stack and executes the quotation.
  '''
  for term in iter_stack(aggregate):
    stack = joy(quote, (term, stack))
  return stack


@note
def while_((body, (if_, stack))):
  '''[if] [body] while'''
  while joy(if_, stack)[0]:
    stack = joy(body, stack)
  return stack


@note
def nullary((quote, stack)):
  '''
  Run the program on TOS and return its first result without consuming
  any of the stack (except the program on TOS.)
  '''
  result = joy(quote, stack)
  return result[0], stack


@note
def unary((quote, stack)):
  _, return_stack = stack
  result = joy(quote, stack)
  return result[0], return_stack


@note
def binary((quote, stack)):
  _, (_, return_stack) = stack
  result = joy(quote, stack)
  return result[0], return_stack


@note
def ternary((quote, stack)):
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

  def f(stack):
    global TRACE
    if TRACE:
      print '#', name, '==', strbody
    try:
      return joy(body, stack)
    finally:
      if TRACE:
        print '#', name, 'done.'

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
  return wraps(f)(lambda ((tos, stack)): (f(tos), stack))


def joyful_2_arg_op(f):
  '''
  Return a Joy function that pops the top two arguments from the stack
  and pushes f(second, tos) back.
  '''
  return wraps(f)(lambda ((tos, (second, stack))): (f(second, tos), stack))


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
      print
      print '->', strstack(stack)
      print
      try:
        text = raw_input('joy? ')
      except (EOFError, KeyboardInterrupt):
        break
      try:
        stack = run(text, stack)
      except:
        print_exc()
  except:
    print_exc()
  print
  return stack


def _print_trace(stack, expression):
  stack = list(iter_stack(stack))
  stack.reverse()
  print strstack(list_to_stack(stack)), u'\u2022', strstack(expression)


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


if __name__ == "__main__":
  initialize()
  stack = repl()
  if TRACE:
    joy.show_trace()
