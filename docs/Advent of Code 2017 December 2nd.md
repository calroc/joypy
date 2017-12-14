
# Advent of Code 2017

## December 2nd

For each row, determine the difference between the largest value and the smallest value; the checksum is the sum of all of these differences.

For example, given the following spreadsheet:

    5 1 9 5
    7 5 3
    2 4 6 8

* The first row's largest and smallest values are 9 and 1, and their difference is 8.
* The second row's largest and smallest values are 7 and 3, and their difference is 4.
* The third row's difference is 6.

In this example, the spreadsheet's checksum would be 8 + 4 + 6 = 18.


```python
from notebook_preamble import J, V, define
```

I'll assume the input is a Joy sequence of sequences of integers.

    [[5 1 9 5]
     [7 5 3]
     [2 4 6 8]]

So, obviously, the initial form will be a `step` function:

    AoC2017.2 == 0 swap [F +] step

This function `F` must get the `max` and `min` of a row of numbers and subtract.  We can define a helper function `maxmin` which does this:


```python
define('maxmin == [max] [min] cleave')
```


```python
J('[1 2 3] maxmin')
```

    3 1


Then `F` just does that then subtracts the min from the max:

    F == maxmin -

So:


```python
define('AoC2017.2 == [maxmin - +] step_zero')
```


```python
J('''

[[5 1 9 5]
 [7 5 3]
 [2 4 6 8]] AoC2017.2

''')
```

    18


...find the only two numbers in each row where one evenly divides the other - that is, where the result of the division operation is a whole number. They would like you to find those numbers on each line, divide them, and add up each line's result.

For example, given the following spreadsheet:

    5 9 2 8
    9 4 7 3
    3 8 6 5

*    In the first row, the only two numbers that evenly divide are 8 and 2; the result of this division is 4.
*    In the second row, the two numbers are 9 and 3; the result is 3.
*    In the third row, the result is 2.

In this example, the sum of the results would be 4 + 3 + 2 = 9.

What is the sum of each row's result in your puzzle input?


```python
J('[5 9 2 8] sort reverse')
```

    [9 8 5 2]



```python
J('[9 8 5 2] uncons [swap [divmod] cons] dupdip')
```

    [8 5 2] [9 divmod] [8 5 2]



    [9 8 5 2] uncons [swap [divmod] cons F] dupdip G
      [8 5 2]            [9 divmod]      F [8 5 2] G




```python
V('[8 5 2] [9 divmod] [uncons swap] dip dup [i not] dip')
```

                                          . [8 5 2] [9 divmod] [uncons swap] dip dup [i not] dip
                                  [8 5 2] . [9 divmod] [uncons swap] dip dup [i not] dip
                       [8 5 2] [9 divmod] . [uncons swap] dip dup [i not] dip
         [8 5 2] [9 divmod] [uncons swap] . dip dup [i not] dip
                                  [8 5 2] . uncons swap [9 divmod] dup [i not] dip
                                  8 [5 2] . swap [9 divmod] dup [i not] dip
                                  [5 2] 8 . [9 divmod] dup [i not] dip
                       [5 2] 8 [9 divmod] . dup [i not] dip
            [5 2] 8 [9 divmod] [9 divmod] . [i not] dip
    [5 2] 8 [9 divmod] [9 divmod] [i not] . dip
                       [5 2] 8 [9 divmod] . i not [9 divmod]
                                  [5 2] 8 . 9 divmod not [9 divmod]
                                [5 2] 8 9 . divmod not [9 divmod]
                                [5 2] 1 1 . not [9 divmod]
                            [5 2] 1 False . [9 divmod]
                 [5 2] 1 False [9 divmod] . 


## Tricky

Let's think.

Given a *sorted* sequence (from highest to lowest) we want to 
* for head, tail in sequence
    * for term in tail:
        * check if the head % term == 0
            * if so compute head / term and terminate loop
            * else continue

### So we want a `loop` I think

    [a b c d] True [Q] loop
    [a b c d] Q    [Q] loop

`Q` should either leave the result and False, or the `rest` and True.

       [a b c d] Q
    -----------------
        result 0

       [a b c d] Q
    -----------------
        [b c d] 1

This suggests that `Q` should start with:

    [a b c d] uncons dup roll<
    [b c d] [b c d] a

Now we just have to `pop` it if we don't need it.

    [b c d] [b c d] a [P] [T] [cons] app2 popdd [E] primrec
    [b c d] [b c d] [a P] [a T]                 [E] primrec

-------------------

    w/ Q == [% not] [T] [F] primrec

            [a b c d] uncons
            a [b c d] tuck
    [b c d] a [b c d] uncons
    [b c d] a b [c d] roll>
    [b c d] [c d] a b Q
    [b c d] [c d] a b [% not] [T] [F] primrec

    [b c d] [c d] a b T
    [b c d] [c d] a b / roll> popop 0

    [b c d] [c d] a b F                   Q
    [b c d] [c d] a b pop swap uncons ... Q
    [b c d] [c d] a       swap uncons ... Q
    [b c d] a [c d]            uncons ... Q
    [b c d] a c [d]                   roll> Q
    [b c d] [d] a c Q

    Q == [% not] [/ roll> popop 0] [pop swap uncons roll>] primrec
    
    uncons tuck uncons roll> Q


```python
J('[8 5 3 2] 9 [swap] [% not] [cons] app2 popdd')
```

    [8 5 3 2] [9 swap] [9 % not]


-------------------

            [a b c d] uncons
            a [b c d] tuck
    [b c d] a [b c d] [not] [popop 1] [Q] ifte

    [b c d] a [] popop 1
    [b c d] 1

    [b c d] a [b c d] Q 


       a [...] Q
    ---------------
       result 0

       a [...] Q
    ---------------
           1


    w/ Q == [first % not] [first / 0] [rest [not] [popop 1]] [ifte]



    a [b c d] [first % not] [first / 0] [rest [not] [popop 1]] [ifte]
    a [b c d]  first % not
    a b % not
    a%b not
    bool(a%b)

    a [b c d] [first % not] [first / 0] [rest [not] [popop 1]] [ifte]
    a [b c d]                first / 0
    a b / 0
    a/b 0

    a [b c d] [first % not] [first / 0] [rest [not] [popop 1]]   [ifte]
    a [b c d]                            rest [not] [popop 1] [Q] ifte
    a [c d]                                   [not] [popop 1] [Q] ifte
    a [c d]                                   [not] [popop 1] [Q] ifte

    a [c d] [not] [popop 1] [Q] ifte
    a [c d]  not

    a [] popop 1
    1

    a [c d] Q


    uncons tuck [first % not] [first / 0] [rest [not] [popop 1]] [ifte]
    
    


### I finally sat down with a piece of paper and blocked it out.

First, I made a function `G` that expects a number and a sequence of candidates and return the result or zero:

       n [...] G
    ---------------
        result

       n [...] G
    ---------------
           0

It's a recursive function that conditionally executes the recursive part of its recursive branch

    [Pg] [E] [R1 [Pi] [T]] [ifte] genrec

The recursive branch is the else-part of the inner `ifte`:

    G == [Pg] [E] [R1 [Pi] [T]]   [ifte] genrec
      == [Pg] [E] [R1 [Pi] [T] [G] ifte] ifte

But this is in hindsight.  Going forward I derived:

    G == [first % not]
         [first /]
         [rest [not] [popop 0]]
         [ifte] genrec

The predicate detects if the `n` can be evenly divided by the `first` item in the list.  If so, the then-part returns the result.  Otherwise, we have:

    n [m ...] rest [not] [popop 0] [G] ifte
    n [...]        [not] [popop 0] [G] ifte

This `ifte` guards against empty sequences and returns zero in that case, otherwise it executes `G`.


```python
define('G == [first % not] [first /] [rest [not] [popop 0]] [ifte] genrec')
```

Now we need a word that uses `G` on each (head, tail) pair of a sequence until it finds a (non-zero) result.  It's going to be designed to work on a stack that has some candidate `n`, a sequence of possible divisors, and a result that is zero to signal to continue (a non-zero value implies that it is the discovered result):

       n [...] p find-result
    ---------------------------
              result

It applies `G` using `nullary` because if it fails with one candidate it needs the list to get the next one (the list is otherwise consumed by `G`.)

    find-result == [0 >] [roll> popop] [roll< popop uncons [G] nullary] primrec

    n [...] p [0 >] [roll> popop] [roll< popop uncons [G] nullary] primrec

The base-case is trivial, return the (non-zero) result.  The recursive branch...

    n [...] p roll< popop uncons [G] nullary find-result
    [...] p n       popop uncons [G] nullary find-result
    [...]                 uncons [G] nullary find-result
    m [..]                       [G] nullary find-result
    m [..] p                                 find-result

The puzzle states that the input is well-formed, meaning that we can expect a result before the row sequence empties and so do not need to guard the `uncons`.


```python
define('find-result == [0 >] [roll> popop] [roll< popop uncons [G] nullary] primrec')
```


```python
J('[11 9 8 7 3 2] 0 tuck find-result')
```

    3.0


In order to get the thing started, we need to `sort` the list in descending order, then prime the `find-result` function with a dummy candidate value and zero ("continue") flag.


```python
define('prep-row == sort reverse 0 tuck')
```

Now we can define our program.


```python
define('AoC20017.2.extra == [prep-row find-result +] step_zero')
```


```python
J('''

[[5 9 2 8]
 [9 4 7 3]
 [3 8 6 5]] AoC20017.2.extra

''')
```

    9.0

