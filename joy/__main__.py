# We run in Python 2 and Python 3
from __future__ import print_function
try:
  input = raw_input
except NameError:
  pass

from sys import argv
from traceback import print_exc

from .joy import joy, run
from library import print_words # Import loads library functions.
from stack import strstack
from initializer import initialize
import combinators # Import loads combinators.
import tracer


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

      if tracer.TRACE: joy.reset()

      try:
        stack = run(text, stack)
      except:
        print_exc()

      if tracer.TRACE: joy.show_trace()

  except:
    print_exc()
  print()
  return stack


initialize()


if '--gui' in argv:
  from gui import main
  t = main()
  print_words(None)
  print()
  print('<STACK')
  t.mainloop()
else:
  stack = repl()

