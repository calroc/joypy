'''


Definitions
  functions as equations


'''
from .joy import joy
from .parser import text_to_expression
from .stack import strstack
from .functions import note
from . import tracer


DEFINITIONS = '''


  rest == uncons popd ;
  first == uncons pop ;
  second == rest first ;
  third == rest rest first ;

  sum == 0 swap [+] step ;
  product == 1 swap [*] step ;

  swons == swap cons ;
  swoncat == swap concat ;
  shunt == [swons] step ;
  reverse == [] swap shunt ;
  flatten == [] swap [concat] step ;

  unit == [] cons ;
  quoted == [unit] dip ;
  unquoted == [i] dip ;

  enstacken == stack [clear] dip ;
  disenstacken == [truth] [uncons] while pop ;

  pam == [i] map ;
  run == [] swap infra ;
  size == [1] map sum ;
  size == 0 swap [pop ++] step ;

  average == [sum 1.0 *] [size] cleave / ;

  gcd == [0 >] [dup rollup modulus] while pop ;

  least_fraction == dup [gcd] infra [/] concat map ;


  divisor == popop 2 * ;
  minusb == pop neg ;
  radical == swap dup * rollup * 4 * - sqrt ;
  root1 == + swap / ;
  root2 == - swap / ;

  quadratic ==
    [[[divisor] [minusb] [radical]] pam] ternary i
    [[[root1] [root2]] pam] ternary ;


  *fraction ==
    [uncons] dip uncons
    [swap] dip concat
    [*] infra [*] dip cons ;

  *fraction0 == concat [[swap] dip * [*] dip] infra ;


  down_to_zero == [0 >] [dup --] while ;
  range_to_zero == unit [down_to_zero] infra ;

  times == [-- dip] cons [swap] infra [0 >] swap while pop ;


''' # End of DEFINITIONS


def partition_definition(d):
  name, proper, body_text = (n.strip() for n in d.partition('=='))
  if not proper and d:
    raise ValueError('Definition %r failed' % (d,))
  return name, body_text


def add_definition(d):
  '''
  Given the text of a definition such as "sum == 0 swap [+] step" add the
  parsed body expression to FUNCTIONS under that name.
  '''
  name, body_text = partition_definition(d)
  body = text_to_expression(body_text)
  strbody = strstack(body) # Normalized body_text.
  _enter_message = '%s == %s' % (name, strbody)
  _exit_message = '%s done.' % name

  def f(stack):
    if tracer.TRACE: joy.add_message(_enter_message)
    try:
      return joy(body, stack)
    finally:
      if tracer.TRACE: joy.add_message(_exit_message)

  f.__name__ = name
  f.__doc__ = strbody
  f.__body__ = body
  return note(f)
