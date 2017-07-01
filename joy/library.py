# -*- coding: utf-8 -*-
#
#    Copyright © 2014, 2015, 2017 Simon Forman
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
from inspect import getdoc
import operator, math

from .btree import insert, items
from .joy import joy, run
from .parser import text_to_expression, Symbol
from .stack import list_to_stack, iter_stack, pick


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


definitions = '''\
rest == uncons popd
first == uncons pop
second == rest first
third == rest rest first
sum == 0 swap [+] step
product == 1 swap [*] step
swons == swap cons
swoncat == swap concat
shunt == [swons] step
reverse == [] swap shunt
flatten == [] swap [concat] step
unit == [] cons
quoted == [unit] dip
unquoted == [i] dip
enstacken == stack [clear] dip
disenstacken == [truthy] [uncons] while pop
pam == [i] map
run == [] swap infra
sqr == dup mul
size == 0 swap [pop ++] step
average == [sum 1.0 *] [size] cleave /
gcd == [0 >] [dup rollup modulus] while pop
least_fraction == dup [gcd] infra [div] concat map
divisor == popop 2 *
minusb == pop neg
radical == swap dup * rollup * 4 * - sqrt
root1 == + swap /
root2 == - swap /
q0 == [divisor] [minusb] [radical]
q1 == [root1] [root2]
quadratic == [[q0] pam] ternary i [[q1] pam] ternary
*fraction == [uncons] dip uncons [swap] dip concat [*] infra [*] dip cons
*fraction0 == concat [[swap] dip * [*] dip] infra
down_to_zero == [0 >] [dup --] while
range_to_zero == unit [down_to_zero] infra
times == [-- dip] cons [swap] infra [0 >] swap while pop
'''


def add_aliases(D, A=ALIASES):
  for name, aliases in A:
    try:
      F = D[name]
    except KeyError:
      continue
    for alias in aliases:
      D[alias] = F


class FunctionWrapper(object):
  '''
  Allow functions to have a nice repr().
  '''

  def __init__(self, f):
    self.f = f
    self.name = f.__name__.rstrip('_')
    self.__doc__ = f.__doc__ or str(f)

  def __call__(self, stack, expression, dictionary):
    return self.f(stack, expression, dictionary)

  def __repr__(self):
    return self.name


class SimpleFunctionWrapper(FunctionWrapper):

  def __call__(self, stack, expression, dictionary):
    return self.f(stack), expression, dictionary


class BinaryBuiltinWrapper(FunctionWrapper):

  def __call__(self, stack, expression, dictionary):
    (a, (b, stack)) = stack
    result = self.f(b, a)
    return (result, stack), expression, dictionary


class UnaryBuiltinWrapper(FunctionWrapper):

  def __call__(self, stack, expression, dictionary):
    (a, stack) = stack
    result = self.f(a)
    return (result, stack), expression, dictionary


class DefinitionWrapper(FunctionWrapper):
  '''
  Allow functions to have a nice repr().
  '''

  def __init__(self, name, body_text, doc=None):
    self.name = self.__name__ = name
    self.body = text_to_expression(body_text)
    self._body = tuple(iter_stack(self.body))
    self.__doc__ = doc or body_text

  def __call__(self, stack, expression, dictionary):
    expression = list_to_stack(self._body, expression)
##    i = get(dictionary, 'i')
##    expression = self.body, (i, expression)
    return stack, expression, dictionary

  @classmethod
  def parse_definition(class_, defi):
    '''
    Given some text describing a Joy function definition parse it and
    return a DefinitionWrapper.
    '''
    name, proper, body_text = (n.strip() for n in defi.partition('=='))
    if not proper:
      raise ValueError('Definition %r failed' % (defi,))
    return class_(name, body_text)


def generate_definitions(defs, dictionary):
  for definition in defs.splitlines():
    definition = definition.strip()
    if not definition or definition.isspace():
      continue
    F = DefinitionWrapper.parse_definition(definition)
    dictionary[F.name] = F


#
# Functions
#
def first(stack):
  Q, stack = stack
  stack = Q[0], stack
  return stack


def truthy(stack):
  n, stack = stack
  return bool(n), stack


def getitem(stack):
  n, (Q, stack) = stack
  return pick(Q, n), stack


def min_(S):
  '''
  Given a list find the minimum.
  '''
  tos, stack = S
  return min(iter_stack(tos)), stack


def sum_(S):
  tos, stack = S
  return sum(iter_stack(tos)), stack


def remove(S):
  (tos, (second, stack)) = S
  l = list(iter_stack(second))
  l.remove(tos)
  return list_to_stack(l), stack


def cons(S):
  '''
  The cons operator expects a list on top of the stack and the potential
  member below. The effect is to add the potential member into the
  aggregate.
  '''
  (tos, (second, stack)) = S
  return (second, tos), stack


def uncons(S):
  '''
  Inverse of cons, removes an item from the top of the list on the stack
  and places it under the remaining list.
  '''
  (tos, stack) = S
  item, tos = tos
  return tos, (item, stack)


def clear(stack):
  '''Clear everything from the stack.'''
  return ()


def dup(S):
  '''Duplicate the top item on the stack.'''
  (tos, stack) = S
  return tos, (tos, stack)


def swap(S):
  '''Swap the top two items on stack.'''
  (tos, (second, stack)) = S
  return second, (tos, stack)


def stack_(stack):
  '''
  The stack operator pushes onto the stack a list containing all the
  elements of the stack.
  '''
  return stack, stack


def unstack(S):
  '''
  The unstack operator expects a list on top of the stack and makes that
  the stack discarding the rest of the stack.
  '''
  (tos, stack) = S
  return tos


def pop(S):
  '''Pop and discard the top item from the stack.'''
  (tos, stack) = S
  return stack


def popd(S):
  '''Pop and discard the second item from the stack.'''
  (tos, (second, stack)) = S
  return tos, stack


def popop(S):
  '''Pop and discard the first and second items from the stack.'''
  (tos, (second, stack)) = S
  return stack


def dupd(S):
  '''Duplicate the second item on the stack.'''
  (tos, (second, stack)) = S
  return tos, (second, (second, stack))


def reverse(S):
  '''Reverse the list on the top of the stack.'''
  (tos, stack) = S
  res = ()
  for term in iter_stack(tos):
    res = term, res
  return res, stack


def concat(S):
  '''Concatinate the two lists on the top of the stack.'''
  (tos, (second, stack)) = S
  for term in reversed(list(iter_stack(second))):
    tos = term, tos
  return tos, stack


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


def succ(S):
  '''Increment TOS.'''
  (tos, stack) = S
  return tos + 1, stack


def pred(S):
  '''Decrement TOS.'''
  (tos, stack) = S
  return tos - 1, stack


def rollup(S):
  '''a b c -> b c a'''
  (a, (b, (c, stack))) = S
  return b, (c, (a, stack))


def rolldown(S):
  '''a b c -> c a b'''
  (a, (b, (c, stack))) = S
  return c, (a, (b, stack))


def execute(S):
  (text, stack) = S
  if isinstance(text, str):
    return run(text, stack)
  return stack


def id_(stack):
  return stack


def void(stack):
  form, stack = stack
  return _void(form), stack


def _void(form):
  return any(not _void(i) for i in iter_stack(form))


##
##def first(((head, tail), stack)):
##  return head, stack


##
##def rest(((head, tail), stack)):
##  return tail, stack


##  flatten
##  transpose
##  sign
##  at
##  of
##  drop
##  take


def print_words(stack, expression, dictionary):
  '''Print all the words in alphabetical order.'''
  print(' '.join(name for name, f in dictionary.items()))
  return stack, expression, dictionary


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


def help_(S):
  '''Accepts a quoted word on the top of the stack and prints its docs.'''
  (quote, stack) = S
  word = quote[0]
  print(getdoc(word))
  return stack


#
# § Combinators
#


S_i = Symbol('i')
S_swaack = Symbol('swaack')
S_i = Symbol('i')
S_infra = Symbol('infra')
S_first = Symbol('first')
S_truthy = Symbol('truthy')
S_getitem = Symbol('getitem')


def i(stack, expression, dictionary):
  (quote, stack) = stack
  accumulator = list(iter_stack(quote))
  expression = list_to_stack(accumulator, expression)
  return stack, expression, dictionary


def x(stack, expression, dictionary):
  '''
  x == dup i

  ... [Q] x = ... [Q] dup i
  ... [Q] x = ... [Q] [Q] i
  ... [Q] x = ... [Q]  Q

  '''
  quote = stack[0]
  expression = (S_i, (quote, expression))
  return stack, expression, dictionary


def b(stack, expression, dictionary):
  '''
  b == [i] dip i

  ... [P] [Q] b == ... [P] i [Q] i
  ... [P] [Q] b == ... P Q

  '''
  (q, (p, (stack))) = stack
  expression = (p, (S_i, (q, (S_i, expression))))
  return stack, expression, dictionary


def infra(stack, expression, dictionary):
  '''
  Accept a quoted program and a list on the stack and run the program
  with the list as its stack.
  '''
  (quote, (aggregate, stack)) = stack
  Q = (S_i, (stack, (S_swaack, expression)))
  return (quote, aggregate), Q, dictionary


def swaack(stack, expression, dictionary):
  old_stack, stack = stack
  stack = stack, old_stack
  return stack, expression, dictionary


def map_(S, expression, dictionary):
  '''
  Run the quoted program on TOS on the items in the list under it, push a
  new list with the results (in place of the program and original list.
  '''
  (quote, (aggregate, stack)) = S
  results = list_to_stack([
    joy((term, stack), quote, dictionary)[0][0]
    for term in iter_stack(aggregate)
    ])
  return (results, stack), expression, dictionary


def cleave(S, expression, dictionary):
  '''
  The cleave combinator expects two quotations, and below that an item X.
  It first executes [P], with X on top, and saves the top result element.
  Then it executes [Q], again with X, and saves the top result.
  Finally it restores the stack to what it was below X and pushes the two
  results P(X) and Q(X).
  '''
  (Q, (P, (x, stack))) = S
  p = joy((x, stack), P, dictionary)[0][0]
  q = joy((x, stack), Q, dictionary)[0][0]
  return (q, (p, stack)), expression, dictionary


def ifte(stack, expression, dictionary):
  (else_, (then, (if_, stack))) = stack
  expression = (
    (else_, (then, ())),
    (stack, (if_,
             (S_infra, (S_first, (S_truthy, (S_getitem, (S_i, expression))))))))
  return stack, expression, dictionary


def dip(stack, expression, dictionary):
  (quote, (x, stack)) = stack
  stack = (quote, stack)
  expression = S_i, (x, expression)
  return stack, expression, dictionary


def dipd(S, expression, dictionary):
  '''Like dip but expects two items.'''
  (quote, (x, (y, stack))) = S
  stack = joy(stack, quote, dictionary)[0]
  return (x, (y, stack)), expression, dictionary


def dipdd(S, expression, dictionary):
  '''Like dip but expects three items.'''
  (quote, (x, (y, (z, stack)))) = S
  stack = joy(stack, quote, dictionary)[0]
  return (x, (y, (z, stack))), expression, dictionary


def app1(S, expression, dictionary):
  '''
  Given a quoted program on TOS and anything as the second stack item run
  the program and replace the two args with the first result of the
  program.
  '''
  (quote, (x, stack)) = S
  result = joy((x, stack), quote, dictionary)[0]
  return (result[0], stack), expression, dictionary


def app2(S, expression, dictionary):
  '''Like app1 with two items.'''
  (quote, (x, (y, stack))) = S
  resultx = joy((x, stack), quote, dictionary)[0][0]
  resulty = joy((y, stack), quote, dictionary)[0][0]
  return (resultx, (resulty, stack)), expression, dictionary


def app3(S, expression, dictionary):
  '''Like app1 with three items.'''
  (quote, (x, (y, (z, stack)))) = S
  resultx = joy((x, stack), quote, dictionary)[0][0]
  resulty = joy((y, stack), quote, dictionary)[0][0]
  resultz = joy((z, stack), quote, dictionary)[0][0]
  return (resultx, (resulty, (resultz, stack))), expression, dictionary


def step(S, expression, dictionary):
  '''
  The step combinator removes the aggregate and the quotation, and then
  repeatedly puts the members of the aggregate on top of the remaining
  stack and executes the quotation.
  '''
  (quote, (aggregate, stack)) = S
  for term in iter_stack(aggregate):
    stack = joy((term, stack), quote, dictionary)[0]
  return stack, expression, dictionary


def while_(S, expression, dictionary):
  '''[if] [body] while'''
  (body, (if_, stack)) = S
  while joy(stack, if_, dictionary)[0][0]:
    stack = joy(stack, body, dictionary)[0]
  return stack, expression, dictionary


def nullary(S, expression, dictionary):
  '''
  Run the program on TOS and return its first result without consuming
  any of the stack (except the program on TOS.)
  '''
  (quote, stack) = S
  result = joy(stack, quote, dictionary)
  return (result[0][0], stack), expression, dictionary


def unary(S, expression, dictionary):
  (quote, stack) = S
  _, return_stack = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary


def binary(S, expression, dictionary):
  (quote, stack) = S
  _, (_, return_stack) = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary


def ternary(S, expression, dictionary):
  (quote, stack) = S
  _, (_, (_, return_stack)) = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary


builtins = (
  BinaryBuiltinWrapper(operator.add),
  BinaryBuiltinWrapper(operator.and_),
  BinaryBuiltinWrapper(operator.div),
  BinaryBuiltinWrapper(operator.eq),
  BinaryBuiltinWrapper(operator.floordiv),
  BinaryBuiltinWrapper(operator.ge),
  BinaryBuiltinWrapper(operator.gt),
  BinaryBuiltinWrapper(operator.le),
  BinaryBuiltinWrapper(operator.lshift),
  BinaryBuiltinWrapper(operator.lt),
  BinaryBuiltinWrapper(operator.mod),
  BinaryBuiltinWrapper(operator.mul),
  BinaryBuiltinWrapper(operator.ne),
  BinaryBuiltinWrapper(operator.or_),
  BinaryBuiltinWrapper(operator.pow),
  BinaryBuiltinWrapper(operator.rshift),
  BinaryBuiltinWrapper(operator.sub),
  BinaryBuiltinWrapper(operator.truediv),
  BinaryBuiltinWrapper(operator.xor),

  UnaryBuiltinWrapper(operator.neg),
  UnaryBuiltinWrapper(operator.not_),
  UnaryBuiltinWrapper(math.sqrt),
  )


combinators = (
  FunctionWrapper(app1),
  FunctionWrapper(app2),
  FunctionWrapper(app3),
  FunctionWrapper(b),
  FunctionWrapper(binary),
  FunctionWrapper(cleave),
  FunctionWrapper(dip),
  FunctionWrapper(dipd),
  FunctionWrapper(dipdd),
  FunctionWrapper(i),
  FunctionWrapper(ifte),
  FunctionWrapper(infra),
  FunctionWrapper(map_),
  FunctionWrapper(nullary),
  FunctionWrapper(step),
  FunctionWrapper(swaack),
  FunctionWrapper(ternary),
  FunctionWrapper(unary),
  FunctionWrapper(while_),
  FunctionWrapper(x),
  FunctionWrapper(print_words),
  )


primitives = (
  SimpleFunctionWrapper(first),
  SimpleFunctionWrapper(truthy),
  SimpleFunctionWrapper(getitem),
  SimpleFunctionWrapper(unstack),
  SimpleFunctionWrapper(clear),
  SimpleFunctionWrapper(concat),
  SimpleFunctionWrapper(cons),
  SimpleFunctionWrapper(dup),
  SimpleFunctionWrapper(dupd),
  SimpleFunctionWrapper(id_),
  SimpleFunctionWrapper(min_),
  SimpleFunctionWrapper(pop),
  SimpleFunctionWrapper(popd),
  SimpleFunctionWrapper(popop),
  SimpleFunctionWrapper(pred),
  SimpleFunctionWrapper(remove),
  SimpleFunctionWrapper(reverse),
  SimpleFunctionWrapper(rolldown),
  SimpleFunctionWrapper(rollup),
  SimpleFunctionWrapper(stack_),
  SimpleFunctionWrapper(succ),
  SimpleFunctionWrapper(sum_),
  SimpleFunctionWrapper(swap),
  SimpleFunctionWrapper(uncons),
  SimpleFunctionWrapper(unstack),
  SimpleFunctionWrapper(void),
  SimpleFunctionWrapper(zip_),
  )


def initialize(dictionary=None):
  if dictionary is None:
    dictionary = {}
  dictionary.update((F.name, F) for F in builtins)
  dictionary.update((F.name, F) for F in combinators)
  dictionary.update((F.name, F) for F in primitives)
  add_aliases(dictionary)
  return dictionary
