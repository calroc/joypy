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

from .parser import text_to_expression, Symbol
from .utils.stack import list_to_stack, iter_stack, pick, pushback


ALIASES = (
  ('add', ['+']),
  ('and', ['&']),
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
  )


definitions = ('''\
second == rest first
third == rest rest first
sum == 0 swap [+] step
product == 1 swap [*] step
swons == swap cons
swoncat == swap concat
reverse == [] swap shunt
flatten == [] swap [concat] step
unit == [] cons
quoted == [unit] dip
unquoted == [i] dip
enstacken == stack [clear] dip
disenstacken == ? [uncons ?] loop pop
? == dup truthy
dinfrirst == dip infra first
nullary == [stack] dinfrirst
unary == [stack [pop] dip] dinfrirst
binary == [stack [popop] dip] dinfrirst
ternary == [stack [popop pop] dip] dinfrirst
pam == [i] map
run == [] swap infra
sqr == dup mul
size == 0 swap [pop ++] step
cleave == [i] app2 [popd] dip
branch == roll< choice i
average == [sum 1.0 *] [size] cleave /
gcd == 1 [tuck modulus dup 0 >] loop pop
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
anamorphism == [pop []] swap [dip swons] genrec
range == [0 <=] [1 - dup] anamorphism
while == swap [nullary] cons dup dipd concat loop
dudipd == dup dipd
primrec == [i] genrec
z-down == [] swap uncons swap
z-up == swons swap shunt
z-right == [swons] cons dip uncons swap
z-left == swons [uncons swap] dip swap
'''

# Project Euler
'''\
PE1.1 == + dup [+] dip
PE1.2 == dup [3 & PE1.1] dip 2 >>
PE1.3 == 14811 swap [PE1.2] times pop
PE1 == 0 0 66 [7 PE1.3] times 4 PE1.3 pop
'''
#PE1.2 == [PE1.1] step
#PE1 == 0 0 66 [[3 2 1 3 1 2 3] PE1.2] times [3 2 1 3] PE1.2 pop
)



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


def add_definitions(defs, dictionary):
  for definition in defs.splitlines():
    definition = definition.strip()
    if not definition or definition.isspace():
      continue
    F = DefinitionWrapper.parse_definition(definition)
    dictionary[F.name] = F


#
# Functions
#


def parse((text, stack)):
  expression = text_to_expression(text)
  return expression, stack


def first(stack):
  '''first == uncons pop'''
  Q, stack = stack
  stack = Q[0], stack
  return stack


def rest(((head, tail), stack)):
  '''rest == uncons popd'''
  return tail, stack


def truthy(stack):
  n, stack = stack
  return bool(n), stack


def getitem(stack):
  n, (Q, stack) = stack
  return pick(Q, n), stack


def choice(stack):
  '''
  Use a Boolean value to select one of two items.

        A B False choice
     ----------------------
               A


        A B True choice
     ---------------------
               B

  Currently Python semantics are used to evaluate the "truthiness" of the
  Boolean value (so empty string, zero, etc. are counted as false, etc.)
  '''
  (if_, (then, (else_, stack))) = stack
  return then if if_ else else_, stack


def select(stack):
  '''
  Use a Boolean value to select one of two items from a sequence.

        [A B] False select
     ------------------------
                A


        [A B] True select
     -----------------------
               B

  The sequence can contain more than two items but not fewer.
  Currently Python semantics are used to evaluate the "truthiness" of the
  Boolean value (so empty string, zero, etc. are counted as false, etc.)
  '''
  (flag, (choices, stack)) = stack
  (else_, (then, _)) = choices
  return then if flag else else_, stack


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
  '''Clear everything from the stack.

     ... clear
  ---------------

  '''
  return ()


def dup(S):
  '''Duplicate the top item on the stack.'''
  (tos, stack) = S
  return tos, (tos, stack)


def over(S):
  '''
  Copy the second item down on the stack to the top of the stack.

     a b over
  --------------
      a b a

  '''
  second = S[1][0]
  return second, S


def tuck(S):
  '''
  Copy the item at TOS under the second item of the stack.

     a b tuck
  --------------
      b a b

  '''
  (tos, (second, stack)) = S
  return tos, (second, (tos, stack))


def swap(S):
  '''Swap the top two items on stack.'''
  (tos, (second, stack)) = S
  return second, (tos, stack)


def swaack(stack):
  old_stack, stack = stack
  return stack, old_stack


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


def shunt((tos, (second, stack))):
  '''
  shunt == [swons] step

  Like concat but reverses the top list into the second.
  '''
  while tos:
    term, tos = tos
    second = term, second
  return second, stack


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


#def execute(S):
#  (text, stack) = S
#  if isinstance(text, str):
#    return run(text, stack)
#  return stack


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



##  flatten
##  transpose
##  sign
##  at
##  of
##  drop
##  take


def print_words(stack, expression, dictionary):
  '''Print all the words in alphabetical order.'''
  print(' '.join(sorted(dictionary)))
  return stack, expression, dictionary


# def simple_manual(stack):
#   '''
#   Print words and help for each word.
#   '''
#   for name, f in sorted(FUNCTIONS.items()):
#     d = getdoc(f)
#     boxline = '+%s+' % ('-' * (len(name) + 2))
#     print('\n'.join((
#       boxline,
#       '| %s |' % (name,),
#       boxline,
#       d if d else '   ...',
#       '',
#       '--' * 40,
#       '',
#       )))
#   return stack


def help_(S, expression, dictionary):
  '''Accepts a quoted symbol on the top of the stack and prints its docs.'''
  ((symbol, _), stack) = S
  word = dictionary[symbol]
  print(getdoc(word))
  return stack, expression, dictionary


#
# § Combinators
#


# Several combinators depend on other words in their definitions,
# we use symbols to prevent hard-coding these, so in theory, you
# could change the word in the dictionary to use different semantics.
S_choice = Symbol('choice')
S_first = Symbol('first')
S_getitem = Symbol('getitem')
S_genrec = Symbol('genrec')
S_loop = Symbol('loop')
S_i = Symbol('i')
S_ifte = Symbol('ifte')
S_infra = Symbol('infra')
S_step = Symbol('step')
S_times = Symbol('times')
S_swaack = Symbol('swaack')
S_truthy = Symbol('truthy')


def i(stack, expression, dictionary):
  quote, stack = stack
  return stack, pushback(quote, expression), dictionary


def x(stack, expression, dictionary):
  '''
  x == dup i

  ... [Q] x = ... [Q] dup i
  ... [Q] x = ... [Q] [Q] i
  ... [Q] x = ... [Q]  Q

  '''
  quote, _ = stack
  return stack, pushback(quote, expression), dictionary


def b(stack, expression, dictionary):
  '''
  b == [i] dip i

  ... [P] [Q] b == ... [P] i [Q] i
  ... [P] [Q] b == ... P Q

  '''
  q, (p, (stack)) = stack
  return stack, pushback(p, pushback(q, expression)), dictionary


def infra(stack, expression, dictionary):
  '''
  Accept a quoted program and a list on the stack and run the program
  with the list as its stack.

     ... [a b c] [Q] . infra
  -----------------------------
     c b a . Q [...] swaack

  '''
  (quote, (aggregate, stack)) = stack
  return aggregate, pushback(quote, (stack, (S_swaack, expression))), dictionary


def genrec(stack, expression, dictionary):
  '''
  General Recursion Combinator.

                          [if] [then] [rec1] [rec2] genrec
    ---------------------------------------------------------------------
       [if] [then] [rec1 [[if] [then] [rec1] [rec2] genrec] rec2] ifte

  From "Recursion Theory and Joy" (j05cmp.html) by Manfred von Thun:
  "The genrec combinator takes four program parameters in addition to
  whatever data parameters it needs. Fourth from the top is an if-part,
  followed by a then-part. If the if-part yields true, then the then-part
  is executed and the combinator terminates. The other two parameters are
  the rec1-part and the rec2-part. If the if-part yields false, the
  rec1-part is executed. Following that the four program parameters and
  the combinator are again pushed onto the stack bundled up in a quoted
  form. Then the rec2-part is executed, where it will find the bundled
  form. Typically it will then execute the bundled form, either with i or
  with app2, or some other combinator."

  The way to design one of these is to fix your base case [then] and the
  test [if], and then treat rec1 and rec2 as an else-part "sandwiching"
  a quotation of the whole function.

  For example, given a (general recursive) function 'F':

      F == [I] [T] [R1] [R2] genrec

  If the [I] if-part fails you must derive R1 and R2 from:

      ... R1 [F] R2

  Just set the stack arguments in front, and figure out what R1 and R2
  have to do to apply the quoted [F] in the proper way.  In effect, the
  genrec combinator turns into an ifte combinator with a quoted copy of
  the original definition in the else-part:

      F == [I] [T] [R1]   [R2] genrec
        == [I] [T] [R1 [F] R2] ifte

  (Primitive recursive functions are those where R2 == i.

      P == [I] [T] [R] primrec
        == [I] [T] [R [P] i] ifte
        == [I] [T] [R P] ifte
  )
  '''
  (rec2, (rec1, T)) = stack
  (then, (if_, _)) = T
  Q = ((if_, (then, (rec1, (rec2, (S_genrec, ()))))), rec2)
  for term in reversed(list(iter_stack(rec1))):
    Q = term, Q
  expression = (S_ifte, expression)
  return (Q, T), expression, dictionary


def map_(S, expression, dictionary):
  '''
  Run the quoted program on TOS on the items in the list under it, push a
  new list with the results (in place of the program and original list.
  '''
#  (quote, (aggregate, stack)) = S
#  results = list_to_stack([
#    joy((term, stack), quote, dictionary)[0][0]
#    for term in iter_stack(aggregate)
#    ])
#  return (results, stack), expression, dictionary
  (quote, (aggregate, stack)) = S
  if not aggregate:
    return (aggregate, stack), expression, dictionary
  batch = ()
  for term in iter_stack(aggregate):
    s = term, stack
    batch = (s, (quote, (S_infra, (S_first, batch))))
  stack = (batch, ((), stack))
  return stack, (S_infra, expression), dictionary


#def cleave(S, expression, dictionary):
#  '''
#  The cleave combinator expects two quotations, and below that an item X.
#  It first executes [P], with X on top, and saves the top result element.
#  Then it executes [Q], again with X, and saves the top result.
#  Finally it restores the stack to what it was below X and pushes the two
#  results P(X) and Q(X).
#  '''
#  (Q, (P, (x, stack))) = S
#  p = joy((x, stack), P, dictionary)[0][0]
#  q = joy((x, stack), Q, dictionary)[0][0]
#  return (q, (p, stack)), expression, dictionary


def ifte(stack, expression, dictionary):
  '''
  If-Then-Else Combinator

                  ... [if] [then] [else] ifte
       ---------------------------------------------------
          ... [[else] [then]] [...] [if] infra select i




                ... [if] [then] [else] ifte
       -------------------------------------------------------
          ... [else] [then] [...] [if] infra first choice i


  Has the effect of grabbing a copy of the stack on which to run the
  if-part using infra.
  '''
  (else_, (then, (if_, stack))) = stack
  expression = (S_infra, (S_first, (S_choice, (S_i, expression))))
  stack = (if_, (stack, (then, (else_, stack))))
  return stack, expression, dictionary


def dip(stack, expression, dictionary):
  (quote, (x, stack)) = stack
  stack = (quote, stack)
  expression = S_i, (x, expression)
  return stack, expression, dictionary


def dipd(S, expression, dictionary):
  '''Like dip but expects two items.'''
  (quote, (x, (y, stack))) = S
  stack = (quote, stack)
  expression = S_i, (y, (x, expression))
  return stack, expression, dictionary


def dipdd(S, expression, dictionary):
  '''Like dip but expects three items.'''
  (quote, (x, (y, (z, stack)))) = S
  stack = (quote, stack)
  expression = S_i, (z, (y, (x, expression)))
  return stack, expression, dictionary


def app1(S, expression, dictionary):
  '''
  Given a quoted program on TOS and anything as the second stack item run
  the program and replace the two args with the first result of the
  program.

              ... x [Q] . app1
     -----------------------------------
        ... [x ...] [Q] . infra first
  '''
  (quote, (x, stack)) = S
  stack = (quote, ((x, stack), stack))
  expression = (S_infra, (S_first, expression))
  return stack, expression, dictionary


def app2(S, expression, dictionary):
  '''Like app1 with two items.

            ... y x [Q] . app2
     -----------------------------------
        ... [y ...] [Q] . infra first
            [x ...] [Q]   infra first
'''
  (quote, (x, (y, stack))) = S
  expression = (S_infra, (S_first,
    ((x, stack), (quote, (S_infra, (S_first,
      expression))))))
  stack = (quote, ((y, stack), stack))
  return stack, expression, dictionary


def app3(S, expression, dictionary):
  '''Like app1 with three items.

            ... z y x [Q] . app3
     -----------------------------------
        ... [z ...] [Q] . infra first
            [y ...] [Q]   infra first
            [x ...] [Q]   infra first
'''
  (quote, (x, (y, (z, stack)))) = S
  expression = (S_infra, (S_first,
    ((y, stack), (quote, (S_infra, (S_first,
    ((x, stack), (quote, (S_infra, (S_first,
      expression))))))))))
  stack = (quote, ((z, stack), stack))
  return stack, expression, dictionary


def step(S, expression, dictionary):
  '''
  Run a quoted program on each item in a sequence.

          ... [] [Q] . step
       -----------------------
                 ... .


         ... [a] [Q] . step
      ------------------------
               ... a . Q


     ... [a b c] [Q] . step
  ----------------------------------------
               ... a . Q [b c] [Q] step

  The step combinator removes the aggregate and the quotation, and then
  repeatedly puts the members of the aggregate on top of the remaining
  stack and executes the quotation.
  '''
  (quote, (aggregate, stack)) = S
  if not aggregate:
    return stack, expression, dictionary
  head, tail = aggregate
  stack = quote, (head, stack)
  if tail:
    expression = tail, (quote, (S_step, expression))
  expression = S_i, expression
  return stack, expression, dictionary


def times(stack, expression, dictionary):
  '''
  times == [-- dip] cons [swap] infra [0 >] swap while pop

     ... n [Q] . times
  ---------------------  w/ n <= 0
           ... .


     ... 1 [Q] . times
  ---------------------------------
           ... . Q


     ... n [Q] . times
  ---------------------------------  w/ n > 1
           ... . Q (n - 1) [Q] times

  '''
  # times == [-- dip] cons [swap] infra [0 >] swap while pop
  (quote, (n, stack)) = stack
  if n <= 0:
    return stack, expression, dictionary
  stack = quote, stack
  n -= 1
  if n:
    expression = n, (quote, (S_times, expression))
  expression = S_i, expression
  return stack, expression, dictionary


# The current definition above works like this:

#             [P] [Q] while
# --------------------------------------
#    [P] nullary [Q [P] nullary] loop

#   while == [pop i not] [popop] [dudipd] primrec

#def while_(S, expression, dictionary):
#  '''[if] [body] while'''
#  (body, (if_, stack)) = S
#  while joy(stack, if_, dictionary)[0][0]:
#    stack = joy(stack, body, dictionary)[0]
#  return stack, expression, dictionary





def loop(stack, expression, dictionary):
  '''
  Basic loop combinator.

     ... True [Q] loop
  -----------------------
       ... Q [Q] loop

     ... False [Q] loop
  ------------------------
            ...

  '''
  quote, (flag, stack) = stack
  if flag:
    stack = quote, stack
    expression = S_i, (quote, (S_loop, expression))
  return stack, expression, dictionary

#def nullary(S, expression, dictionary):
#  '''
#  Run the program on TOS and return its first result without consuming
#  any of the stack (except the program on TOS.)
#  '''
#  (quote, stack) = S
#  result = joy(stack, quote, dictionary)
#  return (result[0][0], stack), expression, dictionary
#
#
#def unary(S, expression, dictionary):
#  (quote, stack) = S
#  _, return_stack = stack
#  result = joy(stack, quote, dictionary)[0]
#  return (result[0], return_stack), expression, dictionary
#
#
#def binary(S, expression, dictionary):
#  (quote, stack) = S
#  _, (_, return_stack) = stack
#  result = joy(stack, quote, dictionary)[0]
#  return (result[0], return_stack), expression, dictionary
#
#
#def ternary(S, expression, dictionary):
#  (quote, stack) = S
#  _, (_, (_, return_stack)) = stack
#  result = joy(stack, quote, dictionary)[0]
#  return (result[0], return_stack), expression, dictionary


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
#  FunctionWrapper(binary),
#  FunctionWrapper(cleave),
  FunctionWrapper(dip),
  FunctionWrapper(dipd),
  FunctionWrapper(dipdd),
  FunctionWrapper(genrec),
  FunctionWrapper(help_),
  FunctionWrapper(i),
  FunctionWrapper(ifte),
  FunctionWrapper(infra),
  FunctionWrapper(loop),
  FunctionWrapper(map_),
#  FunctionWrapper(nullary),
  FunctionWrapper(print_words),
  FunctionWrapper(step),
  FunctionWrapper(times),
#  FunctionWrapper(ternary),
#  FunctionWrapper(unary),
#  FunctionWrapper(while_),
  FunctionWrapper(x),
  )


primitives = (
  SimpleFunctionWrapper(choice),
  SimpleFunctionWrapper(clear),
  SimpleFunctionWrapper(concat),
  SimpleFunctionWrapper(cons),
  SimpleFunctionWrapper(dup),
  SimpleFunctionWrapper(dupd),
  SimpleFunctionWrapper(first),
  SimpleFunctionWrapper(getitem),
  SimpleFunctionWrapper(id_),
  SimpleFunctionWrapper(min_),
  SimpleFunctionWrapper(over),
  SimpleFunctionWrapper(parse),
  SimpleFunctionWrapper(pop),
  SimpleFunctionWrapper(popd),
  SimpleFunctionWrapper(popop),
  SimpleFunctionWrapper(pred),
  SimpleFunctionWrapper(remove),
  SimpleFunctionWrapper(rest),
  SimpleFunctionWrapper(reverse),
  SimpleFunctionWrapper(rolldown),
  SimpleFunctionWrapper(rollup),
  SimpleFunctionWrapper(select),
  SimpleFunctionWrapper(shunt),
  SimpleFunctionWrapper(stack_),
  SimpleFunctionWrapper(succ),
  SimpleFunctionWrapper(sum_),
  SimpleFunctionWrapper(swaack),
  SimpleFunctionWrapper(swap),
  SimpleFunctionWrapper(truthy),
  SimpleFunctionWrapper(tuck),
  SimpleFunctionWrapper(uncons),
  SimpleFunctionWrapper(unstack),
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
  add_definitions(definitions, dictionary)
  return dictionary
