This is an interpreter for the Joy computer language created by the late Manfred von Thun of La Trobe University.  It is provided as two pure Python scripts (they are compatible with Python 2 and Python 3): one has the interpreter and CLI and one has a GUI (Tkinter) interface. They have no other dependencies (beyond Python and Tkinter for the GUI.)

I think Joy is pretty important and useful and I hope that making available a version very close to the spirit of the original in a form that is easy to use and well-documented will help others discover it.

### Running **joy.py** from the command line. ###

If you start the **joy.py** script from the command line it will print all the defined functions' names and then start a Read-Evaluate-Print Loop, taking input from the keyboard and printing out the contents of the stack after each expression has be run.

```
joypy$ python joy.py
 != % * *fraction *fraction0 + ++ - -- / < << <= <> = > >= >> TRACE ^ abs acos acosh add and app1 app2 app3 asin asinh atan atan2 average b binary ceil clear cleave concat cons copysign cos cosh degrees dip dipd dipdd disenstacken div divisor down_to_zero dup dupd enstacken eq erf erfc execute exp expm1 fabs factorial first flatten floor floordiv fmod frexp gamma gcd ge gt help hypot i id ifte infra ldexp le least_fraction lgamma log log10 log1p lshift lt map minusb mod modf modulus mul ne neg not nullary or pam pop popd popop pos pow pred print_words product quadratic quoted radians radical range_to_zero rem remainder rest reverse roll< roll> rolldown rollup root1 root2 rshift run second shunt simple_manual sin sinh size sqrt stack step sub succ sum swap swoncat swons tan tanh ternary third times truediv trunc truth unary uncons unit unquoted unstack while x xor zip •

-> 

joy? 1 2 3 * +

-> 7

joy? [dup *] i

-> 49

joy? pop

-> 

joy? TRACE

-> 

joy? 1 2 3 * + [dup *] i
#  /-----\
    • 1 2 3 mul add [dup mul] i
   1 • 2 3 mul add [dup mul] i
   1 2 • 3 mul add [dup mul] i
   1 2 3 • mul add [dup mul] i
   1 6 • add [dup mul] i
   7 • [dup mul] i
   7 [dup mul] • i
# .. /-----\
     7 • dup mul
     7 7 • mul
     49 • 
# .. \-----/
# .. i done.
   49 • 
#  \-----/

-> 49

joy?  
```