# -*- coding: utf-8 -*-
#
#    Copyright © 2014, 2015 Simon Forman
#
#    This file is part of joy.py
#
#    joy.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    joy.py is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with joy.py.  If not see <http://www.gnu.org/licenses/>.
#
'''


§ Converting text to a joy expression.

  parse()
  tokenize()
  convert()


'''
from re import Scanner

from .stack import list_to_stack
from .functions import convert


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


def text_to_expression(text):
  '''
  Convert a text to a Joy expression.
  '''
  tokens = tokenize(text)
  expression = parse(tokens)
  return expression
