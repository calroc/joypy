§ Combinators

TODO: Brief description of combinators (as contrasted with "normal" functions.)

Note: the combinators that have calls to joy() in them haven't been
rewritten to be in Continuation-Passing Style yet.

~~~~ {.python .numberLines startFrom="30"}
from .joy import joy
from .btree import get
from .stack import list_to_stack, iter_stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## i

The most straightforward combinator is called "i".  It just executes the
quoted program on the stack.

In the Continuation-Passing Style (CSP) it works by transferring the
terms from the quoted list on TOS into the pending expression before
returning back to the main joy() loop.

~~~~ {.python .numberLines startFrom="44"}
def i(stack, expression, dictionary):
  (quote, stack) = stack
  accumulator = list(iter_stack(quote))
  expression = list_to_stack(accumulator, expression)
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## x

Given a quoted program on the stack, the "x" combinator duplicates it and
then runs it.

    ... [Q] x = ... [Q] Q

It could be defined like so:

    x == dup i

    ... [Q] x = ... [Q] dup i
    ... [Q] x = ... [Q] [Q] i
    ... [Q] x = ... [Q]  Q

But rather than implement "x" as a definition, we write a Python function
that is almost exactly like the "i" combinator.

~~~~ {.python .numberLines startFrom="70"}
def x(stack, expression, dictionary):
  i = get(dictionary, 'i')
  quote = stack[0]
  expression = (i, (quote, expression))
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## b

The "b" combinator...

    ... [P] [Q] b = ... P Q

This combinator is slightly more involved than the "x" combinator, so
we look up the current "i" combinator and use it to make things simpler.
The "i" combinator is interleaved with the [P] and [Q] quoted programs:

    b == [i] dip i

    ... [P] [Q] b = ... [P] [Q] [i] dip i
    ... [P] [Q] b = ... [P] i [Q] i
    ... [P] [Q] b = ... P [Q] i
    ... [P] [Q] b = ... P Q

The implementation is straightforward:

~~~~ {.python .numberLines startFrom="97"}
def b(stack, expression, dictionary):
  i = get(dictionary, 'i')
  (q, (p, (stack))) = stack
  expression = (p, (i, (q, (i, expression))))
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## infra

Accept a quoted program and a list on the stack and run the program
with the list as its stack.

~~~~ {.python .numberLines startFrom="110"}
def infra(stack, expression, dictionary):
  i = get(dictionary, 'i')
  swaack = get(dictionary, 'swaack')
  (quote, (aggregate, stack)) = stack
  Q = (i, (stack, (swaack, expression)))
  return (quote, aggregate), Q, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## swaack

The name comes from "SWAp stACK".  I am considering dropping the extra a.

This is a weird combinator that takes a quoted literal and swaps the
existing stack contents with the contents of the quoted literal:

    c b a [x y z] swaack = z y x [a b c]

It is very useful (you can write a function much like call/cc with it for
example.)

The Python implementation is delightful:

~~~~ {.python .numberLines startFrom="133"}
def swaack(stack, expression, dictionary):
  new_stack, stack = stack
  stack = stack, new_stack
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## map

Run the quoted program on TOS on the items in the list under it, push a
new list with the results (in place of the program and original list.

~~~~ {.python .numberLines startFrom="145"}
def map_(S, expression, dictionary):
  (quote, (aggregate, stack)) = S
  results = list_to_stack([
    joy((term, stack), quote, dictionary)[0][0]
    for term in iter_stack(aggregate)
    ])
  return (results, stack), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## cleave
 
The cleave combinator expects two quotations, and below that an item X.
It first executes [P], with X on top, and saves the top result element.
Then it executes [Q], again with X, and saves the top result.
Finally it restores the stack to what it was below X and pushes the two
results P(X) and Q(X).

~~~~ {.python .numberLines startFrom="163"}
def cleave(S, expression, dictionary):
  (Q, (P, (x, stack))) = S
  p = joy((x, stack), P, dictionary)[0][0]
  q = joy((x, stack), Q, dictionary)[0][0]
  return (q, (p, stack)), expression, dictionary


def linrec(S, expression, dictionary):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The linrec combinator for linear recursion expects an if-part, a then-
  part, an else1-part and on top an else2-part. Like the ifte combinator it
  executes the if-part, and if that yields true it executes the then-part.
  Otherwise it executes the else1-part, then it recurses with all four
  parts, and finally it executes the else2-part.

~~~~ {.python .numberLines startFrom="178"}
##  else2, (else1, (then, (if_, stack))) = S
##  n = joy(stack, if_, dictionary)[0][0]
##  if n:
##    stack, _, d = joy(stack, then, dictionary)
##  else:
##    stack, _, d = joy(stack, else1, dictionary)
##    stk = (else2, (else1, (then, (if_, stack))))
##    stack, _, d = linrec(stk, (), d)
##  stack, _, d = joy(stack, else2, d)
##  return stack, expression, d
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[
    [[else1] i [if] [then] [else1] [else2] linrec]
    [then]
  ]
  [stackk] [if]
  infra first truthy getitem
  i [else2] i

~~~~ {.python .numberLines startFrom="199"}
  i = get(dictionary, 'i')
  infra = get(dictionary, 'infra')
  first = get(dictionary, 'first')
  truthy = get(dictionary, 'truthy')
  getitem = get(dictionary, 'getitem')
  linrec = get(dictionary, 'linrec')
  else2, (else1, (then, (if_, stack))) = S

  expression = (
    ((else1, (i, (if_, (then, (else1, (else2, (linrec, ()))))))),
     (then, ())),
    (stack,
     (if_,
      (infra,
       (first,
        (truthy,
         (getitem,
          (i,
           (else2,
            (i,
             expression))))))))))
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## ifte

    ... [if] [then] [else] . ifte

    ... [[else] [then]] [...] [if] . infra first truthy getitem i

~~~~ {.python .numberLines startFrom="232"}
def ifte(stack, expression, dictionary):
  i = get(dictionary, 'i')
  infra = get(dictionary, 'infra')
  first = get(dictionary, 'first')
  truthy = get(dictionary, 'truthy')
  getitem = get(dictionary, 'getitem')
  (else_, (then, (if_, stack))) = stack
  stack = (if_, (stack, ((else_, (then, ())), stack)))
  expression = (infra, (first, (truthy, (getitem, (i, expression)))))
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## dip
 
The dip combinator expects a program [P] and below that another item X. It pops both,
saves X, executes P and then restores X.

~~~~ {.python .numberLines startFrom="250"}
def dip(stack, expression, dictionary):
  i = get(dictionary, 'i')
  (quote, (x, stack)) = stack
  stack = (quote, stack)
  expression = i, (x, expression)
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## dipd
 
Like dip but expects two items.

~~~~ {.python .numberLines startFrom="263"}
def dipd(S, expression, dictionary):
  '''Like dip but expects two items.'''
  (quote, (x, (y, stack))) = S
  stack = joy(stack, quote, dictionary)[0]
  return (x, (y, stack)), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## dipdd

Like dip but expects three items.

~~~~ {.python .numberLines startFrom="275"}
def dipdd(S, expression, dictionary):
  '''Like dip but expects three items.'''
  (quote, (x, (y, (z, stack)))) = S
  stack = joy(stack, quote, dictionary)[0]
  return (x, (y, (z, stack))), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## app1

Given a quoted program on TOS and anything as the second stack item run
the program and replace the two args with the first result of the
program.

~~~~ {.python .numberLines startFrom="289"}
def app1(S, expression, dictionary):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given a quoted program on TOS and anything as the second stack item run
  the program and replace the two args with the first result of the
  program.

~~~~ {.python .numberLines startFrom="295"}
  (quote, (x, stack)) = S
  result = joy((x, stack), quote, dictionary)[0]
  return (result[0], stack), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## app2

Like app1 with two items.

~~~~ {.python .numberLines startFrom="305"}
def app2(S, expression, dictionary):
  '''Like app1 with two items.'''
  (quote, (x, (y, stack))) = S
  resultx = joy((x, stack), quote, dictionary)[0][0]
  resulty = joy((y, stack), quote, dictionary)[0][0]
  return (resultx, (resulty, stack)), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## app3

Like app1 with three items.

~~~~ {.python .numberLines startFrom="318"}
def app3(S, expression, dictionary):
  '''Like app1 with three items.'''
  (quote, (x, (y, (z, stack)))) = S
  resultx = joy((x, stack), quote, dictionary)[0][0]
  resulty = joy((y, stack), quote, dictionary)[0][0]
  resultz = joy((z, stack), quote, dictionary)[0][0]
  return (resultx, (resulty, (resultz, stack))), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## step

The step combinator removes the aggregate and the quotation, and then
repeatedly puts the members of the aggregate on top of the remaining
stack and executes the quotation.

~~~~ {.python .numberLines startFrom="334"}
def step(S, expression, dictionary):
  (quote, (aggregate, stack)) = S
  for term in iter_stack(aggregate):
    stack = joy((term, stack), quote, dictionary)[0]
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## while

    [if] [body] while

~~~~ {.python .numberLines startFrom="347"}
def while_(S, expression, dictionary):
  (body, (if_, stack)) = S
  while joy(stack, if_, dictionary)[0][0]:
    stack = joy(stack, body, dictionary)[0]
  return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## nullary

Run the program on TOS and return its first result without consuming
any of the stack (except the program on TOS.)

~~~~ {.python .numberLines startFrom="360"}
def nullary(S, expression, dictionary):
  (quote, stack) = S
  result = joy(stack, quote, dictionary)
  return (result[0][0], stack), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## unary

Run the program on TOS and return its first result, consuming exactly one
item from the stack (in addition to the program on TOS.)

~~~~ {.python .numberLines startFrom="372"}
def unary(S, expression, dictionary):
  (quote, stack) = S
  _, return_stack = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## binary

Run the program on TOS and return its first result, consuming exactly two
items from the stack (in addition to the program on TOS.)

~~~~ {.python .numberLines startFrom="385"}
def binary(S, expression, dictionary):
  (quote, stack) = S
  _, (_, return_stack) = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## ternary

Run the program on TOS and return its first result, consuming exactly
three items from the stack (in addition to the program on TOS.)

~~~~ {.python .numberLines startFrom="398"}
def ternary(S, expression, dictionary):
  (quote, stack) = S
  _, (_, (_, return_stack)) = stack
  result = joy(stack, quote, dictionary)[0]
  return (result[0], return_stack), expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



