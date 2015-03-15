# How to make an Integer Range #

Let's make a function that takes three integers representing the start, end and step values for a range and leaves a sequence of integers on the stack, like so:
```
0 5 1 R == [4 3 2 1 0]
3 19 3 R == [18 15 12 9 6 3]
```


## A new stack ##
Put a new empty sequence on the stack to contain the output range.
```
  a b c [[]] dipdd == [] a b c
```


## A comparison ##
We want to keep going **while** the number is less than the _stop_ input.
```
  a b c [[<] cons] dip == a [b <] c
```

## An operation ##
Each time we operate during the **while** combinator we want to put a copy of the current number starting with _start_ into the new sequence and then increase the current number by the step amount.  We can make that quoted program like so:
```
  a b c [+] cons [dup [swons] dip] swoncat == a b [dup [swons] dip c +]
```

and it works like this

```
  [...] n dup [swons] dip c +
  [...] n n   [swons] dip c +
  [...] n swons n         c +
  [n ...]       n         c +
  [n ...] n c +
```

The next thing that happens is **n c +** and the while loop repeats the conditional.

## Putting it all together ##

If we put these three programs together and use the **while** combinator it looks like this:
```
  R == [[<] cons] dip
       [+] cons [dup [swons] dip] swoncat
       [[]] dipdd
       while pop ;
```

Here's what a run of this function looks like:

```
-> 3 19 3

joy? [[<] cons] dip [+] cons [dup [swons] dip] swoncat [[]] dipdd while pop
#  /-----\
   3 19 3 • [[lt] cons] dip [add] cons [dup [swons] dip] swoncat [[]] dipdd while pop
   3 19 3 [[lt] cons] • dip [add] cons [dup [swons] dip] swoncat [[]] dipdd while pop
# .. /-----\
     3 19 • [lt] cons
     3 19 [lt] • cons
     3 [19 lt] • 
# .. \-----/
# .. dip done.
   3 [19 lt] 3 • [add] cons [dup [swons] dip] swoncat [[]] dipdd while pop
   3 [19 lt] 3 [add] • cons [dup [swons] dip] swoncat [[]] dipdd while pop
   3 [19 lt] [3 add] • [dup [swons] dip] swoncat [[]] dipdd while pop
   3 [19 lt] [3 add] [dup [swons] dip] • swoncat [[]] dipdd while pop
# .. swoncat == swap concat
# .. /-----\
     3 [19 lt] [3 add] [dup [swons] dip] • swap concat
     3 [19 lt] [dup [swons] dip] [3 add] • concat
     3 [19 lt] [dup [swons] dip 3 add] • 
# .. \-----/
# .. swoncat done.
   3 [19 lt] [dup [swons] dip 3 add] • [[]] dipdd while pop
   3 [19 lt] [dup [swons] dip 3 add] [[]] • dipdd while pop
# .. /-----\
      • []
     [] • 
# .. \-----/
# .. dipdd done.
```

At this point the quoted programs for the **while** combinator and the arguments for its operation are ready on the stack and the "execution" phase of the program begins.

```
   [] 3 [19 lt] [dup [swons] dip 3 add] • while pop
# .. /-----\
     [] 3 • 19 lt
     [] 3 19 • lt
     [] True • 
# .. \-----/
# .. /-----\
     [] 3 • dup [swons] dip 3 add
     [] 3 3 • [swons] dip 3 add
     [] 3 3 [swons] • dip 3 add
# .... /-----\
       [] 3 • swons
# ...... swons == swap cons
# ...... /-----\
         [] 3 • swap cons
         3 [] • cons
         [3] • 
# ...... \-----/
# ...... swons done.
       [3] • 
# .... \-----/
# .... dip done.
     [3] 3 • 3 add
     [3] 3 3 • add
     [3] 6 • 
# .. \-----/
# .. /-----\
     [3] 6 • 19 lt
     [3] 6 19 • lt
     [3] True • 
# .. \-----/
# .. /-----\
     [3] 6 • dup [swons] dip 3 add
     [3] 6 6 • [swons] dip 3 add
     [3] 6 6 [swons] • dip 3 add
# .... /-----\
       [3] 6 • swons
# ...... swons == swap cons
# ...... /-----\
         [3] 6 • swap cons
         6 [3] • cons
         [6 3] • 
# ...... \-----/
# ...... swons done.
       [6 3] • 
# .... \-----/
# .... dip done.
     [6 3] 6 • 3 add
     [6 3] 6 3 • add
     [6 3] 9 • 
# .. \-----/
# .. /-----\
     [6 3] 9 • 19 lt
     [6 3] 9 19 • lt
     [6 3] True • 
# .. \-----/
# .. /-----\
     [6 3] 9 • dup [swons] dip 3 add
     [6 3] 9 9 • [swons] dip 3 add
     [6 3] 9 9 [swons] • dip 3 add
# .... /-----\
       [6 3] 9 • swons
# ...... swons == swap cons
# ...... /-----\
         [6 3] 9 • swap cons
         9 [6 3] • cons
         [9 6 3] • 
# ...... \-----/
# ...... swons done.
       [9 6 3] • 
# .... \-----/
# .... dip done.
     [9 6 3] 9 • 3 add
     [9 6 3] 9 3 • add
     [9 6 3] 12 • 
# .. \-----/
# .. /-----\
     [9 6 3] 12 • 19 lt
     [9 6 3] 12 19 • lt
     [9 6 3] True • 
# .. \-----/
# .. /-----\
     [9 6 3] 12 • dup [swons] dip 3 add
     [9 6 3] 12 12 • [swons] dip 3 add
     [9 6 3] 12 12 [swons] • dip 3 add
# .... /-----\
       [9 6 3] 12 • swons
# ...... swons == swap cons
# ...... /-----\
         [9 6 3] 12 • swap cons
         12 [9 6 3] • cons
         [12 9 6 3] • 
# ...... \-----/
# ...... swons done.
       [12 9 6 3] • 
# .... \-----/
# .... dip done.
     [12 9 6 3] 12 • 3 add
     [12 9 6 3] 12 3 • add
     [12 9 6 3] 15 • 
# .. \-----/
# .. /-----\
     [12 9 6 3] 15 • 19 lt
     [12 9 6 3] 15 19 • lt
     [12 9 6 3] True • 
# .. \-----/
# .. /-----\
     [12 9 6 3] 15 • dup [swons] dip 3 add
     [12 9 6 3] 15 15 • [swons] dip 3 add
     [12 9 6 3] 15 15 [swons] • dip 3 add
# .... /-----\
       [12 9 6 3] 15 • swons
# ...... swons == swap cons
# ...... /-----\
         [12 9 6 3] 15 • swap cons
         15 [12 9 6 3] • cons
         [15 12 9 6 3] • 
# ...... \-----/
# ...... swons done.
       [15 12 9 6 3] • 
# .... \-----/
# .... dip done.
     [15 12 9 6 3] 15 • 3 add
     [15 12 9 6 3] 15 3 • add
     [15 12 9 6 3] 18 • 
# .. \-----/
# .. /-----\
     [15 12 9 6 3] 18 • 19 lt
     [15 12 9 6 3] 18 19 • lt
     [15 12 9 6 3] True • 
# .. \-----/
# .. /-----\
     [15 12 9 6 3] 18 • dup [swons] dip 3 add
     [15 12 9 6 3] 18 18 • [swons] dip 3 add
     [15 12 9 6 3] 18 18 [swons] • dip 3 add
# .... /-----\
       [15 12 9 6 3] 18 • swons
# ...... swons == swap cons
# ...... /-----\
         [15 12 9 6 3] 18 • swap cons
         18 [15 12 9 6 3] • cons
         [18 15 12 9 6 3] • 
# ...... \-----/
# ...... swons done.
       [18 15 12 9 6 3] • 
# .... \-----/
# .... dip done.
     [18 15 12 9 6 3] 18 • 3 add
     [18 15 12 9 6 3] 18 3 • add
     [18 15 12 9 6 3] 21 • 
# .. \-----/
# .. /-----\
     [18 15 12 9 6 3] 21 • 19 lt
     [18 15 12 9 6 3] 21 19 • lt
     [18 15 12 9 6 3] False • 
# .. \-----/
# .. while done.
   [18 15 12 9 6 3] 21 • pop
   [18 15 12 9 6 3] • 
#  \-----/

-> [18 15 12 9 6 3]

joy? 
```