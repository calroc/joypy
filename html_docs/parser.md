§ Converting text to a joy expression.

This module exports a single function:

  text_to_expression(text, dictionary)

When supplied with a string text and a dictionary BTree (see btree.py)
this function will return a Python datastructure that represents the Joy
datastructure described by the text expression.  Any symbols (pretty much
anything that isn't a number or enclosed in double-quote marks) will be
looked up in the dictionary, a warning will be printed to stdout for any
unfound symbols.

~~~~ {.python .numberLines startFrom="36"}
from __future__ import print_function
from sys import stderr
from re import Scanner
from .btree import get
from .stack import list_to_stack


def convert(token, dictionary):
  '''Look up symbols in the functions dictionary.'''
  try:
    return get(dictionary, token)
  except KeyError:
    print('unknown word', token, file=stderr)
    return token


def text_to_expression(text, dictionary):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert a text to a Joy expression.

~~~~ {.python .numberLines startFrom="56"}
  tokens = _tokenize(text, dictionary)
  expression = _parse(tokens)
  return expression


def _tokenize(text, dictionary):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert a text into a stream of tokens, look up command symbols using
  convert().  Raise ValueError (with some of the failing text) if the
  scan fails.

~~~~ {.python .numberLines startFrom="67"}
  _scanner.dictionary = dictionary
  tokens, rest = _scanner.scan(text)
  if rest:
    raise ValueError(
      'Scan failed at position %i, %r'
      % (len(text) - len(rest), rest[:10])
      )
  return tokens


def _parse(tokens):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Return a stack/list expression of the tokens.

~~~~ {.python .numberLines startFrom="81"}
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


def _scan_identifier(scanner, token): return convert(token, scanner.dictionary)
def _scan_bracket(scanner, token): return token
def _scan_float(scanner, token): return float(token)
def _scan_int(scanner, token): return int(token)
def _scan_str(scanner, token): return token[1:-1].replace('\\"', '"')


_scanner = Scanner([
  (r'-?\d+\.\d*', _scan_float),
  (r'-?\d+', _scan_int),
  (r'[•\w!@$%^&*()_+<>?|\/;:`~,.=-]+', _scan_identifier),
  (r'\[|\]', _scan_bracket),
  (r'"(?:[^"\\]|\\.)*"', _scan_str),
  (r'\s+', None),
  ])
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



