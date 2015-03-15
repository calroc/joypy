# Finding the _size_ of a sequence #

One way to compute the **size** of a sequence is to **sum** a sequence that contains 1 for each of the items in the original sequence, in effect counting it.  Summing a sequence of numbers is easy, just start with zero and use **step** combinator to **add** each number to the running total.

```
   sum == 0 swap [+] step ;
  size == [1] map sum ;
```

Here's a trace:

```
joy? [1 "two" 3.0] size
 • [1 'two' 3.0] size
[1 'two' 3.0] • size
# size == [1] map sum
[1 'two' 3.0] • [1] map sum
[1 'two' 3.0] [1] • map sum
1 • 1
'two' • 1
3.0 • 1
[1 1 1] • sum
# sum == 0 swap [add] step
[1 1 1] • 0 swap [add] step
[1 1 1] 0 • swap [add] step
0 [1 1 1] • [add] step
0 [1 1 1] [add] • step
0 1 • add
1 1 • add
2 1 • add
# sum done.
# size done.

-> 3

joy? 
```

## Improving the algorithm ##

One thing this trace reveals is the inefficiency of iterating over sequences twice, once to build the sequence of ones and then again over the sequence of ones to add them up.  What if we modified the program to just count the items as it iterated over the sequence the first time?

Consider the line:
```
0 [1 1 1] [add] • step
```

If we replaced the sequence here with the original sequence:
```
0 [1 'two' 3.0] Q • step
```

What program would **Q** have to be to count up the **size** of the sequence?  It would have to discard the item (from the sequence, that **step** puts onto the stack) and instead **add** **1** to the item on the top of the stack (put there originally by the **0** **swap** functions.) Since **add** **1** is the same as **++** (the **succ** or successor function, aka increment) this give us the following for **Q**:
```
0 [1 'two' 3.0] [pop ++] • step
```

and

```
joy? [1 "two" 3.0] 0 swap [pop ++] step                                                
 • [1 'two' 3.0] 0 swap [pop succ] step
[1 'two' 3.0] • 0 swap [pop succ] step
[1 'two' 3.0] 0 • swap [pop succ] step
0 [1 'two' 3.0] • [pop succ] step
0 [1 'two' 3.0] [pop succ] • step
0 1 • pop succ
0 • succ
1 'two' • pop succ
1 • succ
2 3.0 • pop succ
2 • succ

-> 3

joy? 
```

## A better _size_ ##

This gives us a new definition for **size**:

```
  size == 0 swap [pop ++] step ;
```