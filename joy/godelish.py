# -*- coding: utf-8 -*-
from __future__ import print_function
from .parser import text_to_expression
from .stack import strstack, iter_stack, list_to_stack
from .library import dup, unstack


class Wrapper(object):
  def __init__(self, f):
    self.f = f
    self.name = f.__name__.rstrip('_')
    self.__doc__ = f.__doc__ or str(f)
  def __call__(self, stack, continuation, dictionary):
    return self.f(stack, continuation, dictionary)
  def __repr__(self):
    return self.name


class SimpleFunctionWrapper(Wrapper):
  def __call__(self, stack, continuation, dictionary):
    return self.f(stack), continuation, dictionary


@Wrapper
def dip(stack, continuation, dictionary):
  (quote, (x, stack)) = stack
  continuation = i, (x, continuation)
  return (quote, stack), continuation, dictionary


@Wrapper
def i(stack, continuation, dictionary):
  (quote, stack) = stack
  accumulator = list(iter_stack(quote))
  continuation = list_to_stack(accumulator, continuation)
  return stack, continuation, dictionary


@Wrapper
def x(stack, continuation, dictionary):
  '''
  x == dup i

  ... [Q] x = ... [Q] dup i
  ... [Q] x = ... [Q] [Q] i
  ... [Q] x = ... [Q] [Q] i
  ... [Q] x = ... [Q]  Q

  '''
  quote = stack[0]
  accumulator = list(iter_stack(quote))
  continuation = list_to_stack(accumulator, continuation)
  return stack, continuation, dictionary


@Wrapper
def b(stack, continuation, dictionary):
  (q, (p, (stack))) = stack
  continuation = (p, (i, (q, (i, continuation))))
  return stack, continuation, dictionary


@Wrapper
def infra(stack, continuation, dictionary):
  '''
  Accept a quoted program and a list on the stack and run the program
  with the list as its stack.
  '''
  (quote, (aggregate, stack)) = stack
  Q = (i, (stack, (swaack, continuation)))
  return (quote, aggregate), Q, dictionary


@Wrapper
def swaack(stack, continuation, dictionary):
  old_stack, stack = stack
  stack = stack, old_stack
  return stack, continuation, dictionary


@SimpleFunctionWrapper
def first(stack):
  Q, stack = stack
  stack = Q[0], stack
  return stack


@SimpleFunctionWrapper
def truthy(stack):
  n, stack = stack
  return bool(n), stack


@SimpleFunctionWrapper
def getitem(stack):
  n, (Q, stack) = stack
  return pick(Q, n), stack


unstack = SimpleFunctionWrapper(unstack)


@Wrapper
def ifte(stack, continuation, dictionary):
  (else_, (then, (if_, stack))) = stack
  ii = (( (stack, (else_, (infra, ()))) , (
      (stack, (then,  (infra, ()))) , ())), ())
  stack = (if_, (stack, ii))
  continuation = (infra, (first, (truthy, (getitem, (i, (unstack, ()))))))
  return stack, continuation, dictionary


def J(stack, continuation, dictionary):
  while continuation:
    print_trace(stack, continuation)
    term, continuation = continuation
    if callable(term):
      stack, continuation, dictionary = term(stack, continuation, dictionary)
    else:
      stack = term, stack
  return stack, continuation, dictionary


def print_trace(stack, expression):
  stack = list(iter_stack(stack))
  stack.reverse()
  print(strstack(list_to_stack(stack)), '.', strstack(expression))


def pick(s, n):
  '''
  Find the nth item on the stack. (Pick with zero is the same as "dup".)
  '''
  if n < 0:
    raise ValueError
  while True:
    try:
      item, s = s
    except ValueError:
      raise IndexError
    n -= 1
    if n < 0:
      break
  return item





##U = '''[[["..."]["then"]"infra"]
##       [["..."]["else"]"infra"]]
##      ["..."] ["if"] "infra" "first" "truthy" "getitem" "i" "i" '''
##
##print(text_to_expression(U))







##def runit(C):
###  C = [(E, s)]
##
##  while True:
##
##    E, s = C.pop()
##    if not E:
##      return s
##
##    term, E = E
##    if not callable(term):
##      s = term, s
##      C.append((E, s))
##      continue
##
##    C.append((E, s))
##    C = term(C)
##  return C



##    def f(res):
##      return J(E, res)
##    expr, stack, continuation = term(s, f)
##    return continuation(J(expr, stack))

##def P(stack):
##  print 'P', stack
##  return stack


##def dip(S, cont):
##  '''
##  dip expects a program [P] and below that another item X. It pops both,
##  saves X, executes P and then restores X.
##  '''
##  (quote, (x, stack)) = S
##  return quote, stack, lambda s: cont((x, s))

##def dip(C):
##  E, s = C.pop()
##  (quote, (x, stack)) = s
##
##  def f(C):
##    E, s = C.pop()
##    s = x, s
##    C.append((E, s))
##    return C
##
##  C.append((quote, stack))
##
##  C.append(((f, E), stack))
##  return C


