# Joypy

## A dialect of Joy in Python.

Joy is a programming language created by Manfred von Thun that is easy to
use and understand and has many other nice properties.  This Python script
is an interpreter for a dialect of Joy that attempts to stay very close
to the spirit of Joy but does not precisely match the behaviour of the
original version(s) written in C.  A Tkinter GUI is provided as well.

~~~~ {.python .numberLines startFrom="33"}
from __future__ import print_function
try:
  input = raw_input
except NameError:
  pass
from traceback import print_exc
from .parser import text_to_expression
from .stack import strstack, iter_stack, list_to_stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## print_trace()

Write out a string representation of the stack and expression to stdout.

~~~~ {.python .numberLines startFrom="47"}
def print_trace(stack, expression):
  stack = list(iter_stack(stack))
  stack.reverse()
  print(strstack(list_to_stack(stack)), '.', strstack(expression))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## § joy()

The basic joy() function is quite straightforward.  It iterates through a
sequence of terms which are either literals (strings, numbers, sequences)
or functions.  Literals are put onto the stack and functions are
executed.

Every Joy function is an unary mapping from stacks to stacks.  Even
literals are considered to be functions that accept a stack and return a
new stack with the literal value on top.

~~~~ {.python .numberLines startFrom="66"}
def joy(stack, expression, dictionary, viewer=print_trace):
  while expression:
    viewer(stack, expression)
    term, expression = expression
    if callable(term):
      stack, expression, dictionary = term(stack, expression, dictionary)
    else:
      stack = term, stack
  viewer(stack, expression)
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## run()

Return the stack resulting from running the Joy code text on the stack.

~~~~ {.python .numberLines startFrom="83"}
def run(text, stack, dictionary):
  expression = text_to_expression(text, dictionary)
  return joy(stack, expression, dictionary)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## repl() 

### Read-Evaluate-Print Loop

Accept input and run it on the stack, loop.

~~~~ {.python .numberLines startFrom="95"}
def repl(stack=(), dictionary=()):
  try:
    while True:
      print()
      print('->', strstack(stack))
      print()
      try:
        text = input('joy? ')
      except (EOFError, KeyboardInterrupt):
        break
      try:
        stack, _, dictionary = run(text, stack, dictionary)
      except:
        print_exc()
  except:
    print_exc()
  print()
  return stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



