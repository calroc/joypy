from __future__ import print_function
from sys import argv
from .joy import repl
from .initializer import initialize


if '--gui' in argv:
  from .gui.textwidget import main
  t = main(dictionary=initialize())
  print()
  print('<STACK')
  t.mainloop()
else:
  stack = repl(dictionary=initialize())
