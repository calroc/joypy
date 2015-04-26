# -*- coding: utf-8 -*-
#
#    Copyright  2014, 2015 Simon Forman
#
'''
This is a script to convert a Python module to a markdown file.

Given a module object (not name) print out a Markdown file suitable for
Pandoc processing into a handsome webpage decribing the module.

'''
from inspect import cleandoc
'''
Rather than using Python's built-in and default docstring system, I
have to write my descriptions of the functions as comments above
them.  This way I can extract them using `inspect.getcomments()` and
format them nicely.  I don't want long docstrings in the functions
because then they show up in the syntax-highlighted code in the HTML.
I could strip the docstrings out but then that would mess up the line
numbering.  This way I can have long-winded descriptions in the
comments and tidy docstrings that give "just the facts".


### do_it(lines, out)

Given a name of a module, its source as an enumerated list of lines, and
a file-like object out, write an md file describing the module.

'''
def do_it(lines, out):
  '''
  First, discard any initial comments.
  '''
  for n, line in lines:
    if not line.startswith('#'):
      break

  assert line.startswith("'''"), repr(line)

  '''
  Then run through the rest of the lines, breaking them up into blocks of
  code and (quoted) text.  The code becomes delimited code blocks in the
  markdown and the text is passed through as-is, so it can contain
  arbitrary markdown, uh, markup.
  '''
  while True:
    try:
      print >> out, doc_chunk(lines)
      print >> out
      code_chunk(lines, out)
      print >> out
    except StopIteration:
      break

'''
### code_chunk(lines, out)

Emit lines of code to file(-like object) out as a MD delimited code block.
'''
def code_chunk(lines, out):
  n, line = next(lines)
  print >> out, '~~~~ {.python .numberLines startFrom="%i"}' % (n + 1)
  c = [line]
  for n, line in lines:
    if line.strip() == "'''":
      break
    c.append(line)
  print >> out, '\n'.join(c).rstrip()
  print >> out, '~' * 50


'''
### doc_chunk(lines, out)

Collect and return lines of text as a single chunk of text (a str.)
'''
def doc_chunk(lines):
  c = []
  for n, line in lines:
    if line.strip() == "'''":
      break
    c.append(line)
  return '\n'.join(c).strip()

'''

### clean_comments(comments)

This function takes a block of text of commented-out comments and
strips the comment characters from the front of each line and runs the
result of that through `inspect.cleandoc()`.

'''
def clean_comments(comments):
  c = '\n'.join(line.lstrip('#') for line in comments.splitlines())
  return cleandoc(c)


'''

To demonstrate and test this module, it loads and prints itself.

'''
if __name__ == '__main__':
  import os

  for fn in (
    '__main__.py',
    'btree.py',
    'combinators.py',
    'functions.py',
    'initializer.py',
    'joy.py',
    'library.py',
    'parser.py',
    'stack.py',
    ):
    ifn = os.path.join('joy', fn)
    ofn = os.path.join('html_docs', fn[:-3] + '.md')
    lines = enumerate(open(ifn).read().splitlines())
    try:
      with open(ofn, 'w') as F:
        do_it(lines, F)
    except:
      print ifn
      raise
    else:
      print ofn
    hfn = ofn[:-3] + '.html'
    command = (
      'pandoc %s -o %s '
      #'--standalone '
      '--highlight-style tango') % (
      ofn, hfn
      )
    print os.system(command)
  os.chdir('./html_docs')
  print os.system('./catdocs.sh')
