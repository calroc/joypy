Given a quoted program and and integer on the stack,
run the program that many times.

Start with a while program that runs P n times
```
... n [0 >] [-- P] while
```

But this means P has n as its first arg
```
... n P
```

The the general form of P can be some other program Q
run with dip on the rest of the stack, saving n.
```
... n [Q] dip
... Q n
```

So substituing back in we get:
```
... n [0 >] [-- [Q] dip] while pop
```

And now we must find a program that builds our "times"
program for us.
```
... n [Q] times => ... n [0 >] [-- [Q] dip] while pop
```

An obvious first step is to put Q into the body of the while program.
```
... n [Q] [-- dip] cons
... n [[Q] -- dip] [swap] infra
```

Arrange the test in the expected location.
```
... n [-- [Q] dip] [0 >] swap while pop
```

Run the while program.
```
... n [0 >] [-- [Q] dip] while pop
```

Putting it all together we get:
```
times == [-- dip] cons [swap] infra [0 >] swap while pop
```

And here it is in action:
```
joy? 1 5 [dup +] times
#  /-----\
    • 1 5 [dup add] times
   1 • 5 [dup add] times
   1 5 • [dup add] times
   1 5 [dup add] • times
# .. times == [pred dip] cons [swap] infra [0 gt] swap while pop
# .. /-----\
     1 5 [dup add] • [pred dip] cons [swap] infra [0 gt] swap while pop
     1 5 [dup add] [pred dip] • cons [swap] infra [0 gt] swap while pop
     1 5 [[dup add] pred dip] • [swap] infra [0 gt] swap while pop
     1 5 [[dup add] pred dip] [swap] • infra [0 gt] swap while pop
# .... /-----\
       dip pred [dup add] • swap
       dip [dup add] pred • 
# .... \-----/
# .... infra done.
     1 5 [pred [dup add] dip] • [0 gt] swap while pop
     1 5 [pred [dup add] dip] [0 gt] • swap while pop
     1 5 [0 gt] [pred [dup add] dip] • while pop
# .... /-----\
       1 5 • 0 gt
       1 5 0 • gt
       1 True • 
# .... \-----/
# .... /-----\
       1 5 • pred [dup add] dip
       1 4 • [dup add] dip
       1 4 [dup add] • dip
# ...... /-----\
         1 • dup add
         1 1 • add
         2 • 
# ...... \-----/
# ...... dip done.
       2 4 • 
# .... \-----/
# .... /-----\
       2 4 • 0 gt
       2 4 0 • gt
       2 True • 
# .... \-----/
# .... /-----\
       2 4 • pred [dup add] dip
       2 3 • [dup add] dip
       2 3 [dup add] • dip
# ...... /-----\
         2 • dup add
         2 2 • add
         4 • 
# ...... \-----/
# ...... dip done.
       4 3 • 
# .... \-----/
# .... /-----\
       4 3 • 0 gt
       4 3 0 • gt
       4 True • 
# .... \-----/
# .... /-----\
       4 3 • pred [dup add] dip
       4 2 • [dup add] dip
       4 2 [dup add] • dip
# ...... /-----\
         4 • dup add
         4 4 • add
         8 • 
# ...... \-----/
# ...... dip done.
       8 2 • 
# .... \-----/
# .... /-----\
       8 2 • 0 gt
       8 2 0 • gt
       8 True • 
# .... \-----/
# .... /-----\
       8 2 • pred [dup add] dip
       8 1 • [dup add] dip
       8 1 [dup add] • dip
# ...... /-----\
         8 • dup add
         8 8 • add
         16 • 
# ...... \-----/
# ...... dip done.
       16 1 • 
# .... \-----/
# .... /-----\
       16 1 • 0 gt
       16 1 0 • gt
       16 True • 
# .... \-----/
# .... /-----\
       16 1 • pred [dup add] dip
       16 0 • [dup add] dip
       16 0 [dup add] • dip
# ...... /-----\
         16 • dup add
         16 16 • add
         32 • 
# ...... \-----/
# ...... dip done.
       32 0 • 
# .... \-----/
# .... /-----\
       32 0 • 0 gt
       32 0 0 • gt
       32 False • 
# .... \-----/
# .... while done.
     32 0 • pop
     32 • 
# .. \-----/
# .. times done.
   32 • 
#  \-----/

-> 32

joy? 
```