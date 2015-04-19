# Library

~~~~ {.python .numberLines startFrom="23"}
from inspect import getdoc

from .btree import items
from .joy import run
from .stack import list_to_stack, iter_stack, pick


definitions = """\
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
"""


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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given a list find the minimum.

~~~~ {.python .numberLines startFrom="90"}
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The cons operator expects a list on top of the stack and the potential
  member below. The effect is to add the potential member into the
  aggregate.

~~~~ {.python .numberLines startFrom="112"}
  (tos, (second, stack)) = S
  return (second, tos), stack


def uncons(S):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inverse of cons, removes an item from the top of the list on the stack
  and places it under the remaining list.

~~~~ {.python .numberLines startFrom="121"}
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The stack operator pushes onto the stack a list containing all the
  elements of the stack.

~~~~ {.python .numberLines startFrom="148"}
  return stack, stack


def unstack(S):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The unstack operator expects a list on top of the stack and makes that
  the stack discarding the rest of the stack.

~~~~ {.python .numberLines startFrom="156"}
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Replace the two lists on the top of the stack with a list of the pairs
  from each list.  The smallest list sets the length of the result list.

~~~~ {.python .numberLines startFrom="206"}
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
  print(' '.join(name for name, f in items(dictionary)))
  return stack, expression, dictionary


def simple_manual(stack):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Print words and help for each word.

~~~~ {.python .numberLines startFrom="287"}
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



