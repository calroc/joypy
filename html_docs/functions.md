# Functions

stack → stack

We can catagorize functions into those that rearrange things on the stack
but don't otherwise process them, those that perform some process on
them, and those that call back into the joy() function to execute one or
more quoted programs themselves.  And, of course, there are commands that
do more than one or all three.

Commands that execute quoted programs are called "Combinators" and
they are the key to Joy's expressiveness and power.  The joy()
function by itself wouldn't accomplish much but with the availability of
several combinators it becomes a powerhouse.

Commands that just rearrange things on the stack can be written in python
as simple tuple unpacking and repacking.

Definitions, functions defined by equations, refactoring and how
important it is..

~~~~ {.python .numberLines startFrom="43"}
from .btree import get, insert
from .parser import text_to_expression
from .stack import list_to_stack, iter_stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## ALIASES

We allow for having alternate names for functions by this mapping.

~~~~ {.python .numberLines startFrom="52"}
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
  )


def add_aliases(items, A=ALIASES):
  D = dict(items)
  for name, aliases in A:
    try:
      F = D[name]
    except KeyError:
      continue
    for alias in aliases:
      D[alias] = F
  return D.items()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## FunctionWrapper

Right now, this just allows functions to have a nice repr().

~~~~ {.python .numberLines startFrom="92"}
class FunctionWrapper(object):
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

  def __init__(self, name, body_text, dictionary, doc=None):
    self.name = self.__name__ = name
    self.body = text_to_expression(body_text, dictionary)
    self._body = tuple(iter_stack(self.body))
    self.__doc__ = doc or body_text

  def __call__(self, stack, expression, dictionary):
    expression = list_to_stack(self._body, expression)
    return stack, expression, dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given some text describing a Joy function definition parse it and
  return a DefinitionWrapper.

~~~~ {.python .numberLines startFrom="143"}
  @classmethod
  def parse_definition(class_, defi, dictionary):
    name, proper, body_text = (n.strip() for n in defi.partition('=='))
    if not proper:
      raise ValueError('Definition %r failed' % (defi,))
    return class_(name, body_text, dictionary)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## generate_definitions()

~~~~ {.python .numberLines startFrom="153"}
def generate_definitions(defs, dictionary):
  for definition in defs.splitlines():
    definition = definition.strip()
    if not definition or definition.isspace():
      continue
    F = DefinitionWrapper.parse_definition(definition, dictionary)
    dictionary = insert(dictionary, F.name, F)
  return dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



