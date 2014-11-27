#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''


A dialect of Joy in Python.


Joy is a programming language created by Manfred von Thun that is easy to
use and understand and has many other nice properties.  This Python script
is an interpreter for a dialect of Joy that attempts to stay very close
to the spirit of Joy but does not precisely match the behaviour of the
original version(s) written in C.  A Tkinter GUI is provided too.


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


Table of Contents

  Introduction
    GUI Quick-start

  Part I - Joy
    Manfred von Thun, Appreciation
    Simplicity

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
      wrap functions from Python operator module

    Combinators
      functions that call joy()

    Definitions
      functions as equations

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


Introduction

  Quick-start for the GUI ('joy.py --gui'):

  Right-click on the numbers and words here to put two numbers on the stack
  and add them together.  (If you get a gray error window just close it.)

  123 500 add

<STACK


--------------------------------------------------


Part I - Joy
  Manfred von Thun, Appreciation
  Simplicity


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

    quoted == [[] cons] dip ;
  unquoted == [i] dip ;

  enstacken == stack [clear] dip ;

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


''' # End of DEFINITIONS


'''


Part II - This Implementation


'''
from sys import stderr, modules
from time import time
from inspect import getmembers, isbuiltin, getdoc, getsource
from traceback import print_exc, format_exc
from functools import wraps
from re import Scanner, compile as regular_expression
from Tkinter import (Text, Toplevel, TclError, END,
                     INSERT, SEL, DISABLED, NORMAL, BOTH)
from tkFont import families, Font
import os
import operator, math


TRACE = False


'''


joy()

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
      _print_trace(stack, expression)

    term, expression = expression

    if callable(term) and not isinstance(term, tuple):
      stack = term(stack)
    else:
      stack = term, stack

  return stack


'''


Converting text to a joy expression.
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


Stack

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
one-by-one in order:

  list_to_stack()

  iter_stack()

  stack_to_string()


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

A word about the stacks.

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


Functions
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
  '''Accepts a quoted word on the top os the stack and prints its docs.'''
  word = quote[0]
  print getdoc(word)
  return stack


@note
def TRACE_(stack):
  '''Toggle print out of execution trace.'''
  global TRACE
  TRACE = not TRACE
  return stack


# Auto-generate functions from Python builtins.


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

for module in (operator, math):
  for name, function in getmembers(module, isbuiltin):

    if name.startswith('_') or name.startswith('i'):
      continue

    if is_unary_math_op(function):
      note(joyful_1_arg_op(function))

    elif is_binary_math_op(function):
      note(joyful_2_arg_op(function))

    else:
      _non.append(function)


# Now that all the functions are in the dict, add the aliases.
for name, aliases in ALIASES:
  for alias in aliases:
    FUNCTIONS[alias] = FUNCTIONS[name]


'''


  Combinators
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


'''


Definitions
  functions as equations


'''


def add_definition(d):
  '''
  Given the text of a definition such as "sum == 0 swap [+] step" add the
  parsed body expression to FUNCTIONS under that name.
  '''
  name, proper, body_text = (n.strip() for n in d.partition('=='))
  if not proper:
    if d: # Ignore chunks of blankspace, report failed text.
      print >> stderr, 'definition', repr(d), 'failed'
    return

  body = parse(tokenize(body_text))
  strbody = strstack(body)

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
  print strstack(list_to_stack(stack)),
  print u'\u2022', strstack(expression)


'''


Part III - The GUI

  History
  Structure
  Commands
    Mouse Chords
    Keyboard
  Output from Joy


'''


class WorldWrapper:

  def __init__(self, stack=(), text_widget=None):
    self.stack = stack
    self.text_widget = text_widget

  def do_lookup(self, name):
    word = FUNCTIONS[name]
    self.stack = word, self.stack
    self.print_stack()

  def do_opendoc(self, name):
    self.do_lookup(name)

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
    self.stack = run(command, self.stack)
    self.print_stack()

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


#Do-nothing event handler.
nothing = lambda event: None


class mousebindingsmixin:
  """TextViewerWidget mixin class to provide mouse bindings."""

  def __init__(self):

    #Remember our mouse button state
    self.B1_DOWN = False
    self.B2_DOWN = False
    self.B3_DOWN = False

    #Remember our pending action.
    self.dothis = nothing

    #We'll need to remember whether or not we've been moving B2.
    self.beenMovingB2 = False

    #Unbind the events we're interested in.
    for sequence in (
      "<Button-1>", "<B1-Motion>", "<ButtonRelease-1>",
      "<Button-2>", "<B2-Motion>", "<ButtonRelease-2>",
      "<Button-3>", "<B3-Motion>", "<ButtonRelease-3>",
      "<B1-Leave>", "<B2-Leave>", "<B3-Leave>", "<Any-Leave>", "<Leave>"
      ):
      self.unbind(sequence)
      self.unbind_all(sequence)

    self.event_delete('<<PasteSelection>>') #I forgot what this was for! :-P  D'oh!

    #Bind our event handlers to their events.
    self.bind("<Button-1>", self.B1d)
    self.bind("<B1-Motion>", self.B1m)
    self.bind("<ButtonRelease-1>", self.B1r)

    self.bind("<Button-2>", self.B2d)
    self.bind("<B2-Motion>", self.B2m)
    self.bind("<ButtonRelease-2>", self.B2r)

    self.bind("<Button-3>", self.B3d)
    self.bind("<B3-Motion>", self.B3m)
    self.bind("<ButtonRelease-3>", self.B3r)

    self.bind("<Any-Leave>", self.leave)

  def B1d(self, event):
    '''button one pressed'''
    self.B1_DOWN = True

    if self.B2_DOWN:

      self.unset_command()

      if self.B3_DOWN :
        self.dothis = self.cancel

      else:
        #copy TOS to the mouse (instead of system selection.)
        self.dothis = self.copyto #middle-left-interclick

    elif self.B3_DOWN :
      self.unset_command()
      self.dothis = self.opendoc #right-left-interclick

    else:
      ##button 1 down, set insertion and begin selection.
      ##Actually, do nothing. Tk Text widget defaults take care of it.
      self.dothis = nothing
      return

    #Prevent further event handling by returning "break".
    return "break"

  def B2d(self, event):
    '''button two pressed'''
    self.B2_DOWN = 1

    if self.B1_DOWN :

      if self.B3_DOWN :
        self.dothis = self.cancel

      else:
        #left-middle-interclick - cut selection to stack
        self.dothis = self.cut

    elif self.B3_DOWN :
      self.unset_command()
      self.dothis = self.lookup #right-middle-interclick - lookup

    else:
      #middle-click - paste X selection to mouse pointer
      self.set_insertion_point(event)
      self.dothis = self.paste_X_selection_to_mouse_pointer
      return

    return "break"

  def B3d(self, event):
    '''button three pressed'''
    self.B3_DOWN = 1

    if self.B1_DOWN :

      if self.B2_DOWN :
        self.dothis = self.cancel

      else:
        #left-right-interclick - copy selection to stack
        self.dothis = self.run_selection

    elif self.B2_DOWN :
      #middle-right-interclick - Pop/Cut from TOS to insertion cursor
      self.unset_command()
      self.dothis = self.pastecut

    else:
      #right-click
      self.CommandFirstDown(event)

    return "break"

  def B1m(self, event):
    '''button one moved'''
    if self.B2_DOWN or self.B3_DOWN:
      return "break"

  def B2m(self, event):
    '''button two moved'''
    if self.dothis == self.paste_X_selection_to_mouse_pointer and \
       not (self.B1_DOWN or self.B3_DOWN):

      self.beenMovingB2 = True
      return

    return "break"

  def B3m(self, event):
    '''button three moved'''
    if self.dothis == self.do_command and \
       not (self.B1_DOWN or self.B2_DOWN):

      self.update_command_word(event)

    return "break"

  def B1r(self, event):
    '''button one released'''
    self.B1_DOWN = False

    if not (self.B2_DOWN or self.B3_DOWN):
      self.dothis(event)

    return "break"

  def B2r(self, event):
    '''button two released'''
    self.B2_DOWN = False

    if not (self.B1_DOWN or self.B3_DOWN or self.beenMovingB2):
      self.dothis(event)

    self.beenMovingB2 = False

    return "break"

  def B3r(self, event):
    '''button three released'''
    self.B3_DOWN = False

    if not (self.B1_DOWN or self.B2_DOWN) :
      self.dothis(event)

    return "break"

  def InsertFirstDown(self, event):
    self.focus()
    self.dothis = nothing
    self.set_insertion_point(event)

  def CommandFirstDown(self, event):
    self.dothis = self.do_command
    self.update_command_word(event)


#: Define mapping between Tkinter events and functions or methods. The
#: keys are string Tk "event sequences" and the values are callables that
#: get passed the TextViewer instance (so you can bind to methods) and
#: must return the actual callable to which to bind the event sequence.
text_bindings = {

  #I want to ensure that these keyboard shortcuts work.
  '<Control-v>': lambda tv: tv._paste,
  '<Control-V>': lambda tv: tv._paste,
  '<Shift-Insert>': lambda tv: tv._paste,

  }


class TextViewerWidget(Text, mousebindingsmixin):
  """
  This class is a Tkinter Text with special mousebindings to make
  it act as a Xerblin Text Viewer.
  """

  #This is a regular expression for finding commands in the text.
  command_re = regular_expression(r'[-a-zA-Z0-9_\\~/.:!@#$%&*?=+]+')

  #These are the config tags for command text when it's highlighted.
  command_tags = dict(
    underline = 1,
    bgstipple = "gray50",
    borderwidth = "1",
    foreground = "orange"
  )

  def __init__(self, world, master=None,  **kw):

    # Get the filename associated with this widget's contents, if any.
    self.filename = kw.pop('filename', False)

    self.world = world
    if self.world.text_widget is None:
      self.world.text_widget = self

    #Turn on undo, but don't override a passed-in setting.
    kw.setdefault('undo', True)

#        kw.setdefault('bg', 'white')
    kw.setdefault('wrap', 'word')
    kw.setdefault('font', 'arial 12')

    #Create ourselves as a Tkinter Text
    Text.__init__(self, master, **kw)

    #Initialize our mouse mixin.
    mousebindingsmixin.__init__(self)

    #Add tag config for command highlighting.
    self.tag_config('command', **self.command_tags)

    #Create us a command instance variable
    self.command = ''

    #Activate event bindings. Modify text_bindings in your config
    #file to affect the key bindings and whatnot here.
    for event_sequence, callback_finder in text_bindings.iteritems():
      callback = callback_finder(self)
      self.bind(event_sequence, callback)

    self.tk.call(self._w, 'edit', 'modified', 0)
    self.bind('<<Modified>>', self._beenModified)
    self._resetting_modified_flag = False

##        T.protocol("WM_DELETE_WINDOW", self.on_close)

  def _beenModified(self, event):
    if self._resetting_modified_flag:
      return
    self._clearModifiedFlag()
    self.save()

  def _clearModifiedFlag(self):
    self._resetting_modified_flag = True
    try:
      self.tk.call(self._w, 'edit', 'modified', 0)
    finally:
      self._resetting_modified_flag = False

  _saveDelay = 2000

  def save(self):
    '''
    Call _saveFunc() after a certain amount of idle time.

    Called by _beenModified().
    '''
    self._cancelSave()
    self._saveAfter(self._saveDelay)

  def _saveFunc(self):
    self._save = None
    if not self.filename:
      return
    self['state'] = DISABLED
    try:
      text = self.get_contents()
      with open(self.filename, 'w') as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
      self.world.save()
    finally:
      self['state'] = NORMAL

##        tags = self._saveTags()
##        chunks = self.DUMP()
##        print chunks

  def _saveAfter(self, delay):
    '''
    Trigger a cancel-able call to _saveFunc() after delay milliseconds.
    '''
    self._save = self.after(delay, self._saveFunc)

  def _cancelSave(self):
    try:
      save = self._save
    except AttributeError:
      pass
    else:
      if save:
        self.after_cancel(save)
        save = None

  def get_contents(self):
    return self.get('0.0', END)[:-1]

  def findCommandInLine(self, line, index):
    '''findCommandInLine(line, index) => command, begin, end
    Return the command at index in line and its begin and end indices.'''

    #Iterate through the possible commands in the line...
    for match in self.command_re.finditer(line):

      #Pull out the indices of the possible command.
      b, e = match.span()

      #If the indices bracket the index return the result.
      if b <= index <= e:
        return match.group(), b, e

  def paste_X_selection_to_mouse_pointer(self, event):
    '''Paste the X selection to the mouse pointer.'''

    #Use the Tkinter method selection_get() to try to get the X selection.
    try:
      text = self.selection_get()

    #TclError gets raised if no current selection.
    except TclError:

      #So just carry on, there's nothing to do.
      return 'break'

    self.insert_it(text)

  def update_command_word(self, event):
    '''Highlight the command under the mouse.'''

    #Get rid of any old command highlighting.
    self.unset_command()

    #Get the index of the mouse.
    index = '@%d,%d' % (event.x, event.y)

    #Find coordinates for the line under the mouse.
    linestart = self.index(index + 'linestart')
    lineend = self.index(index + 'lineend')

    #Get the entire line under the mouse.
    line = self.get(linestart, lineend)

    #Parse out the row and offset of the mouse
    row, offset = self._get_index(index)

    #If the mouse is off the end of the line or on a space..
    if offset >= len(line) or line[offset].isspace():

      #There's no command, we're done.
      self.command = ''
      return

    #Get the command at the offset in the line.
    cmd = self.findCommandInLine(line, offset)

    if cmd and (self.world.has(cmd[0]) or isNumerical(cmd[0])):

      #Set self's command variable and extract the indices of it.
      self.command, b, e = cmd

      #Get the indices relative to the Text.
      cmdstart = self.index('%d.%d' % (row, b))
      cmdend = self.index('%d.%d' % (row, e))

      #Add the command highlighting tags to the command text.
      self.tag_add('command', cmdstart, cmdend)

    #If there was no command, clear our command variable.
    else:
      self.command = ''

  def do_command(self, event):
    '''Do the currently highlighted command.'''

    #Remove any old highlighting.
    self.unset_command()

    #If there is a current command..
    if self.command:

      #Interpret the current command.
      self.run_command(self.command)

  def run_command(self, command):
    '''Given a string run it on the stack, report errors.'''
    try:
      self.world.interpret(command)
    except SystemExit:
      raise
    except:
      self.popupTB(format_exc().rstrip())

  def unset_command(self):
    '''Remove any command highlighting.'''
    self.tag_remove('command', 1.0, END)

  def set_insertion_point(self, event):
    '''Set the insertion cursor to the current mouse location.'''
    self.focus()
    self.mark_set(INSERT, '@%d,%d' % (event.x, event.y))

  def cut(self, event):
    '''Cut selection to stack.'''

    #Get the indices of the current selection if any.
    select_indices = self.tag_ranges(SEL)

    #If there is a current selection..
    if select_indices:

      #Get the text of it.
      s = self.get(select_indices[0], select_indices[1])

      #Append the text to our interpreter's stack.
      self.world.push(s)

      #Let the pre-existing machinery take care of cutting the selection.
      self.event_generate("<<Cut>>")

  def copyto(self, event):
    '''Actually "paste" from TOS'''
    try:
      s = self.world.peek()
    except IndexError:
      return
    self.insert_it(s)

  def insert_it(self, s):

    #Make sure it's a string.
    if not isinstance(s, basestring):
      s = str(s)

    #When pasting from the mouse we have to remove the current selection
    #to prevent destroying it by the paste operation.

    #Find out if there's a current selection.
    select_indices = self.tag_ranges(SEL)

    #If there's a selection.
    if select_indices:

      #Remember that we have to reset it after pasting.
      reset_selection = True

      #Set two marks to remember the selection.
      self.mark_set('_sel_start', select_indices[0])
      self.mark_set('_sel_end', select_indices[1])

      #Remove the selection.
      self.tag_remove(SEL, 1.0, END)

    #If there's no selection we don't have to reset it
    else:
      reset_selection = False

    #Insert the TOS string.
    self.insert(INSERT, s)

    #If we have to reset the selection...
    if reset_selection:

      #Put the SEL tag back.
      self.tag_add(SEL, '_sel_start', '_sel_end')

      #Get rid of the marks we set.
      self.mark_unset('_sel_start')
      self.mark_unset('_sel_end')

    #Key pasting should still work fine, allowing one to select a piece
    #of text and paste to it, replacing the selection.

  def run_selection(self, event):
    '''Run the current selection if any on the stack.'''

    #Get the selection.
    select_indices = self.tag_ranges(SEL)

    #If there is a selection..
    if select_indices:

      #Get the text of the selection.
      selection = self.get(select_indices[0], select_indices[1])

      #Remove the SEL tag from the whole Text.
      self.tag_remove(SEL, 1.0, END)

      self.run_command(selection)

  def pastecut(self, event):
    '''Cut the TOS item to the mouse.'''
    self.copyto(event)
    self.world.pop()

  def opendoc(self, event):
    '''OpenDoc the current command.'''
    if self.command:
      self.world.do_opendoc(self.command)

  def lookup(self, event):
    '''Look up the current command.'''
    if self.command:
      self.world.do_lookup(self.command)

  def cancel(self, event):
    '''Cancel whatever we're doing.'''
    
    #Remove any old highlighting.
    self.unset_command()

    #Unset our command variable
    self.command = ''

    #Remove the SEL tag
    self.tag_remove(SEL, 1.0, END)

    #Reset the selection anchor.
    self._sel_anchor = '0.0'

    #I don't know if this helps, or even if it does anything. But what the heck.
    self.mark_unset(INSERT)

  def leave(self, event):
    '''Called when mouse leaves the Text window.'''

    #Remove any old highlighting.
    self.unset_command()

    #Unset our command variable
    self.command = ''

  def _get_index(self, index):
    '''Get the index in (int, int) form of index.'''
    return tuple(map(int, self.index(index).split('.')))

  def _paste(self, event):
    '''Paste the system selection to the current selection, replacing it.'''

    #If we're "key" pasting, we have to move the insertion point
    #to the selection so the pasted text gets inserted at the
    #location of the deleted selection.

    #Get the current selection's indices if any.
    select_indices = self.tag_ranges(SEL)

    #If the selection exists.
    if select_indices:

      #Mark the location of the current insertion cursor 
      self.mark_set('tmark', INSERT)

      #Put the insertion cursor at the selection
      self.mark_set(INSERT, select_indices[1])

    #Paste to the current selection, or if none, to the insertion cursor.
    self.event_generate("<<Paste>>")

    #If we mess with the insertion cursor above, fix it now.
    if select_indices:

      #Put the insertion cursor back where it was.
      self.mark_set(INSERT, 'tmark')

      #And get rid of our unneeded mark.
      self.mark_unset('tmark')

    #Tell Tkinter that event handling for this event is over.
    return 'break'

  def popupTB(self, tb):
    top = Toplevel()
    T = TextViewerWidget(
      self.world,
      top,
      width=max(len(s) for s in tb.splitlines()) + 3,
      )

    T['background'] = 'darkgrey'
    T['foreground'] = 'darkblue'
    T.tag_config('err', foreground='yellow')

    T.insert(END, tb)
    last_line = str(int(T.index(END).split('.')[0]) - 1) + '.0'
    T.tag_add('err', last_line, END)
    T['state'] = DISABLED

    top.title(T.get(last_line, END).strip())

    T.pack(expand=1, fill=BOTH)
    T.see(END)


class FileFaker(object):
  def __init__(self, T):
    self.T = T
  def write(self, text):
    self.T.insert(END, text)


def isNumerical(s):
  try:
    float(s)
  except ValueError:
    return False
  return True


def get_font(family='EB Garamond', size=18):
  if family not in families():
    family = 'Times'
  return Font(family=family, size=size)


def own_source():
  return getsource(modules[__name__])


if __name__ == "__main__":
  import sys
  if '--gui' in sys.argv:
    t = TextViewerWidget(WorldWrapper())
    t['font'] = get_font()
    t._root().title('Joy')
    sys.stdout = FileFaker(t)

    print own_source()
    print_words(None)
    print '\n\n1 2 3 4 5\n\n'

    t.pack(expand=True, fill=BOTH)
    t.mainloop()

  else:
    print "run 'joy --gui' to use the GUI\n"
    stack = repl()


'''


References


Wikipedia entry for Joy:
https://en.wikipedia.org/wiki/Joy_%28programming_language%29


Homepage at La Trobe University:
http://www.latrobe.edu.au/humanities/research/research-projects/past-projects/joy-programming-language


'''
