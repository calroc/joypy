
Cf. ["Bananas, Lenses, & Barbed Wire"](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.41.125)

# [Hylomorphism](https://en.wikipedia.org/wiki/Hylomorphism_%28computer_science%29)
A [hylomorphism](https://en.wikipedia.org/wiki/Hylomorphism_%28computer_science%29) `H :: A -> B` converts a value of type A into a value of type B by means of:

- A generator `G :: A -> (A, B)`
- A combiner `F :: (B, B) -> B`
- A predicate `P :: A -> Bool` to detect the base case
- A base case value `c :: B`
- Recursive calls (zero or more); it has a "call stack in the form of a cons list".

It may be helpful to see this function implemented in imperative Python code.


```python
def hylomorphism(c, F, P, G):
    '''Return a hylomorphism function H.'''

    def H(a):
        if P(a):
            result = c
        else:
            b, aa = G(a)
            result = F(b, H(aa))
        return result

    return H
```

### Finding [Triangular Numbers](https://en.wikipedia.org/wiki/Triangular_number)
As a concrete example let's use a function that, given a positive integer, returns the sum of all positive integers less than that one.  (In this case the types A and B are both `int`.)
### With `range()` and `sum()`


```python
r = range(10)
r
```




    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]




```python
sum(r)
```




    45




```python
range_sum = lambda n: sum(range(n))
range_sum(10)
```




    45



### As a hylomorphism


```python
G = lambda n: (n - 1, n - 1)
F = lambda a, b: a + b
P = lambda n: n <= 1

H = hylomorphism(0, F, P, G)
```


```python
H(10)
```




    45



If you were to run the above code in a debugger and check out the call stack you would find that the variable `b` in each call to `H()` is storing the intermediate values as `H()` recurses.  This is what was meant by "call stack in the form of a cons list".

### Joy Preamble


```python
from notebook_preamble import D, DefinitionWrapper, J, V, define
```

## Hylomorphism in Joy
We can define a combinator `hylomorphism` that will make a hylomorphism combinator `H` from constituent parts.

    H == c [F] [P] [G] hylomorphism

The function `H` is recursive, so we start with `ifte` and set the else-part to
some function `J` that will contain a quoted copy of `H`.  (The then-part just
discards the leftover `a` and replaces it with the base case value `c`.)

    H == [P] [pop c] [J] ifte

The else-part `J` gets just the argument `a` on the stack.

    a J
    a G              The first thing to do is use the generator G
    aa b             which produces b and a new aa
    aa b [H] dip     we recur with H on the new aa
    aa H b F         and run F on the result.

This gives us a definition for `J`.

    J == G [H] dip F

Plug it in and convert to genrec.

    H == [P] [pop c] [G [H] dip F] ifte
    H == [P] [pop c] [G]   [dip F] genrec

This is the form of a hylomorphism in Joy, which nicely illustrates that
it is a simple specialization of the general recursion combinator.

    H == [P] [pop c] [G] [dip F] genrec

## Derivation of `hylomorphism`

Now we just need to derive a definition that builds the `genrec` arguments
out of the pieces given to the `hylomorphism` combinator.

    H == [P] [pop c]              [G]                  [dip F] genrec
         [P] [c]    [pop] swoncat [G]        [F] [dip] swoncat genrec
         [P] c unit [pop] swoncat [G]        [F] [dip] swoncat genrec
         [P] c [G] [F] [unit [pop] swoncat] dipd [dip] swoncat genrec

Working in reverse:
- Use `swoncat` twice to decouple `[c]` and `[F]`.
- Use `unit` to dequote `c`.
- Use `dipd` to untangle `[unit [pop] swoncat]` from the givens.

At this point all of the arguments (givens) to the hylomorphism are to the left so we have
a definition for `hylomorphism`:

    hylomorphism == [unit [pop] swoncat] dipd [dip] swoncat genrec

The order of parameters is different than the one we started with but
that hardly matters, you can rearrange them or just supply them in the
expected order.

    [P] c [G] [F] hylomorphism == H




```python
define('hylomorphism == [unit [pop] swoncat] dipd [dip] swoncat genrec')
```

Demonstrate summing a range of integers from 0 to n-1.

- `[P]` is `[0 <=]`
- `c` is `0`
- `[G]` is `[1 - dup]`
- `[F]` is `[+]`

So to sum the positive integers less than five we can do this.


```python
V('5 [0 <=] 0 [1 - dup] [+] hylomorphism')
```

                                                                                   . 5 [0 <=] 0 [1 - dup] [+] hylomorphism
                                                                                 5 . [0 <=] 0 [1 - dup] [+] hylomorphism
                                                                          5 [0 <=] . 0 [1 - dup] [+] hylomorphism
                                                                        5 [0 <=] 0 . [1 - dup] [+] hylomorphism
                                                              5 [0 <=] 0 [1 - dup] . [+] hylomorphism
                                                          5 [0 <=] 0 [1 - dup] [+] . hylomorphism
                                                          5 [0 <=] 0 [1 - dup] [+] . [unit [pop] swoncat] dipd [dip] swoncat genrec
                                     5 [0 <=] 0 [1 - dup] [+] [unit [pop] swoncat] . dipd [dip] swoncat genrec
                                                                        5 [0 <=] 0 . unit [pop] swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                        5 [0 <=] 0 . [] cons [pop] swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                     5 [0 <=] 0 [] . cons [pop] swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                      5 [0 <=] [0] . [pop] swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                5 [0 <=] [0] [pop] . swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                5 [0 <=] [0] [pop] . swap concat [1 - dup] [+] [dip] swoncat genrec
                                                                5 [0 <=] [pop] [0] . concat [1 - dup] [+] [dip] swoncat genrec
                                                                  5 [0 <=] [pop 0] . [1 - dup] [+] [dip] swoncat genrec
                                                        5 [0 <=] [pop 0] [1 - dup] . [+] [dip] swoncat genrec
                                                    5 [0 <=] [pop 0] [1 - dup] [+] . [dip] swoncat genrec
                                              5 [0 <=] [pop 0] [1 - dup] [+] [dip] . swoncat genrec
                                              5 [0 <=] [pop 0] [1 - dup] [+] [dip] . swap concat genrec
                                              5 [0 <=] [pop 0] [1 - dup] [dip] [+] . concat genrec
                                                5 [0 <=] [pop 0] [1 - dup] [dip +] . genrec
        5 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte
    5 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [5] [0 <=] . infra first choice i
                                                                                 5 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 5] swaack first choice i
                                                                               5 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 5] swaack first choice i
                                                                             False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 5] swaack first choice i
       False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 5] . swaack first choice i
       5 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i
         5 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i
                       5 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i
                                                                                 5 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +
                                                                               5 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +
                                                                                 4 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +
                                                                               4 4 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +
                                     4 4 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip +
                                                                                 4 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 4 +
                                                                          4 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 4 +
                                                                  4 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 4 +
                                                        4 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 4 +
                                                4 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 4 +
        4 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 4 +
    4 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [4] [0 <=] . infra first choice i 4 +
                                                                                 4 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 4] swaack first choice i 4 +
                                                                               4 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 4] swaack first choice i 4 +
                                                                             False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 4] swaack first choice i 4 +
       False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 4] . swaack first choice i 4 +
       4 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 4 +
         4 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 4 +
                       4 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 4 +
                                                                                 4 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 4 +
                                                                               4 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 4 +
                                                                                 3 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 4 +
                                                                               3 3 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 4 +
                                     3 3 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 4 +
                                                                                 3 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 3 + 4 +
                                                                          3 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 3 + 4 +
                                                                  3 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 3 + 4 +
                                                        3 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 3 + 4 +
                                                3 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 3 + 4 +
        3 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 3 + 4 +
    3 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [3] [0 <=] . infra first choice i 3 + 4 +
                                                                                 3 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 3] swaack first choice i 3 + 4 +
                                                                               3 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 3] swaack first choice i 3 + 4 +
                                                                             False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 3] swaack first choice i 3 + 4 +
       False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 3] . swaack first choice i 3 + 4 +
       3 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 3 + 4 +
         3 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 3 + 4 +
                       3 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 3 + 4 +
                                                                                 3 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 3 + 4 +
                                                                               3 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 3 + 4 +
                                                                                 2 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 3 + 4 +
                                                                               2 2 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 3 + 4 +
                                     2 2 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 3 + 4 +
                                                                                 2 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 2 + 3 + 4 +
                                                                          2 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 2 + 3 + 4 +
                                                                  2 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 2 + 3 + 4 +
                                                        2 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 2 + 3 + 4 +
                                                2 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 2 + 3 + 4 +
        2 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 2 + 3 + 4 +
    2 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [2] [0 <=] . infra first choice i 2 + 3 + 4 +
                                                                                 2 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 2] swaack first choice i 2 + 3 + 4 +
                                                                               2 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 2] swaack first choice i 2 + 3 + 4 +
                                                                             False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 2] swaack first choice i 2 + 3 + 4 +
       False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 2] . swaack first choice i 2 + 3 + 4 +
       2 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 2 + 3 + 4 +
         2 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 2 + 3 + 4 +
                       2 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 2 + 3 + 4 +
                                                                                 2 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 2 + 3 + 4 +
                                                                               2 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 2 + 3 + 4 +
                                                                                 1 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 2 + 3 + 4 +
                                                                               1 1 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 2 + 3 + 4 +
                                     1 1 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 2 + 3 + 4 +
                                                                                 1 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 1 + 2 + 3 + 4 +
                                                                          1 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 1 + 2 + 3 + 4 +
                                                                  1 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 1 + 2 + 3 + 4 +
                                                        1 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 1 + 2 + 3 + 4 +
                                                1 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 1 + 2 + 3 + 4 +
        1 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 1 + 2 + 3 + 4 +
    1 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [1] [0 <=] . infra first choice i 1 + 2 + 3 + 4 +
                                                                                 1 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 1] swaack first choice i 1 + 2 + 3 + 4 +
                                                                               1 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 1] swaack first choice i 1 + 2 + 3 + 4 +
                                                                             False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 1] swaack first choice i 1 + 2 + 3 + 4 +
       False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 1] . swaack first choice i 1 + 2 + 3 + 4 +
       1 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 1 + 2 + 3 + 4 +
         1 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 1 + 2 + 3 + 4 +
                       1 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 1 + 2 + 3 + 4 +
                                                                                 1 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 1 + 2 + 3 + 4 +
                                                                               1 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 1 + 2 + 3 + 4 +
                                                                                 0 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 1 + 2 + 3 + 4 +
                                                                               0 0 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 1 + 2 + 3 + 4 +
                                     0 0 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 1 + 2 + 3 + 4 +
                                                                                 0 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 0 + 1 + 2 + 3 + 4 +
                                                                          0 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 0 + 1 + 2 + 3 + 4 +
                                                                  0 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 0 + 1 + 2 + 3 + 4 +
                                                        0 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 0 + 1 + 2 + 3 + 4 +
                                                0 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 0 + 1 + 2 + 3 + 4 +
        0 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 0 + 1 + 2 + 3 + 4 +
    0 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [0] [0 <=] . infra first choice i 0 + 1 + 2 + 3 + 4 +
                                                                                 0 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 0] swaack first choice i 0 + 1 + 2 + 3 + 4 +
                                                                               0 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 0] swaack first choice i 0 + 1 + 2 + 3 + 4 +
                                                                              True . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 0] swaack first choice i 0 + 1 + 2 + 3 + 4 +
        True [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 0] . swaack first choice i 0 + 1 + 2 + 3 + 4 +
        0 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [True] . first choice i 0 + 1 + 2 + 3 + 4 +
          0 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] True . choice i 0 + 1 + 2 + 3 + 4 +
                                                                         0 [pop 0] . i 0 + 1 + 2 + 3 + 4 +
                                                                                 0 . pop 0 0 + 1 + 2 + 3 + 4 +
                                                                                   . 0 0 + 1 + 2 + 3 + 4 +
                                                                                 0 . 0 + 1 + 2 + 3 + 4 +
                                                                               0 0 . + 1 + 2 + 3 + 4 +
                                                                                 0 . 1 + 2 + 3 + 4 +
                                                                               0 1 . + 2 + 3 + 4 +
                                                                                 1 . 2 + 3 + 4 +
                                                                               1 2 . + 3 + 4 +
                                                                                 3 . 3 + 4 +
                                                                               3 3 . + 4 +
                                                                                 6 . 4 +
                                                                               6 4 . +
                                                                                10 . 


# Anamorphism
An anamorphism can be defined as a hylomorphism that uses `[]` for `c` and
`swons` for `F`.

    [P] [G] anamorphism == [P] [] [G] [swons] hylomorphism == A

This allows us to define an anamorphism combinator in terms of
the hylomorphism combinator.

    [] swap [swons] hylomorphism == anamorphism

Partial evaluation gives us a "pre-cooked" form.

    [P] [G] . anamorphism
    [P] [G] . [] swap [swons] hylomorphism
    [P] [G] [] . swap [swons] hylomorphism
    [P] [] [G] . [swons] hylomorphism
    [P] [] [G] [swons] . hylomorphism
    [P] [] [G] [swons] . [unit [pop] swoncat] dipd [dip] swoncat genrec
    [P] [] [G] [swons] [unit [pop] swoncat] . dipd [dip] swoncat genrec
    [P] [] . unit [pop] swoncat [G] [swons] [dip] swoncat genrec
    [P] [[]] [pop] . swoncat [G] [swons] [dip] swoncat genrec
    [P] [pop []] [G] [swons] [dip] . swoncat genrec

    [P] [pop []] [G] [dip swons] genrec

(We could also have just substituted for `c` and `F` in the definition of `H`.)

    H == [P] [pop c ] [G] [dip F    ] genrec
    A == [P] [pop []] [G] [dip swons] genrec

The partial evaluation is overkill in this case but it serves as a
reminder that this sort of program specialization can, in many cases, be
carried out automatically.)

Untangle `[G]` from `[pop []]` using `swap`.

    [P] [G] [pop []] swap [dip swons] genrec

All of the arguments to `anamorphism` are to the left, so we have a definition for it.

    anamorphism == [pop []] swap [dip swons] genrec

An example of an anamorphism is the range function.

    range == [0 <=] [1 - dup] anamorphism


# Catamorphism
A catamorphism can be defined as a hylomorphism that uses `[uncons swap]` for `[G]`
and `[[] =]` for the predicate `[P]`.

    c [F] catamorphism == [[] =] c [uncons swap] [F] hylomorphism == C

This allows us to define a `catamorphism` combinator in terms of
the `hylomorphism` combinator.

    [[] =] roll> [uncons swap] swap hylomorphism == catamorphism
 
Partial evaluation doesn't help much.

    c [F] . catamorphism
    c [F] . [[] =] roll> [uncons swap] swap hylomorphism
    c [F] [[] =] . roll> [uncons swap] swap hylomorphism
    [[] =] c [F] [uncons swap] . swap hylomorphism
    [[] =] c [uncons swap] [F] . hylomorphism
    [[] =] c [uncons swap] [F] [unit [pop] swoncat] . dipd [dip] swoncat genrec
    [[] =] c . unit [pop] swoncat [uncons swap] [F] [dip] swoncat genrec
    [[] =] [c] [pop] . swoncat [uncons swap] [F] [dip] swoncat genrec
    [[] =] [pop c] [uncons swap] [F] [dip] . swoncat genrec
    [[] =] [pop c] [uncons swap] [dip F] genrec

Because the arguments to catamorphism have to be prepared (unlike the arguments
to anamorphism, which only need to be rearranged slightly) there isn't much point
to "pre-cooking" the definition.

    catamorphism == [[] =] roll> [uncons swap] swap hylomorphism

An example of a catamorphism is the sum function.

    sum == 0 [+] catamorphism

### "Fusion Law" for catas (UNFINISHED!!!)

I'm not sure exactly how to translate the "Fusion Law" for catamorphisms into Joy.

I know that a `map` composed with a cata can be expressed as a new cata:

    [F] map b [B] cata == b [F B] cata

But this isn't the one described in "Bananas...".  That's more like:

A cata composed with some function can be expressed as some other cata:

    b [B] catamorphism F == c [C] catamorphism

Given:

    b F == c

    ...

    B F == [F] dip C

    ...

    b[B]cata F == c[C]cata

    F(B(head, tail)) == C(head, F(tail))

    1 [2 3] B F         1 [2 3] F C


    b F == c
    B F == F C

    b [B] catamorphism F == c [C] catamorphism
    b [B] catamorphism F == b F [C] catamorphism

    ...

Or maybe,

    [F] map b [B] cata == c [C] cata     ???

    [F] map b [B] cata == b [F B] cata    I think this is generally true, unless F consumes stack items
                                            instead of just transforming TOS.  Of course, there's always [F] unary.
    b [F] unary [[F] unary B] cata

    [10 *] map 0 swap [+] step == 0 swap [10 * +] step


For example:

    F == 10 *
    b == 0
    B == +
    c == 0
    C == F +
    
    b F    == c
    0 10 * == 0

    B F    == [F]    dip C
    + 10 * == [10 *] dip F +
    + 10 * == [10 *] dip 10 * +

    n m + 10 * == 10(n+m)

    n m [10 *] dip 10 * +
    n 10 * m 10 * +
    10n m 10 * +
    10n 10m +
    10n+10m

    10n+10m = 10(n+m)

Ergo:

    0 [+] catamorphism 10 * == 0 [10 * +] catamorphism

## The `step` combinator will usually be better to use than `catamorphism`.

    sum == 0 swap [+] step
    sum == 0 [+] catamorphism

# anamorphism catamorphism == hylomorphism
Here is (part of) the payoff.

An anamorphism followed by (composed with) a
catamorphism is a hylomorphism, with the advantage that the hylomorphism 
does not create the intermediate list structure.  The values are stored in
either the call stack, for those implementations that use one, or in the pending
expression ("continuation") for the Joypy interpreter.  They still have to 
be somewhere, converting from an anamorphism and catamorphism to a hylomorphism
just prevents using additional storage and doing additional processing.

        range == [0 <=] [1 - dup] anamorphism
          sum == 0 [+] catamorphism

    range sum == [0 <=] [1 - dup] anamorphism 0 [+] catamorphism
              == [0 <=] 0 [1 - dup] [+] hylomorphism

We can let the `hylomorphism` combinator build `range_sum` for us or just
substitute ourselves.

            H == [P]    [pop c] [G]       [dip F] genrec
    range_sum == [0 <=] [pop 0] [1 - dup] [dip +] genrec



```python
defs = '''
anamorphism == [pop []] swap [dip swons] genrec
hylomorphism == [unit [pop] swoncat] dipd [dip] swoncat genrec
catamorphism == [[] =] roll> [uncons swap] swap hylomorphism
range == [0 <=] [1 - dup] anamorphism
sum == 0 [+] catamorphism
range_sum == [0 <=] 0 [1 - dup] [+] hylomorphism
'''

DefinitionWrapper.add_definitions(defs, D)
```


```python
J('10 range')
```

    [9 8 7 6 5 4 3 2 1 0]



```python
J('[9 8 7 6 5 4 3 2 1 0] sum')
```

    45



```python
V('10 range sum')
```

                                                                                                                                   . 10 range sum
                                                                                                                                10 . range sum
                                                                                                                                10 . [0 <=] [1 - dup] anamorphism sum
                                                                                                                         10 [0 <=] . [1 - dup] anamorphism sum
                                                                                                               10 [0 <=] [1 - dup] . anamorphism sum
                                                                                                               10 [0 <=] [1 - dup] . [pop []] swap [dip swons] genrec sum
                                                                                                      10 [0 <=] [1 - dup] [pop []] . swap [dip swons] genrec sum
                                                                                                      10 [0 <=] [pop []] [1 - dup] . [dip swons] genrec sum
                                                                                          10 [0 <=] [pop []] [1 - dup] [dip swons] . genrec sum
                                             10 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte sum
                                        10 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [10] [0 <=] . infra first choice i sum
                                                                                                                                10 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 10] swaack first choice i sum
                                                                                                                              10 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 10] swaack first choice i sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 10] swaack first choice i sum
                                            False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 10] . swaack first choice i sum
                                            10 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i sum
                                              10 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i sum
                                                             10 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i sum
                                                                                                                                10 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons sum
                                                                                                                              10 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons sum
                                                                                                                                 9 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons sum
                                                                                                                               9 9 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons sum
                                                                                9 9 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons sum
                                                                                                                                 9 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 9 swons sum
                                                                                                                          9 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 9 swons sum
                                                                                                                 9 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 9 swons sum
                                                                                                       9 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 9 swons sum
                                                                                           9 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 9 swons sum
                                              9 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 9 swons sum
                                          9 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [9] [0 <=] . infra first choice i 9 swons sum
                                                                                                                                 9 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 9] swaack first choice i 9 swons sum
                                                                                                                               9 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 9] swaack first choice i 9 swons sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 9] swaack first choice i 9 swons sum
                                             False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 9] . swaack first choice i 9 swons sum
                                             9 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 9 swons sum
                                               9 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i 9 swons sum
                                                              9 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i 9 swons sum
                                                                                                                                 9 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 9 swons sum
                                                                                                                               9 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 9 swons sum
                                                                                                                                 8 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 9 swons sum
                                                                                                                               8 8 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 9 swons sum
                                                                                8 8 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons 9 swons sum
                                                                                                                                 8 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 8 swons 9 swons sum
                                                                                                                          8 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 8 swons 9 swons sum
                                                                                                                 8 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 8 swons 9 swons sum
                                                                                                       8 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 8 swons 9 swons sum
                                                                                           8 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 8 swons 9 swons sum
                                              8 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 8 swons 9 swons sum
                                          8 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [8] [0 <=] . infra first choice i 8 swons 9 swons sum
                                                                                                                                 8 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 8] swaack first choice i 8 swons 9 swons sum
                                                                                                                               8 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 8] swaack first choice i 8 swons 9 swons sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 8] swaack first choice i 8 swons 9 swons sum
                                             False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 8] . swaack first choice i 8 swons 9 swons sum
                                             8 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 8 swons 9 swons sum
                                               8 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i 8 swons 9 swons sum
                                                              8 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i 8 swons 9 swons sum
                                                                                                                                 8 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 8 swons 9 swons sum
                                                                                                                               8 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 8 swons 9 swons sum
                                                                                                                                 7 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 8 swons 9 swons sum
                                                                                                                               7 7 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 8 swons 9 swons sum
                                                                                7 7 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons 8 swons 9 swons sum
                                                                                                                                 7 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 7 swons 8 swons 9 swons sum
                                                                                                                          7 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 7 swons 8 swons 9 swons sum
                                                                                                                 7 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 7 swons 8 swons 9 swons sum
                                                                                                       7 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 7 swons 8 swons 9 swons sum
                                                                                           7 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 7 swons 8 swons 9 swons sum
                                              7 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 7 swons 8 swons 9 swons sum
                                          7 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [7] [0 <=] . infra first choice i 7 swons 8 swons 9 swons sum
                                                                                                                                 7 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 7] swaack first choice i 7 swons 8 swons 9 swons sum
                                                                                                                               7 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 7] swaack first choice i 7 swons 8 swons 9 swons sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 7] swaack first choice i 7 swons 8 swons 9 swons sum
                                             False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 7] . swaack first choice i 7 swons 8 swons 9 swons sum
                                             7 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 7 swons 8 swons 9 swons sum
                                               7 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i 7 swons 8 swons 9 swons sum
                                                              7 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i 7 swons 8 swons 9 swons sum
                                                                                                                                 7 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 7 swons 8 swons 9 swons sum
                                                                                                                               7 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 7 swons 8 swons 9 swons sum
                                                                                                                                 6 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 7 swons 8 swons 9 swons sum
                                                                                                                               6 6 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 7 swons 8 swons 9 swons sum
                                                                                6 6 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons 7 swons 8 swons 9 swons sum
                                                                                                                                 6 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                          6 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                 6 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 6 swons 7 swons 8 swons 9 swons sum
                                                                                                       6 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 6 swons 7 swons 8 swons 9 swons sum
                                                                                           6 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 6 swons 7 swons 8 swons 9 swons sum
                                              6 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 6 swons 7 swons 8 swons 9 swons sum
                                          6 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [6] [0 <=] . infra first choice i 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 6 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 6] swaack first choice i 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               6 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 6] swaack first choice i 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 6] swaack first choice i 6 swons 7 swons 8 swons 9 swons sum
                                             False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 6] . swaack first choice i 6 swons 7 swons 8 swons 9 swons sum
                                             6 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 6 swons 7 swons 8 swons 9 swons sum
                                               6 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i 6 swons 7 swons 8 swons 9 swons sum
                                                              6 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 6 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               6 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 5 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               5 5 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                5 5 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 5 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                          5 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                 5 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                       5 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                           5 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                              5 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                          5 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [5] [0 <=] . infra first choice i 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 5 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 5] swaack first choice i 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               5 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 5] swaack first choice i 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 5] swaack first choice i 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 5] . swaack first choice i 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             5 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                               5 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                              5 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 5 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               5 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 4 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               4 4 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                4 4 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 4 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                          4 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                 4 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                       4 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                           4 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                              4 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                          4 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [4] [0 <=] . infra first choice i 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 4 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 4] swaack first choice i 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               4 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 4] swaack first choice i 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 4] swaack first choice i 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 4] . swaack first choice i 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             4 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                               4 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                              4 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 4 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               4 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 3 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               3 3 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                3 3 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 3 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                          3 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                 3 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                       3 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                           3 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                              3 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                          3 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [3] [0 <=] . infra first choice i 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 3 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 3] swaack first choice i 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               3 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 3] swaack first choice i 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 3] swaack first choice i 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 3] . swaack first choice i 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             3 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                               3 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                              3 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 3 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               3 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 2 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               2 2 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                2 2 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 2 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                          2 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                 2 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                       2 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                           2 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                              2 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                          2 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [2] [0 <=] . infra first choice i 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 2 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 2] swaack first choice i 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               2 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 2] swaack first choice i 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 2] swaack first choice i 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 2] . swaack first choice i 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             2 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                               2 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                              2 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 2 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               2 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 1 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               1 1 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                1 1 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 1 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                          1 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                 1 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                       1 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                           1 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                              1 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                          1 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [1] [0 <=] . infra first choice i 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 1 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 1] swaack first choice i 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               1 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 1] swaack first choice i 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             False . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 1] swaack first choice i 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             False [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 1] . swaack first choice i 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                             1 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                               1 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] False . choice i 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                              1 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . i 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 1 . 1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               1 1 . - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 0 . dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               0 0 . [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                0 0 [[0 <=] [pop []] [1 - dup] [dip swons] genrec] . dip swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 0 . [0 <=] [pop []] [1 - dup] [dip swons] genrec 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                          0 [0 <=] . [pop []] [1 - dup] [dip swons] genrec 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                 0 [0 <=] [pop []] . [1 - dup] [dip swons] genrec 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                       0 [0 <=] [pop []] [1 - dup] . [dip swons] genrec 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                           0 [0 <=] [pop []] [1 - dup] [dip swons] . genrec 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                              0 [0 <=] [pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] . ifte 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                          0 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [0] [0 <=] . infra first choice i 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 0 . 0 <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 0] swaack first choice i 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               0 0 . <= [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 0] swaack first choice i 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                              True . [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 0] swaack first choice i 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                              True [[pop []] [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] 0] . swaack first choice i 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                              0 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] [True] . first choice i 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                0 [1 - dup [[0 <=] [pop []] [1 - dup] [dip swons] genrec] dip swons] [pop []] True . choice i 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                        0 [pop []] . i 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                 0 . pop [] 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                   . [] 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                                [] . 0 swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                              [] 0 . swons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                              [] 0 . swap cons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                              0 [] . cons 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                               [0] . 1 swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             [0] 1 . swons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             [0] 1 . swap cons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             1 [0] . cons 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                             [1 0] . 2 swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                           [1 0] 2 . swons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                           [1 0] 2 . swap cons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                           2 [1 0] . cons 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                           [2 1 0] . 3 swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                         [2 1 0] 3 . swons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                         [2 1 0] 3 . swap cons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                         3 [2 1 0] . cons 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                         [3 2 1 0] . 4 swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                       [3 2 1 0] 4 . swons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                       [3 2 1 0] 4 . swap cons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                       4 [3 2 1 0] . cons 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                       [4 3 2 1 0] . 5 swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                     [4 3 2 1 0] 5 . swons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                     [4 3 2 1 0] 5 . swap cons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                     5 [4 3 2 1 0] . cons 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                     [5 4 3 2 1 0] . 6 swons 7 swons 8 swons 9 swons sum
                                                                                                                   [5 4 3 2 1 0] 6 . swons 7 swons 8 swons 9 swons sum
                                                                                                                   [5 4 3 2 1 0] 6 . swap cons 7 swons 8 swons 9 swons sum
                                                                                                                   6 [5 4 3 2 1 0] . cons 7 swons 8 swons 9 swons sum
                                                                                                                   [6 5 4 3 2 1 0] . 7 swons 8 swons 9 swons sum
                                                                                                                 [6 5 4 3 2 1 0] 7 . swons 8 swons 9 swons sum
                                                                                                                 [6 5 4 3 2 1 0] 7 . swap cons 8 swons 9 swons sum
                                                                                                                 7 [6 5 4 3 2 1 0] . cons 8 swons 9 swons sum
                                                                                                                 [7 6 5 4 3 2 1 0] . 8 swons 9 swons sum
                                                                                                               [7 6 5 4 3 2 1 0] 8 . swons 9 swons sum
                                                                                                               [7 6 5 4 3 2 1 0] 8 . swap cons 9 swons sum
                                                                                                               8 [7 6 5 4 3 2 1 0] . cons 9 swons sum
                                                                                                               [8 7 6 5 4 3 2 1 0] . 9 swons sum
                                                                                                             [8 7 6 5 4 3 2 1 0] 9 . swons sum
                                                                                                             [8 7 6 5 4 3 2 1 0] 9 . swap cons sum
                                                                                                             9 [8 7 6 5 4 3 2 1 0] . cons sum
                                                                                                             [9 8 7 6 5 4 3 2 1 0] . sum
                                                                                                             [9 8 7 6 5 4 3 2 1 0] . 0 [+] catamorphism
                                                                                                           [9 8 7 6 5 4 3 2 1 0] 0 . [+] catamorphism
                                                                                                       [9 8 7 6 5 4 3 2 1 0] 0 [+] . catamorphism
                                                                                                       [9 8 7 6 5 4 3 2 1 0] 0 [+] . [[] =] roll> [uncons swap] swap hylomorphism
                                                                                                [9 8 7 6 5 4 3 2 1 0] 0 [+] [[] =] . roll> [uncons swap] swap hylomorphism
                                                                                                [9 8 7 6 5 4 3 2 1 0] [[] =] 0 [+] . [uncons swap] swap hylomorphism
                                                                                  [9 8 7 6 5 4 3 2 1 0] [[] =] 0 [+] [uncons swap] . swap hylomorphism
                                                                                  [9 8 7 6 5 4 3 2 1 0] [[] =] 0 [uncons swap] [+] . hylomorphism
                                                                                  [9 8 7 6 5 4 3 2 1 0] [[] =] 0 [uncons swap] [+] . [unit [pop] swoncat] dipd [dip] swoncat genrec
                                                             [9 8 7 6 5 4 3 2 1 0] [[] =] 0 [uncons swap] [+] [unit [pop] swoncat] . dipd [dip] swoncat genrec
                                                                                                    [9 8 7 6 5 4 3 2 1 0] [[] =] 0 . unit [pop] swoncat [uncons swap] [+] [dip] swoncat genrec
                                                                                                    [9 8 7 6 5 4 3 2 1 0] [[] =] 0 . [] cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec
                                                                                                 [9 8 7 6 5 4 3 2 1 0] [[] =] 0 [] . cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec
                                                                                                  [9 8 7 6 5 4 3 2 1 0] [[] =] [0] . [pop] swoncat [uncons swap] [+] [dip] swoncat genrec
                                                                                            [9 8 7 6 5 4 3 2 1 0] [[] =] [0] [pop] . swoncat [uncons swap] [+] [dip] swoncat genrec
                                                                                            [9 8 7 6 5 4 3 2 1 0] [[] =] [0] [pop] . swap concat [uncons swap] [+] [dip] swoncat genrec
                                                                                            [9 8 7 6 5 4 3 2 1 0] [[] =] [pop] [0] . concat [uncons swap] [+] [dip] swoncat genrec
                                                                                              [9 8 7 6 5 4 3 2 1 0] [[] =] [pop 0] . [uncons swap] [+] [dip] swoncat genrec
                                                                                [9 8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] . [+] [dip] swoncat genrec
                                                                            [9 8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] [+] . [dip] swoncat genrec
                                                                      [9 8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] [+] [dip] . swoncat genrec
                                                                      [9 8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] [+] [dip] . swap concat genrec
                                                                      [9 8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] [dip] [+] . concat genrec
                                                                        [9 8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] [dip +] . genrec
                            [9 8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte
    [9 8 7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[9 8 7 6 5 4 3 2 1 0]] [[] =] . infra first choice i
                                                                                                             [9 8 7 6 5 4 3 2 1 0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [9 8 7 6 5 4 3 2 1 0]] swaack first choice i
                                                                                                          [9 8 7 6 5 4 3 2 1 0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [9 8 7 6 5 4 3 2 1 0]] swaack first choice i
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [9 8 7 6 5 4 3 2 1 0]] swaack first choice i
                           False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [9 8 7 6 5 4 3 2 1 0]] . swaack first choice i
                           [9 8 7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i
                             [9 8 7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i
                                           [9 8 7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i
                                                                                                             [9 8 7 6 5 4 3 2 1 0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +
                                                                                                             9 [8 7 6 5 4 3 2 1 0] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +
                                                                                                             [8 7 6 5 4 3 2 1 0] 9 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +
                                                               [8 7 6 5 4 3 2 1 0] 9 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip +
                                                                                                               [8 7 6 5 4 3 2 1 0] . [[] =] [pop 0] [uncons swap] [dip +] genrec 9 +
                                                                                                        [8 7 6 5 4 3 2 1 0] [[] =] . [pop 0] [uncons swap] [dip +] genrec 9 +
                                                                                                [8 7 6 5 4 3 2 1 0] [[] =] [pop 0] . [uncons swap] [dip +] genrec 9 +
                                                                                  [8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] . [dip +] genrec 9 +
                                                                          [8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] [dip +] . genrec 9 +
                              [8 7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 9 +
        [8 7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[8 7 6 5 4 3 2 1 0]] [[] =] . infra first choice i 9 +
                                                                                                               [8 7 6 5 4 3 2 1 0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [8 7 6 5 4 3 2 1 0]] swaack first choice i 9 +
                                                                                                            [8 7 6 5 4 3 2 1 0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [8 7 6 5 4 3 2 1 0]] swaack first choice i 9 +
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [8 7 6 5 4 3 2 1 0]] swaack first choice i 9 +
                             False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [8 7 6 5 4 3 2 1 0]] . swaack first choice i 9 +
                             [8 7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i 9 +
                               [8 7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 9 +
                                             [8 7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 9 +
                                                                                                               [8 7 6 5 4 3 2 1 0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 9 +
                                                                                                               8 [7 6 5 4 3 2 1 0] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 9 +
                                                                                                               [7 6 5 4 3 2 1 0] 8 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 9 +
                                                                 [7 6 5 4 3 2 1 0] 8 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 9 +
                                                                                                                 [7 6 5 4 3 2 1 0] . [[] =] [pop 0] [uncons swap] [dip +] genrec 8 + 9 +
                                                                                                          [7 6 5 4 3 2 1 0] [[] =] . [pop 0] [uncons swap] [dip +] genrec 8 + 9 +
                                                                                                  [7 6 5 4 3 2 1 0] [[] =] [pop 0] . [uncons swap] [dip +] genrec 8 + 9 +
                                                                                    [7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] . [dip +] genrec 8 + 9 +
                                                                            [7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] [dip +] . genrec 8 + 9 +
                                [7 6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 8 + 9 +
            [7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[7 6 5 4 3 2 1 0]] [[] =] . infra first choice i 8 + 9 +
                                                                                                                 [7 6 5 4 3 2 1 0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [7 6 5 4 3 2 1 0]] swaack first choice i 8 + 9 +
                                                                                                              [7 6 5 4 3 2 1 0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [7 6 5 4 3 2 1 0]] swaack first choice i 8 + 9 +
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [7 6 5 4 3 2 1 0]] swaack first choice i 8 + 9 +
                               False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [7 6 5 4 3 2 1 0]] . swaack first choice i 8 + 9 +
                               [7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i 8 + 9 +
                                 [7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 8 + 9 +
                                               [7 6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 8 + 9 +
                                                                                                                 [7 6 5 4 3 2 1 0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 8 + 9 +
                                                                                                                 7 [6 5 4 3 2 1 0] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 8 + 9 +
                                                                                                                 [6 5 4 3 2 1 0] 7 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 8 + 9 +
                                                                   [6 5 4 3 2 1 0] 7 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 8 + 9 +
                                                                                                                   [6 5 4 3 2 1 0] . [[] =] [pop 0] [uncons swap] [dip +] genrec 7 + 8 + 9 +
                                                                                                            [6 5 4 3 2 1 0] [[] =] . [pop 0] [uncons swap] [dip +] genrec 7 + 8 + 9 +
                                                                                                    [6 5 4 3 2 1 0] [[] =] [pop 0] . [uncons swap] [dip +] genrec 7 + 8 + 9 +
                                                                                      [6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] . [dip +] genrec 7 + 8 + 9 +
                                                                              [6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] [dip +] . genrec 7 + 8 + 9 +
                                  [6 5 4 3 2 1 0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 7 + 8 + 9 +
                [6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[6 5 4 3 2 1 0]] [[] =] . infra first choice i 7 + 8 + 9 +
                                                                                                                   [6 5 4 3 2 1 0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [6 5 4 3 2 1 0]] swaack first choice i 7 + 8 + 9 +
                                                                                                                [6 5 4 3 2 1 0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [6 5 4 3 2 1 0]] swaack first choice i 7 + 8 + 9 +
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [6 5 4 3 2 1 0]] swaack first choice i 7 + 8 + 9 +
                                 False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [6 5 4 3 2 1 0]] . swaack first choice i 7 + 8 + 9 +
                                 [6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i 7 + 8 + 9 +
                                   [6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 7 + 8 + 9 +
                                                 [6 5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 7 + 8 + 9 +
                                                                                                                   [6 5 4 3 2 1 0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 7 + 8 + 9 +
                                                                                                                   6 [5 4 3 2 1 0] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 7 + 8 + 9 +
                                                                                                                   [5 4 3 2 1 0] 6 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 7 + 8 + 9 +
                                                                     [5 4 3 2 1 0] 6 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 7 + 8 + 9 +
                                                                                                                     [5 4 3 2 1 0] . [[] =] [pop 0] [uncons swap] [dip +] genrec 6 + 7 + 8 + 9 +
                                                                                                              [5 4 3 2 1 0] [[] =] . [pop 0] [uncons swap] [dip +] genrec 6 + 7 + 8 + 9 +
                                                                                                      [5 4 3 2 1 0] [[] =] [pop 0] . [uncons swap] [dip +] genrec 6 + 7 + 8 + 9 +
                                                                                        [5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] . [dip +] genrec 6 + 7 + 8 + 9 +
                                                                                [5 4 3 2 1 0] [[] =] [pop 0] [uncons swap] [dip +] . genrec 6 + 7 + 8 + 9 +
                                    [5 4 3 2 1 0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 6 + 7 + 8 + 9 +
                    [5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[5 4 3 2 1 0]] [[] =] . infra first choice i 6 + 7 + 8 + 9 +
                                                                                                                     [5 4 3 2 1 0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [5 4 3 2 1 0]] swaack first choice i 6 + 7 + 8 + 9 +
                                                                                                                  [5 4 3 2 1 0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [5 4 3 2 1 0]] swaack first choice i 6 + 7 + 8 + 9 +
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [5 4 3 2 1 0]] swaack first choice i 6 + 7 + 8 + 9 +
                                   False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [5 4 3 2 1 0]] . swaack first choice i 6 + 7 + 8 + 9 +
                                   [5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i 6 + 7 + 8 + 9 +
                                     [5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 6 + 7 + 8 + 9 +
                                                   [5 4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 6 + 7 + 8 + 9 +
                                                                                                                     [5 4 3 2 1 0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 6 + 7 + 8 + 9 +
                                                                                                                     5 [4 3 2 1 0] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 6 + 7 + 8 + 9 +
                                                                                                                     [4 3 2 1 0] 5 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 6 + 7 + 8 + 9 +
                                                                       [4 3 2 1 0] 5 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 6 + 7 + 8 + 9 +
                                                                                                                       [4 3 2 1 0] . [[] =] [pop 0] [uncons swap] [dip +] genrec 5 + 6 + 7 + 8 + 9 +
                                                                                                                [4 3 2 1 0] [[] =] . [pop 0] [uncons swap] [dip +] genrec 5 + 6 + 7 + 8 + 9 +
                                                                                                        [4 3 2 1 0] [[] =] [pop 0] . [uncons swap] [dip +] genrec 5 + 6 + 7 + 8 + 9 +
                                                                                          [4 3 2 1 0] [[] =] [pop 0] [uncons swap] . [dip +] genrec 5 + 6 + 7 + 8 + 9 +
                                                                                  [4 3 2 1 0] [[] =] [pop 0] [uncons swap] [dip +] . genrec 5 + 6 + 7 + 8 + 9 +
                                      [4 3 2 1 0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 5 + 6 + 7 + 8 + 9 +
                        [4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[4 3 2 1 0]] [[] =] . infra first choice i 5 + 6 + 7 + 8 + 9 +
                                                                                                                       [4 3 2 1 0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [4 3 2 1 0]] swaack first choice i 5 + 6 + 7 + 8 + 9 +
                                                                                                                    [4 3 2 1 0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [4 3 2 1 0]] swaack first choice i 5 + 6 + 7 + 8 + 9 +
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [4 3 2 1 0]] swaack first choice i 5 + 6 + 7 + 8 + 9 +
                                     False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [4 3 2 1 0]] . swaack first choice i 5 + 6 + 7 + 8 + 9 +
                                     [4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i 5 + 6 + 7 + 8 + 9 +
                                       [4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 5 + 6 + 7 + 8 + 9 +
                                                     [4 3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 5 + 6 + 7 + 8 + 9 +
                                                                                                                       [4 3 2 1 0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 5 + 6 + 7 + 8 + 9 +
                                                                                                                       4 [3 2 1 0] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 5 + 6 + 7 + 8 + 9 +
                                                                                                                       [3 2 1 0] 4 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 5 + 6 + 7 + 8 + 9 +
                                                                         [3 2 1 0] 4 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 5 + 6 + 7 + 8 + 9 +
                                                                                                                         [3 2 1 0] . [[] =] [pop 0] [uncons swap] [dip +] genrec 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                  [3 2 1 0] [[] =] . [pop 0] [uncons swap] [dip +] genrec 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                          [3 2 1 0] [[] =] [pop 0] . [uncons swap] [dip +] genrec 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                            [3 2 1 0] [[] =] [pop 0] [uncons swap] . [dip +] genrec 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                    [3 2 1 0] [[] =] [pop 0] [uncons swap] [dip +] . genrec 4 + 5 + 6 + 7 + 8 + 9 +
                                        [3 2 1 0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 4 + 5 + 6 + 7 + 8 + 9 +
                            [3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[3 2 1 0]] [[] =] . infra first choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                         [3 2 1 0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [3 2 1 0]] swaack first choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                      [3 2 1 0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [3 2 1 0]] swaack first choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [3 2 1 0]] swaack first choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                       False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [3 2 1 0]] . swaack first choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                       [3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                         [3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                                       [3 2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                         [3 2 1 0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                         3 [2 1 0] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                         [2 1 0] 3 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                           [2 1 0] 3 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                           [2 1 0] . [[] =] [pop 0] [uncons swap] [dip +] genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                    [2 1 0] [[] =] . [pop 0] [uncons swap] [dip +] genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                            [2 1 0] [[] =] [pop 0] . [uncons swap] [dip +] genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                              [2 1 0] [[] =] [pop 0] [uncons swap] . [dip +] genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                      [2 1 0] [[] =] [pop 0] [uncons swap] [dip +] . genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                          [2 1 0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                [2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[2 1 0]] [[] =] . infra first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                           [2 1 0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [2 1 0]] swaack first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                        [2 1 0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [2 1 0]] swaack first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [2 1 0]] swaack first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                         False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [2 1 0]] . swaack first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                         [2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                           [2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                         [2 1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                           [2 1 0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                           2 [1 0] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                           [1 0] 2 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                             [1 0] 2 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             [1 0] . [[] =] [pop 0] [uncons swap] [dip +] genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                      [1 0] [[] =] . [pop 0] [uncons swap] [dip +] genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                              [1 0] [[] =] [pop 0] . [uncons swap] [dip +] genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                [1 0] [[] =] [pop 0] [uncons swap] . [dip +] genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                        [1 0] [[] =] [pop 0] [uncons swap] [dip +] . genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                            [1 0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                    [1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[1 0]] [[] =] . infra first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             [1 0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [1 0]] swaack first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                          [1 0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [1 0]] swaack first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [1 0]] swaack first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                           False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [1 0]] . swaack first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                           [1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                             [1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                           [1 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             [1 0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             1 [0] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             [0] 1 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                               [0] 1 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                               [0] . [[] =] [pop 0] [uncons swap] [dip +] genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                        [0] [[] =] . [pop 0] [uncons swap] [dip +] genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                [0] [[] =] [pop 0] . [uncons swap] [dip +] genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                  [0] [[] =] [pop 0] [uncons swap] . [dip +] genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                          [0] [[] =] [pop 0] [uncons swap] [dip +] . genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                              [0] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                        [0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[0]] [[] =] . infra first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                               [0] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [0]] swaack first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                            [0] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [0]] swaack first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [0]] swaack first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                             False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [0]] . swaack first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                             [0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False] . first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                               [0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                             [0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                               [0] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                              0 [] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                              [] 0 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                [] 0 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                [] . [[] =] [pop 0] [uncons swap] [dip +] genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                         [] [[] =] . [pop 0] [uncons swap] [dip +] genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                 [] [[] =] [pop 0] . [uncons swap] [dip +] genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                   [] [[] =] [pop 0] [uncons swap] . [dip +] genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                           [] [[] =] [pop 0] [uncons swap] [dip +] . genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                               [] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                          [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[]] [[] =] . infra first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                [] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] []] swaack first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                             [] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] []] swaack first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                              True . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] []] swaack first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                               True [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] []] . swaack first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                               [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [True] . first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] True . choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                        [] [pop 0] . i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                [] . pop 0 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                   . 0 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                 0 . 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                               0 0 . + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                 0 . 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                               0 1 . + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                 1 . 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                               1 2 . + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                 3 . 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                               3 3 . + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                 6 . 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                                                               6 4 . + 5 + 6 + 7 + 8 + 9 +
                                                                                                                                10 . 5 + 6 + 7 + 8 + 9 +
                                                                                                                              10 5 . + 6 + 7 + 8 + 9 +
                                                                                                                                15 . 6 + 7 + 8 + 9 +
                                                                                                                              15 6 . + 7 + 8 + 9 +
                                                                                                                                21 . 7 + 8 + 9 +
                                                                                                                              21 7 . + 8 + 9 +
                                                                                                                                28 . 8 + 9 +
                                                                                                                              28 8 . + 9 +
                                                                                                                                36 . 9 +
                                                                                                                              36 9 . +
                                                                                                                                45 . 



```python
V('10 range_sum')
```

                                                                                     . 10 range_sum
                                                                                  10 . range_sum
                                                                                  10 . [0 <=] 0 [1 - dup] [+] hylomorphism
                                                                           10 [0 <=] . 0 [1 - dup] [+] hylomorphism
                                                                         10 [0 <=] 0 . [1 - dup] [+] hylomorphism
                                                               10 [0 <=] 0 [1 - dup] . [+] hylomorphism
                                                           10 [0 <=] 0 [1 - dup] [+] . hylomorphism
                                                           10 [0 <=] 0 [1 - dup] [+] . [unit [pop] swoncat] dipd [dip] swoncat genrec
                                      10 [0 <=] 0 [1 - dup] [+] [unit [pop] swoncat] . dipd [dip] swoncat genrec
                                                                         10 [0 <=] 0 . unit [pop] swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                         10 [0 <=] 0 . [] cons [pop] swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                      10 [0 <=] 0 [] . cons [pop] swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                       10 [0 <=] [0] . [pop] swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                 10 [0 <=] [0] [pop] . swoncat [1 - dup] [+] [dip] swoncat genrec
                                                                 10 [0 <=] [0] [pop] . swap concat [1 - dup] [+] [dip] swoncat genrec
                                                                 10 [0 <=] [pop] [0] . concat [1 - dup] [+] [dip] swoncat genrec
                                                                   10 [0 <=] [pop 0] . [1 - dup] [+] [dip] swoncat genrec
                                                         10 [0 <=] [pop 0] [1 - dup] . [+] [dip] swoncat genrec
                                                     10 [0 <=] [pop 0] [1 - dup] [+] . [dip] swoncat genrec
                                               10 [0 <=] [pop 0] [1 - dup] [+] [dip] . swoncat genrec
                                               10 [0 <=] [pop 0] [1 - dup] [+] [dip] . swap concat genrec
                                               10 [0 <=] [pop 0] [1 - dup] [dip] [+] . concat genrec
                                                 10 [0 <=] [pop 0] [1 - dup] [dip +] . genrec
         10 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte
    10 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [10] [0 <=] . infra first choice i
                                                                                  10 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 10] swaack first choice i
                                                                                10 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 10] swaack first choice i
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 10] swaack first choice i
        False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 10] . swaack first choice i
        10 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i
          10 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i
                        10 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i
                                                                                  10 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +
                                                                                10 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +
                                                                                   9 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +
                                                                                 9 9 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +
                                       9 9 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip +
                                                                                   9 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 9 +
                                                                            9 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 9 +
                                                                    9 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 9 +
                                                          9 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 9 +
                                                  9 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 9 +
          9 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 9 +
      9 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [9] [0 <=] . infra first choice i 9 +
                                                                                   9 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 9] swaack first choice i 9 +
                                                                                 9 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 9] swaack first choice i 9 +
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 9] swaack first choice i 9 +
         False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 9] . swaack first choice i 9 +
         9 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 9 +
           9 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 9 +
                         9 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 9 +
                                                                                   9 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 9 +
                                                                                 9 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 9 +
                                                                                   8 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 9 +
                                                                                 8 8 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 9 +
                                       8 8 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 9 +
                                                                                   8 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 8 + 9 +
                                                                            8 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 8 + 9 +
                                                                    8 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 8 + 9 +
                                                          8 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 8 + 9 +
                                                  8 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 8 + 9 +
          8 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 8 + 9 +
      8 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [8] [0 <=] . infra first choice i 8 + 9 +
                                                                                   8 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 8] swaack first choice i 8 + 9 +
                                                                                 8 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 8] swaack first choice i 8 + 9 +
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 8] swaack first choice i 8 + 9 +
         False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 8] . swaack first choice i 8 + 9 +
         8 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 8 + 9 +
           8 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 8 + 9 +
                         8 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 8 + 9 +
                                                                                   8 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 8 + 9 +
                                                                                 8 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 8 + 9 +
                                                                                   7 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 8 + 9 +
                                                                                 7 7 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 8 + 9 +
                                       7 7 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 8 + 9 +
                                                                                   7 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 7 + 8 + 9 +
                                                                            7 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 7 + 8 + 9 +
                                                                    7 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 7 + 8 + 9 +
                                                          7 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 7 + 8 + 9 +
                                                  7 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 7 + 8 + 9 +
          7 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 7 + 8 + 9 +
      7 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [7] [0 <=] . infra first choice i 7 + 8 + 9 +
                                                                                   7 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 7] swaack first choice i 7 + 8 + 9 +
                                                                                 7 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 7] swaack first choice i 7 + 8 + 9 +
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 7] swaack first choice i 7 + 8 + 9 +
         False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 7] . swaack first choice i 7 + 8 + 9 +
         7 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 7 + 8 + 9 +
           7 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 7 + 8 + 9 +
                         7 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 7 + 8 + 9 +
                                                                                   7 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 7 + 8 + 9 +
                                                                                 7 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 7 + 8 + 9 +
                                                                                   6 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 7 + 8 + 9 +
                                                                                 6 6 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 7 + 8 + 9 +
                                       6 6 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 7 + 8 + 9 +
                                                                                   6 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 6 + 7 + 8 + 9 +
                                                                            6 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 6 + 7 + 8 + 9 +
                                                                    6 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 6 + 7 + 8 + 9 +
                                                          6 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 6 + 7 + 8 + 9 +
                                                  6 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 6 + 7 + 8 + 9 +
          6 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 6 + 7 + 8 + 9 +
      6 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [6] [0 <=] . infra first choice i 6 + 7 + 8 + 9 +
                                                                                   6 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 6] swaack first choice i 6 + 7 + 8 + 9 +
                                                                                 6 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 6] swaack first choice i 6 + 7 + 8 + 9 +
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 6] swaack first choice i 6 + 7 + 8 + 9 +
         False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 6] . swaack first choice i 6 + 7 + 8 + 9 +
         6 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 6 + 7 + 8 + 9 +
           6 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 6 + 7 + 8 + 9 +
                         6 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 6 + 7 + 8 + 9 +
                                                                                   6 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 6 + 7 + 8 + 9 +
                                                                                 6 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 6 + 7 + 8 + 9 +
                                                                                   5 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 6 + 7 + 8 + 9 +
                                                                                 5 5 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 6 + 7 + 8 + 9 +
                                       5 5 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 6 + 7 + 8 + 9 +
                                                                                   5 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 5 + 6 + 7 + 8 + 9 +
                                                                            5 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 5 + 6 + 7 + 8 + 9 +
                                                                    5 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 5 + 6 + 7 + 8 + 9 +
                                                          5 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 5 + 6 + 7 + 8 + 9 +
                                                  5 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 5 + 6 + 7 + 8 + 9 +
          5 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 5 + 6 + 7 + 8 + 9 +
      5 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [5] [0 <=] . infra first choice i 5 + 6 + 7 + 8 + 9 +
                                                                                   5 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 5] swaack first choice i 5 + 6 + 7 + 8 + 9 +
                                                                                 5 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 5] swaack first choice i 5 + 6 + 7 + 8 + 9 +
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 5] swaack first choice i 5 + 6 + 7 + 8 + 9 +
         False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 5] . swaack first choice i 5 + 6 + 7 + 8 + 9 +
         5 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 5 + 6 + 7 + 8 + 9 +
           5 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 5 + 6 + 7 + 8 + 9 +
                         5 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 5 + 6 + 7 + 8 + 9 +
                                                                                   5 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 5 + 6 + 7 + 8 + 9 +
                                                                                 5 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 5 + 6 + 7 + 8 + 9 +
                                                                                   4 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 5 + 6 + 7 + 8 + 9 +
                                                                                 4 4 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 5 + 6 + 7 + 8 + 9 +
                                       4 4 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 5 + 6 + 7 + 8 + 9 +
                                                                                   4 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 4 + 5 + 6 + 7 + 8 + 9 +
                                                                            4 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 4 + 5 + 6 + 7 + 8 + 9 +
                                                                    4 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 4 + 5 + 6 + 7 + 8 + 9 +
                                                          4 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 4 + 5 + 6 + 7 + 8 + 9 +
                                                  4 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 4 + 5 + 6 + 7 + 8 + 9 +
          4 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 4 + 5 + 6 + 7 + 8 + 9 +
      4 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [4] [0 <=] . infra first choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   4 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 4] swaack first choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 4 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 4] swaack first choice i 4 + 5 + 6 + 7 + 8 + 9 +
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 4] swaack first choice i 4 + 5 + 6 + 7 + 8 + 9 +
         False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 4] . swaack first choice i 4 + 5 + 6 + 7 + 8 + 9 +
         4 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 4 + 5 + 6 + 7 + 8 + 9 +
           4 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 4 + 5 + 6 + 7 + 8 + 9 +
                         4 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   4 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 4 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   3 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 3 3 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 4 + 5 + 6 + 7 + 8 + 9 +
                                       3 3 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   3 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                            3 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                    3 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                          3 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                  3 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 3 + 4 + 5 + 6 + 7 + 8 + 9 +
          3 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 3 + 4 + 5 + 6 + 7 + 8 + 9 +
      3 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [3] [0 <=] . infra first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   3 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 3] swaack first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 3 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 3] swaack first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 3] swaack first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
         False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 3] . swaack first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
         3 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
           3 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                         3 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   3 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 3 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   2 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 2 2 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                       2 2 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   2 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                            2 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                    2 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                          2 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                  2 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
          2 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
      2 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [2] [0 <=] . infra first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   2 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 2] swaack first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 2 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 2] swaack first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 2] swaack first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
         False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 2] . swaack first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
         2 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
           2 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                         2 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   2 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 2 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   1 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 1 1 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                       1 1 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   1 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                            1 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                    1 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                          1 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                  1 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
          1 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
      1 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [1] [0 <=] . infra first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   1 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 1] swaack first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 1 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 1] swaack first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                               False . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 1] swaack first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
         False [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 1] . swaack first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
         1 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [False] . first choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
           1 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] False . choice i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                         1 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . i 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   1 . 1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 1 1 . - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   0 . dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 0 0 . [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                       0 0 [[0 <=] [pop 0] [1 - dup] [dip +] genrec] . dip + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   0 . [0 <=] [pop 0] [1 - dup] [dip +] genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                            0 [0 <=] . [pop 0] [1 - dup] [dip +] genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                    0 [0 <=] [pop 0] . [1 - dup] [dip +] genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                          0 [0 <=] [pop 0] [1 - dup] . [dip +] genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                  0 [0 <=] [pop 0] [1 - dup] [dip +] . genrec 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
          0 [0 <=] [pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] . ifte 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
      0 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [0] [0 <=] . infra first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   0 . 0 <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 0] swaack first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 0 0 . <= [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 0] swaack first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                True . [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 0] swaack first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
          True [[pop 0] [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] 0] . swaack first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
          0 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] [True] . first choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
            0 [1 - dup [[0 <=] [pop 0] [1 - dup] [dip +] genrec] dip +] [pop 0] True . choice i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                           0 [pop 0] . i 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   0 . pop 0 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                     . 0 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   0 . 0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 0 0 . + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   0 . 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 0 1 . + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   1 . 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 1 2 . + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   3 . 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 3 3 . + 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                   6 . 4 + 5 + 6 + 7 + 8 + 9 +
                                                                                 6 4 . + 5 + 6 + 7 + 8 + 9 +
                                                                                  10 . 5 + 6 + 7 + 8 + 9 +
                                                                                10 5 . + 6 + 7 + 8 + 9 +
                                                                                  15 . 6 + 7 + 8 + 9 +
                                                                                15 6 . + 7 + 8 + 9 +
                                                                                  21 . 7 + 8 + 9 +
                                                                                21 7 . + 8 + 9 +
                                                                                  28 . 8 + 9 +
                                                                                28 8 . + 9 +
                                                                                  36 . 9 +
                                                                                36 9 . +
                                                                                  45 . 


# Factorial Function and Paramorphisms
A paramorphism `P :: B -> A` is a recursion combinator that uses `dup` on intermediate values.

    n swap [P] [pop] [[F] dupdip G] primrec

With
- `n :: A` is the "identity" for `F` (like 1 for multiplication, 0 for addition)
- `F :: (A, B) -> A`
- `G :: B -> B` generates the next `B` value.
- and lastly `P :: B -> Bool` detects the end of the series.

For Factorial function (types `A` and `B` are both integer):

    n == 1
    F == *
    G == --
    P == 1 <=


```python
define('factorial == 1 swap [1 <=] [pop] [[*] dupdip --] primrec')
```

Try it with input 3 (omitting evaluation of predicate):

    3 1 swap [1 <=] [pop] [[*] dupdip --] primrec
    1 3      [1 <=] [pop] [[*] dupdip --] primrec

    1 3 [*] dupdip --
    1 3  * 3      --
    3      3      --
    3      2

    3 2 [*] dupdip --
    3 2  *  2      --
    6       2      --
    6       1

    6 1 [1 <=] [pop] [[*] dupdip --] primrec

    6 1 pop
    6


```python
J('3 factorial')
```

    6


### Derive `paramorphism` from the form above.

    n swap [P] [pop] [[F] dupdip G] primrec

    n swap [P]       [pop]     [[F] dupdip G]                  primrec
    n [P] [swap] dip [pop]     [[F] dupdip G]                  primrec
    n [P] [[F] dupdip G]                [[swap] dip [pop]] dip primrec
    n [P] [F] [dupdip G]           cons [[swap] dip [pop]] dip primrec
    n [P] [F] [G] [dupdip] swoncat cons [[swap] dip [pop]] dip primrec

    paramorphism == [dupdip] swoncat cons [[swap] dip [pop]] dip primrec


```python
define('paramorphism == [dupdip] swoncat cons [[swap] dip [pop]] dip primrec')
define('factorial == 1 [1 <=] [*] [--] paramorphism')
```


```python
J('3 factorial')
```

    6


# `tails`
An example of a paramorphism for lists given in the ["Bananas..." paper](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.41.125) is `tails` which returns the list of "tails" of a list.

    [1 2 3] tails == [[] [3] [2 3]]
    
Using `paramorphism` we would write:

    n == []
    F == rest swons
    G == rest
    P == not

    tails == [] [not] [rest swons] [rest] paramorphism


```python
define('tails == [] [not] [rest swons] [rest] paramorphism')
```


```python
J('[1 2 3] tails')
```

    [[] [3] [2 3]]



```python
J('25 range tails [popop] infra [sum] map')
```

    [1 3 6 10 15 21 28 36 45 55 66 78 91 105 120 136 153 171 190 210 231 253 276]



```python
J('25 range [range_sum] map')
```

    [276 253 231 210 190 171 153 136 120 105 91 78 66 55 45 36 28 21 15 10 6 3 1 0 0]


### Factoring `rest`
Right before the recursion begins we have:
    
    [] [1 2 3] [not] [pop] [[rest swons] dupdip rest] primrec
    
But we might prefer to factor `rest` in the quote:

    [] [1 2 3] [not] [pop] [rest [swons] dupdip] primrec

There's no way to do that with the `paramorphism` combinator as defined.  We would have to write and use a slightly different recursion combinator that accepted an additional "preprocessor" function `[H]` and built:

    n swap [P] [pop] [H [F] dupdip G] primrec

Or just write it out manually.  This is yet another place where the *sufficiently smart compiler* will one day automatically refactor the code.  We could write a `paramorphism` combinator that checked `[F]` and `[G]` for common prefix and extracted it.

# Patterns of Recursion
Our story so far...

- A combiner `F :: (B, B) -> B`
- A predicate `P :: A -> Bool` to detect the base case
- A base case value `c :: B`


### Hylo- Ana-, Cata-

    w/ G :: A -> (A, B)

    H == [P   ] [pop c ] [G          ] [dip F    ] genrec
    A == [P   ] [pop []] [G          ] [dip swons] genrec
    C == [[] =] [pop c ] [uncons swap] [dip F    ] genrec

### Para-, ?-, ?-

    w/ G :: B -> B

    P == c  swap [P   ] [pop] [[F    ] dupdip G          ] primrec
    ? == [] swap [P   ] [pop] [[swons] dupdip G          ] primrec
    ? == c  swap [[] =] [pop] [[F    ] dupdip uncons swap] primrec


# Four Generalizations
There are at least four kinds of recursive combinator, depending on two choices.  The first choice is whether the combiner function should be evaluated during the recursion or pushed into the pending expression to be "collapsed" at the end.  The second choice is whether the combiner needs to operate on the current value of the datastructure or the generator's output.

    H ==        [P] [pop c] [G             ] [dip F] genrec
    H == c swap [P] [pop]   [G [F]    dip  ] [i]     genrec
    H ==        [P] [pop c] [  [G] dupdip  ] [dip F] genrec
    H == c swap [P] [pop]   [  [F] dupdip G] [i]     genrec

Consider:

    ... a G [H] dip F                w/ a G == a' b
    ... c a G [F] dip H                 a G == b  a'
    ... a [G] dupdip [H] dip F          a G == a'
    ... c a [F] dupdip G H              a G == a'

### 1

    H == [P] [pop c] [G] [dip F] genrec

Iterate n times.

    ... a [P] [pop c] [G] [dip F] genrec
    ... a  G [H] dip F
    ... a' b [H] dip F
    ... a' H b F
    ... a'  G [H] dip F b F
    ... a'' b [H] dip F b F
    ... a'' H b F b F
    ... a''  G [H] dip F b F b F
    ... a''' b [H] dip F b F b F
    ... a''' H b F b F b F
    ... a''' pop c b F b F b F
    ... c b F b F b F

This form builds up a continuation that contains the intermediate results along with the pending combiner functions.  When the base case is reached the last term is replaced by the identity value c and the continuation "collapses" into the final result.

### 2
When you can start with the identity value c on the stack and the combiner can operate as you go, using the intermediate results immediately rather than queuing them up, use this form.  An important difference is that the generator function must return its results in the reverse order.

    H == c swap [P] [pop] [G [F] dip] primrec

    ... c a G [F] dip H
    ... c b a' [F] dip H
    ... c b F a' H
    ... c b F a' G [F] dip H
    ... c b F b a'' [F] dip H
    ... c b F b F a'' H
    ... c b F b F a'' G [F] dip H
    ... c b F b F b a''' [F] dip H
    ... c b F b F b F a''' H
    ... c b F b F b F a''' pop
    ... c b F b F b F

The end line here is the same as for above, but only because we didn't evaluate `F` when it normally would have been.

### 3
If the combiner and the generator both need to work on the current value then `dup` must be used at some point, and the generator must produce one item instead of two (the b is instead the duplicate of a.)


    H == [P] [pop c] [[G] dupdip] [dip F] genrec

    ... a [G] dupdip [H] dip F
    ... a  G a       [H] dip F
    ... a'   a       [H] dip F
    ... a' H a F
    ... a' [G] dupdip [H] dip F a F
    ... a'  G  a'     [H] dip F a F
    ... a''    a'     [H] dip F a F
    ... a'' H  a' F a F
    ... a'' [G] dupdip [H] dip F a' F a F
    ... a''  G  a''    [H] dip F a' F a F
    ... a'''    a''    [H] dip F a' F a F
    ... a''' H  a'' F a' F a F
    ... a''' pop c  a'' F a' F a F
    ...          c  a'' F a' F a F

### 4
And, last but not least, if you can combine as you go, starting with c, and the combiner needs to work on the current item this is the form:

    W == c swap [P] [pop] [[F] dupdip G] primrec

    ... a c swap [P] [pop] [[F] dupdip G] primrec
    ... c a [P] [pop] [[F] dupdip G] primrec
    ... c a [F] dupdip G W
    ... c a  F a G W
    ... c a  F a'  W
    ... c a  F a'  [F] dupdip G W
    ... c a  F a'   F  a'     G W
    ... c a  F a'   F  a''      W
    ... c a  F a'   F  a''      [F] dupdip G W
    ... c a  F a'   F  a''       F  a''    G W
    ... c a  F a'   F  a''       F  a'''     W
    ... c a  F a'   F  a''       F  a'''     pop
    ... c a  F a'   F  a''       F

Each of the four variations above can be specialized to ana- and catamorphic forms.


```python
def WTFmorphism(c, F, P, G):
    '''Return a hylomorphism function H.'''

    def H(a, d=c):
        if P(a):
            result = d
        else:
            a, b = G(a)
            result = H(a, F(d, b))
        return result

    return H
```


```python
F = lambda a, b: a + b
P = lambda n: n <= 1
G = lambda n: (n - 1, n - 1)

wtf = WTFmorphism(0, F, P, G)

print wtf(5)
```

    10


    H == [P   ] [pop c ] [G          ] [dip F    ] genrec


```python
DefinitionWrapper.add_definitions('''
P == 1 <=
Ga == -- dup
Gb == --
c == 0
F == +
''', D)
```


```python
V('[1 2 3] [[] =] [pop []] [uncons swap] [dip swons] genrec')
```

                                                                                                                 . [1 2 3] [[] =] [pop []] [uncons swap] [dip swons] genrec
                                                                                                         [1 2 3] . [[] =] [pop []] [uncons swap] [dip swons] genrec
                                                                                                  [1 2 3] [[] =] . [pop []] [uncons swap] [dip swons] genrec
                                                                                         [1 2 3] [[] =] [pop []] . [uncons swap] [dip swons] genrec
                                                                           [1 2 3] [[] =] [pop []] [uncons swap] . [dip swons] genrec
                                                               [1 2 3] [[] =] [pop []] [uncons swap] [dip swons] . genrec
              [1 2 3] [[] =] [pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] . ifte
    [1 2 3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] [[1 2 3]] [[] =] . infra first choice i
                                                                                                         [1 2 3] . [] = [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [1 2 3]] swaack first choice i
                                                                                                      [1 2 3] [] . = [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [1 2 3]] swaack first choice i
                                                                                                           False . [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [1 2 3]] swaack first choice i
             False [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [1 2 3]] . swaack first choice i
             [1 2 3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] [False] . first choice i
               [1 2 3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] False . choice i
                              [1 2 3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] . i
                                                                                                         [1 2 3] . uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons
                                                                                                         1 [2 3] . swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons
                                                                                                         [2 3] 1 . [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons
                                                      [2 3] 1 [[[] =] [pop []] [uncons swap] [dip swons] genrec] . dip swons
                                                                                                           [2 3] . [[] =] [pop []] [uncons swap] [dip swons] genrec 1 swons
                                                                                                    [2 3] [[] =] . [pop []] [uncons swap] [dip swons] genrec 1 swons
                                                                                           [2 3] [[] =] [pop []] . [uncons swap] [dip swons] genrec 1 swons
                                                                             [2 3] [[] =] [pop []] [uncons swap] . [dip swons] genrec 1 swons
                                                                 [2 3] [[] =] [pop []] [uncons swap] [dip swons] . genrec 1 swons
                [2 3] [[] =] [pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] . ifte 1 swons
        [2 3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] [[2 3]] [[] =] . infra first choice i 1 swons
                                                                                                           [2 3] . [] = [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [2 3]] swaack first choice i 1 swons
                                                                                                        [2 3] [] . = [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [2 3]] swaack first choice i 1 swons
                                                                                                           False . [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [2 3]] swaack first choice i 1 swons
               False [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [2 3]] . swaack first choice i 1 swons
               [2 3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 1 swons
                 [2 3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] False . choice i 1 swons
                                [2 3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] . i 1 swons
                                                                                                           [2 3] . uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons 1 swons
                                                                                                           2 [3] . swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons 1 swons
                                                                                                           [3] 2 . [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons 1 swons
                                                        [3] 2 [[[] =] [pop []] [uncons swap] [dip swons] genrec] . dip swons 1 swons
                                                                                                             [3] . [[] =] [pop []] [uncons swap] [dip swons] genrec 2 swons 1 swons
                                                                                                      [3] [[] =] . [pop []] [uncons swap] [dip swons] genrec 2 swons 1 swons
                                                                                             [3] [[] =] [pop []] . [uncons swap] [dip swons] genrec 2 swons 1 swons
                                                                               [3] [[] =] [pop []] [uncons swap] . [dip swons] genrec 2 swons 1 swons
                                                                   [3] [[] =] [pop []] [uncons swap] [dip swons] . genrec 2 swons 1 swons
                  [3] [[] =] [pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] . ifte 2 swons 1 swons
            [3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] [[3]] [[] =] . infra first choice i 2 swons 1 swons
                                                                                                             [3] . [] = [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [3]] swaack first choice i 2 swons 1 swons
                                                                                                          [3] [] . = [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [3]] swaack first choice i 2 swons 1 swons
                                                                                                           False . [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [3]] swaack first choice i 2 swons 1 swons
                 False [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [3]] . swaack first choice i 2 swons 1 swons
                 [3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 2 swons 1 swons
                   [3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] False . choice i 2 swons 1 swons
                                  [3] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] . i 2 swons 1 swons
                                                                                                             [3] . uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons 2 swons 1 swons
                                                                                                            3 [] . swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons 2 swons 1 swons
                                                                                                            [] 3 . [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons 2 swons 1 swons
                                                         [] 3 [[[] =] [pop []] [uncons swap] [dip swons] genrec] . dip swons 2 swons 1 swons
                                                                                                              [] . [[] =] [pop []] [uncons swap] [dip swons] genrec 3 swons 2 swons 1 swons
                                                                                                       [] [[] =] . [pop []] [uncons swap] [dip swons] genrec 3 swons 2 swons 1 swons
                                                                                              [] [[] =] [pop []] . [uncons swap] [dip swons] genrec 3 swons 2 swons 1 swons
                                                                                [] [[] =] [pop []] [uncons swap] . [dip swons] genrec 3 swons 2 swons 1 swons
                                                                    [] [[] =] [pop []] [uncons swap] [dip swons] . genrec 3 swons 2 swons 1 swons
                   [] [[] =] [pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] . ifte 3 swons 2 swons 1 swons
              [] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] [[]] [[] =] . infra first choice i 3 swons 2 swons 1 swons
                                                                                                              [] . [] = [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] []] swaack first choice i 3 swons 2 swons 1 swons
                                                                                                           [] [] . = [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] []] swaack first choice i 3 swons 2 swons 1 swons
                                                                                                            True . [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] []] swaack first choice i 3 swons 2 swons 1 swons
                   True [[pop []] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] []] . swaack first choice i 3 swons 2 swons 1 swons
                   [] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] [True] . first choice i 3 swons 2 swons 1 swons
                     [] [uncons swap [[[] =] [pop []] [uncons swap] [dip swons] genrec] dip swons] [pop []] True . choice i 3 swons 2 swons 1 swons
                                                                                                     [] [pop []] . i 3 swons 2 swons 1 swons
                                                                                                              [] . pop [] 3 swons 2 swons 1 swons
                                                                                                                 . [] 3 swons 2 swons 1 swons
                                                                                                              [] . 3 swons 2 swons 1 swons
                                                                                                            [] 3 . swons 2 swons 1 swons
                                                                                                            [] 3 . swap cons 2 swons 1 swons
                                                                                                            3 [] . cons 2 swons 1 swons
                                                                                                             [3] . 2 swons 1 swons
                                                                                                           [3] 2 . swons 1 swons
                                                                                                           [3] 2 . swap cons 1 swons
                                                                                                           2 [3] . cons 1 swons
                                                                                                           [2 3] . 1 swons
                                                                                                         [2 3] 1 . swons
                                                                                                         [2 3] 1 . swap cons
                                                                                                         1 [2 3] . cons
                                                                                                         [1 2 3] . 



```python
V('3 [P] [pop c] [Ga] [dip F] genrec')
```

                                                                   . 3 [P] [pop c] [Ga] [dip F] genrec
                                                                 3 . [P] [pop c] [Ga] [dip F] genrec
                                                             3 [P] . [pop c] [Ga] [dip F] genrec
                                                     3 [P] [pop c] . [Ga] [dip F] genrec
                                                3 [P] [pop c] [Ga] . [dip F] genrec
                                        3 [P] [pop c] [Ga] [dip F] . genrec
        3 [P] [pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] . ifte
    3 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] [pop c] [3] [P] . infra first choice i
                                                                 3 . P [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 3] swaack first choice i
                                                                 3 . 1 <= [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 3] swaack first choice i
                                                               3 1 . <= [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 3] swaack first choice i
                                                             False . [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 3] swaack first choice i
    False [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 3] . swaack first choice i
    3 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] [pop c] [False] . first choice i
      3 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] [pop c] False . choice i
                    3 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] . i
                                                                 3 . Ga [[P] [pop c] [Ga] [dip F] genrec] dip F
                                                                 3 . -- dup [[P] [pop c] [Ga] [dip F] genrec] dip F
                                                                 2 . dup [[P] [pop c] [Ga] [dip F] genrec] dip F
                                                               2 2 . [[P] [pop c] [Ga] [dip F] genrec] dip F
                             2 2 [[P] [pop c] [Ga] [dip F] genrec] . dip F
                                                                 2 . [P] [pop c] [Ga] [dip F] genrec 2 F
                                                             2 [P] . [pop c] [Ga] [dip F] genrec 2 F
                                                     2 [P] [pop c] . [Ga] [dip F] genrec 2 F
                                                2 [P] [pop c] [Ga] . [dip F] genrec 2 F
                                        2 [P] [pop c] [Ga] [dip F] . genrec 2 F
        2 [P] [pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] . ifte 2 F
    2 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] [pop c] [2] [P] . infra first choice i 2 F
                                                                 2 . P [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 2] swaack first choice i 2 F
                                                                 2 . 1 <= [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 2] swaack first choice i 2 F
                                                               2 1 . <= [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 2] swaack first choice i 2 F
                                                             False . [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 2] swaack first choice i 2 F
    False [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 2] . swaack first choice i 2 F
    2 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] [pop c] [False] . first choice i 2 F
      2 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] [pop c] False . choice i 2 F
                    2 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] . i 2 F
                                                                 2 . Ga [[P] [pop c] [Ga] [dip F] genrec] dip F 2 F
                                                                 2 . -- dup [[P] [pop c] [Ga] [dip F] genrec] dip F 2 F
                                                                 1 . dup [[P] [pop c] [Ga] [dip F] genrec] dip F 2 F
                                                               1 1 . [[P] [pop c] [Ga] [dip F] genrec] dip F 2 F
                             1 1 [[P] [pop c] [Ga] [dip F] genrec] . dip F 2 F
                                                                 1 . [P] [pop c] [Ga] [dip F] genrec 1 F 2 F
                                                             1 [P] . [pop c] [Ga] [dip F] genrec 1 F 2 F
                                                     1 [P] [pop c] . [Ga] [dip F] genrec 1 F 2 F
                                                1 [P] [pop c] [Ga] . [dip F] genrec 1 F 2 F
                                        1 [P] [pop c] [Ga] [dip F] . genrec 1 F 2 F
        1 [P] [pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] . ifte 1 F 2 F
    1 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] [pop c] [1] [P] . infra first choice i 1 F 2 F
                                                                 1 . P [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 1] swaack first choice i 1 F 2 F
                                                                 1 . 1 <= [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 1] swaack first choice i 1 F 2 F
                                                               1 1 . <= [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 1] swaack first choice i 1 F 2 F
                                                              True . [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 1] swaack first choice i 1 F 2 F
     True [[pop c] [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] 1] . swaack first choice i 1 F 2 F
     1 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] [pop c] [True] . first choice i 1 F 2 F
       1 [Ga [[P] [pop c] [Ga] [dip F] genrec] dip F] [pop c] True . choice i 1 F 2 F
                                                         1 [pop c] . i 1 F 2 F
                                                                 1 . pop c 1 F 2 F
                                                                   . c 1 F 2 F
                                                                   . 0 1 F 2 F
                                                                 0 . 1 F 2 F
                                                               0 1 . F 2 F
                                                               0 1 . + 2 F
                                                                 1 . 2 F
                                                               1 2 . F
                                                               1 2 . +
                                                                 3 . 



```python
V('3 [P] [pop []] [Ga] [dip swons] genrec')
```

                                                                             . 3 [P] [pop []] [Ga] [dip swons] genrec
                                                                           3 . [P] [pop []] [Ga] [dip swons] genrec
                                                                       3 [P] . [pop []] [Ga] [dip swons] genrec
                                                              3 [P] [pop []] . [Ga] [dip swons] genrec
                                                         3 [P] [pop []] [Ga] . [dip swons] genrec
                                             3 [P] [pop []] [Ga] [dip swons] . genrec
        3 [P] [pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] . ifte
    3 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] [pop []] [3] [P] . infra first choice i
                                                                           3 . P [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 3] swaack first choice i
                                                                           3 . 1 <= [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 3] swaack first choice i
                                                                         3 1 . <= [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 3] swaack first choice i
                                                                       False . [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 3] swaack first choice i
    False [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 3] . swaack first choice i
    3 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] [pop []] [False] . first choice i
      3 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] [pop []] False . choice i
                     3 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] . i
                                                                           3 . Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons
                                                                           3 . -- dup [[P] [pop []] [Ga] [dip swons] genrec] dip swons
                                                                           2 . dup [[P] [pop []] [Ga] [dip swons] genrec] dip swons
                                                                         2 2 . [[P] [pop []] [Ga] [dip swons] genrec] dip swons
                                  2 2 [[P] [pop []] [Ga] [dip swons] genrec] . dip swons
                                                                           2 . [P] [pop []] [Ga] [dip swons] genrec 2 swons
                                                                       2 [P] . [pop []] [Ga] [dip swons] genrec 2 swons
                                                              2 [P] [pop []] . [Ga] [dip swons] genrec 2 swons
                                                         2 [P] [pop []] [Ga] . [dip swons] genrec 2 swons
                                             2 [P] [pop []] [Ga] [dip swons] . genrec 2 swons
        2 [P] [pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] . ifte 2 swons
    2 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] [pop []] [2] [P] . infra first choice i 2 swons
                                                                           2 . P [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 2] swaack first choice i 2 swons
                                                                           2 . 1 <= [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 2] swaack first choice i 2 swons
                                                                         2 1 . <= [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 2] swaack first choice i 2 swons
                                                                       False . [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 2] swaack first choice i 2 swons
    False [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 2] . swaack first choice i 2 swons
    2 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] [pop []] [False] . first choice i 2 swons
      2 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] [pop []] False . choice i 2 swons
                     2 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] . i 2 swons
                                                                           2 . Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons 2 swons
                                                                           2 . -- dup [[P] [pop []] [Ga] [dip swons] genrec] dip swons 2 swons
                                                                           1 . dup [[P] [pop []] [Ga] [dip swons] genrec] dip swons 2 swons
                                                                         1 1 . [[P] [pop []] [Ga] [dip swons] genrec] dip swons 2 swons
                                  1 1 [[P] [pop []] [Ga] [dip swons] genrec] . dip swons 2 swons
                                                                           1 . [P] [pop []] [Ga] [dip swons] genrec 1 swons 2 swons
                                                                       1 [P] . [pop []] [Ga] [dip swons] genrec 1 swons 2 swons
                                                              1 [P] [pop []] . [Ga] [dip swons] genrec 1 swons 2 swons
                                                         1 [P] [pop []] [Ga] . [dip swons] genrec 1 swons 2 swons
                                             1 [P] [pop []] [Ga] [dip swons] . genrec 1 swons 2 swons
        1 [P] [pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] . ifte 1 swons 2 swons
    1 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] [pop []] [1] [P] . infra first choice i 1 swons 2 swons
                                                                           1 . P [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 1] swaack first choice i 1 swons 2 swons
                                                                           1 . 1 <= [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 1] swaack first choice i 1 swons 2 swons
                                                                         1 1 . <= [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 1] swaack first choice i 1 swons 2 swons
                                                                        True . [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 1] swaack first choice i 1 swons 2 swons
     True [[pop []] [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] 1] . swaack first choice i 1 swons 2 swons
     1 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] [pop []] [True] . first choice i 1 swons 2 swons
       1 [Ga [[P] [pop []] [Ga] [dip swons] genrec] dip swons] [pop []] True . choice i 1 swons 2 swons
                                                                  1 [pop []] . i 1 swons 2 swons
                                                                           1 . pop [] 1 swons 2 swons
                                                                             . [] 1 swons 2 swons
                                                                          [] . 1 swons 2 swons
                                                                        [] 1 . swons 2 swons
                                                                        [] 1 . swap cons 2 swons
                                                                        1 [] . cons 2 swons
                                                                         [1] . 2 swons
                                                                       [1] 2 . swons
                                                                       [1] 2 . swap cons
                                                                       2 [1] . cons
                                                                       [2 1] . 



```python
V('[2 1] [[] =] [pop c ] [uncons swap] [dip F] genrec')
```

                                                                                                   . [2 1] [[] =] [pop c] [uncons swap] [dip F] genrec
                                                                                             [2 1] . [[] =] [pop c] [uncons swap] [dip F] genrec
                                                                                      [2 1] [[] =] . [pop c] [uncons swap] [dip F] genrec
                                                                              [2 1] [[] =] [pop c] . [uncons swap] [dip F] genrec
                                                                [2 1] [[] =] [pop c] [uncons swap] . [dip F] genrec
                                                        [2 1] [[] =] [pop c] [uncons swap] [dip F] . genrec
            [2 1] [[] =] [pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] . ifte
    [2 1] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [pop c] [[2 1]] [[] =] . infra first choice i
                                                                                             [2 1] . [] = [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [2 1]] swaack first choice i
                                                                                          [2 1] [] . = [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [2 1]] swaack first choice i
                                                                                             False . [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [2 1]] swaack first choice i
           False [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [2 1]] . swaack first choice i
           [2 1] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [pop c] [False] . first choice i
             [2 1] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [pop c] False . choice i
                           [2 1] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] . i
                                                                                             [2 1] . uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F
                                                                                             2 [1] . swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F
                                                                                             [1] 2 . [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F
                                               [1] 2 [[[] =] [pop c] [uncons swap] [dip F] genrec] . dip F
                                                                                               [1] . [[] =] [pop c] [uncons swap] [dip F] genrec 2 F
                                                                                        [1] [[] =] . [pop c] [uncons swap] [dip F] genrec 2 F
                                                                                [1] [[] =] [pop c] . [uncons swap] [dip F] genrec 2 F
                                                                  [1] [[] =] [pop c] [uncons swap] . [dip F] genrec 2 F
                                                          [1] [[] =] [pop c] [uncons swap] [dip F] . genrec 2 F
              [1] [[] =] [pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] . ifte 2 F
        [1] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [pop c] [[1]] [[] =] . infra first choice i 2 F
                                                                                               [1] . [] = [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [1]] swaack first choice i 2 F
                                                                                            [1] [] . = [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [1]] swaack first choice i 2 F
                                                                                             False . [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [1]] swaack first choice i 2 F
             False [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [1]] . swaack first choice i 2 F
             [1] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [pop c] [False] . first choice i 2 F
               [1] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [pop c] False . choice i 2 F
                             [1] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] . i 2 F
                                                                                               [1] . uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F 2 F
                                                                                              1 [] . swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F 2 F
                                                                                              [] 1 . [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F 2 F
                                                [] 1 [[[] =] [pop c] [uncons swap] [dip F] genrec] . dip F 2 F
                                                                                                [] . [[] =] [pop c] [uncons swap] [dip F] genrec 1 F 2 F
                                                                                         [] [[] =] . [pop c] [uncons swap] [dip F] genrec 1 F 2 F
                                                                                 [] [[] =] [pop c] . [uncons swap] [dip F] genrec 1 F 2 F
                                                                   [] [[] =] [pop c] [uncons swap] . [dip F] genrec 1 F 2 F
                                                           [] [[] =] [pop c] [uncons swap] [dip F] . genrec 1 F 2 F
               [] [[] =] [pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] . ifte 1 F 2 F
          [] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [pop c] [[]] [[] =] . infra first choice i 1 F 2 F
                                                                                                [] . [] = [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] []] swaack first choice i 1 F 2 F
                                                                                             [] [] . = [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] []] swaack first choice i 1 F 2 F
                                                                                              True . [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] []] swaack first choice i 1 F 2 F
               True [[pop c] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] []] . swaack first choice i 1 F 2 F
               [] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [pop c] [True] . first choice i 1 F 2 F
                 [] [uncons swap [[[] =] [pop c] [uncons swap] [dip F] genrec] dip F] [pop c] True . choice i 1 F 2 F
                                                                                        [] [pop c] . i 1 F 2 F
                                                                                                [] . pop c 1 F 2 F
                                                                                                   . c 1 F 2 F
                                                                                                   . 0 1 F 2 F
                                                                                                 0 . 1 F 2 F
                                                                                               0 1 . F 2 F
                                                                                               0 1 . + 2 F
                                                                                                 1 . 2 F
                                                                                               1 2 . F
                                                                                               1 2 . +
                                                                                                 3 . 


## Appendix - Fun with Symbols

    |[ (c, F), (G, P) ]| == (|c, F|) • [(G, P)]

["Bananas, Lenses, & Barbed Wire"](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.41.125)

    (|...|)  [(...)]  [<...>]

I think they are having slightly too much fun with the symbols.

"Too much is always better than not enough."

# Tree with node and list of trees.

    tree = [] | [node [tree*]]

### `treestep`

    tree z [C] [N] treestep


       [] z [C] [N] treestep
    ---------------------------
          z


       [node [tree*]] z [C] [N] treestep
    --------------------------------------- w/ K == z [C] [N] treestep
           node N [tree*] [K] map C

### Derive the recursive form.
    K == [not] [pop z] [J] ifte


           [node [tree*]] J
    ------------------------------
       node N [tree*] [K] map C


    J == .. [N] .. [K] .. [C] ..

    [node [tree*]] uncons [N] dip
    node [[tree*]]        [N] dip
    node N [[tree*]]

    node N [[tree*]] i [K] map
    node N  [tree*]    [K] map
    node N  [K.tree*]

    J == uncons [N] dip i [K] map [C] i

    K == [not] [pop z] [uncons [N] dip i [K] map [C] i] ifte
    K == [not] [pop z] [uncons [N] dip i]   [map [C] i] genrec

### Extract the givens to parameterize the program.
    [not] [pop z]                   [uncons [N] dip unquote] [map [C] i] genrec
    [not] [z]         [pop] swoncat [uncons [N] dip unquote] [map [C] i] genrec
    [not]  z     unit [pop] swoncat [uncons [N] dip unquote] [map [C] i] genrec
    z [not] swap unit [pop] swoncat [uncons [N] dip unquote] [map [C] i] genrec
      \............TS0............/
    z TS0 [uncons [N] dip unquote]                      [map [C] i] genrec
    z [uncons [N] dip unquote]                [TS0] dip [map [C] i] genrec
    z [[N] dip unquote]      [uncons] swoncat [TS0] dip [map [C] i] genrec
    z [N] [dip unquote] cons [uncons] swoncat [TS0] dip [map [C] i] genrec
          \...........TS1.................../
    z [N] TS1 [TS0] dip [map [C] i]                       genrec
    z [N]               [map [C] i]            [TS1 [TS0] dip] dip      genrec
    z [N]               [map  C   ]            [TS1 [TS0] dip] dip      genrec
    z [N]                    [C] [map] swoncat [TS1 [TS0] dip] dip genrec
    z [C] [N] swap               [map] swoncat [TS1 [TS0] dip] dip genrec

         TS0 == [not] swap unit [pop] swoncat
         TS1 == [dip i] cons [uncons] swoncat
    treestep == swap [map] swoncat [TS1 [TS0] dip] dip genrec

       [] 0 [C] [N] treestep
    ---------------------------
          0


          [n [tree*]] 0 [sum +] [] treestep
       --------------------------------------------------
           n [tree*] [0 [sum +] [] treestep] map sum +


```python
DefinitionWrapper.add_definitions('''

     TS0 == [not] swap unit [pop] swoncat
     TS1 == [dip i] cons [uncons] swoncat
treestep == swap [map] swoncat [TS1 [TS0] dip] dip genrec

''', D)
```


```python
V('[] 0 [sum +] [] treestep')
```

                                                                                                           . [] 0 [sum +] [] treestep
                                                                                                        [] . 0 [sum +] [] treestep
                                                                                                      [] 0 . [sum +] [] treestep
                                                                                              [] 0 [sum +] . [] treestep
                                                                                           [] 0 [sum +] [] . treestep
                                                                                           [] 0 [sum +] [] . swap [map] swoncat [TS1 [TS0] dip] dip genrec
                                                                                           [] 0 [] [sum +] . [map] swoncat [TS1 [TS0] dip] dip genrec
                                                                                     [] 0 [] [sum +] [map] . swoncat [TS1 [TS0] dip] dip genrec
                                                                                     [] 0 [] [sum +] [map] . swap concat [TS1 [TS0] dip] dip genrec
                                                                                     [] 0 [] [map] [sum +] . concat [TS1 [TS0] dip] dip genrec
                                                                                       [] 0 [] [map sum +] . [TS1 [TS0] dip] dip genrec
                                                                       [] 0 [] [map sum +] [TS1 [TS0] dip] . dip genrec
                                                                                                   [] 0 [] . TS1 [TS0] dip [map sum +] genrec
                                                                                                   [] 0 [] . [dip i] cons [uncons] swoncat [TS0] dip [map sum +] genrec
                                                                                           [] 0 [] [dip i] . cons [uncons] swoncat [TS0] dip [map sum +] genrec
                                                                                           [] 0 [[] dip i] . [uncons] swoncat [TS0] dip [map sum +] genrec
                                                                                  [] 0 [[] dip i] [uncons] . swoncat [TS0] dip [map sum +] genrec
                                                                                  [] 0 [[] dip i] [uncons] . swap concat [TS0] dip [map sum +] genrec
                                                                                  [] 0 [uncons] [[] dip i] . concat [TS0] dip [map sum +] genrec
                                                                                    [] 0 [uncons [] dip i] . [TS0] dip [map sum +] genrec
                                                                              [] 0 [uncons [] dip i] [TS0] . dip [map sum +] genrec
                                                                                                      [] 0 . TS0 [uncons [] dip i] [map sum +] genrec
                                                                                                      [] 0 . [not] swap unit [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                [] 0 [not] . swap unit [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                [] [not] 0 . unit [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                [] [not] 0 . [] cons [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                             [] [not] 0 [] . cons [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                              [] [not] [0] . [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                        [] [not] [0] [pop] . swoncat [uncons [] dip i] [map sum +] genrec
                                                                                        [] [not] [0] [pop] . swap concat [uncons [] dip i] [map sum +] genrec
                                                                                        [] [not] [pop] [0] . concat [uncons [] dip i] [map sum +] genrec
                                                                                          [] [not] [pop 0] . [uncons [] dip i] [map sum +] genrec
                                                                        [] [not] [pop 0] [uncons [] dip i] . [map sum +] genrec
                                                            [] [not] [pop 0] [uncons [] dip i] [map sum +] . genrec
         [] [not] [pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] . ifte
    [] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [[]] [not] . infra first choice i
                                                                                                        [] . not [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] []] swaack first choice i
                                                                                                      True . [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] []] swaack first choice i
        True [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] []] . swaack first choice i
        [] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [True] . first choice i
          [] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] True . choice i
                                                                                                [] [pop 0] . i
                                                                                                        [] . pop 0
                                                                                                           . 0
                                                                                                         0 . 



```python
V('[23 []] 0 [sum +] [] treestep')
```

                                                                                                                     . [23 []] 0 [sum +] [] treestep
                                                                                                             [23 []] . 0 [sum +] [] treestep
                                                                                                           [23 []] 0 . [sum +] [] treestep
                                                                                                   [23 []] 0 [sum +] . [] treestep
                                                                                                [23 []] 0 [sum +] [] . treestep
                                                                                                [23 []] 0 [sum +] [] . swap [map] swoncat [TS1 [TS0] dip] dip genrec
                                                                                                [23 []] 0 [] [sum +] . [map] swoncat [TS1 [TS0] dip] dip genrec
                                                                                          [23 []] 0 [] [sum +] [map] . swoncat [TS1 [TS0] dip] dip genrec
                                                                                          [23 []] 0 [] [sum +] [map] . swap concat [TS1 [TS0] dip] dip genrec
                                                                                          [23 []] 0 [] [map] [sum +] . concat [TS1 [TS0] dip] dip genrec
                                                                                            [23 []] 0 [] [map sum +] . [TS1 [TS0] dip] dip genrec
                                                                            [23 []] 0 [] [map sum +] [TS1 [TS0] dip] . dip genrec
                                                                                                        [23 []] 0 [] . TS1 [TS0] dip [map sum +] genrec
                                                                                                        [23 []] 0 [] . [dip i] cons [uncons] swoncat [TS0] dip [map sum +] genrec
                                                                                                [23 []] 0 [] [dip i] . cons [uncons] swoncat [TS0] dip [map sum +] genrec
                                                                                                [23 []] 0 [[] dip i] . [uncons] swoncat [TS0] dip [map sum +] genrec
                                                                                       [23 []] 0 [[] dip i] [uncons] . swoncat [TS0] dip [map sum +] genrec
                                                                                       [23 []] 0 [[] dip i] [uncons] . swap concat [TS0] dip [map sum +] genrec
                                                                                       [23 []] 0 [uncons] [[] dip i] . concat [TS0] dip [map sum +] genrec
                                                                                         [23 []] 0 [uncons [] dip i] . [TS0] dip [map sum +] genrec
                                                                                   [23 []] 0 [uncons [] dip i] [TS0] . dip [map sum +] genrec
                                                                                                           [23 []] 0 . TS0 [uncons [] dip i] [map sum +] genrec
                                                                                                           [23 []] 0 . [not] swap unit [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                     [23 []] 0 [not] . swap unit [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                     [23 []] [not] 0 . unit [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                     [23 []] [not] 0 . [] cons [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                  [23 []] [not] 0 [] . cons [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                   [23 []] [not] [0] . [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                             [23 []] [not] [0] [pop] . swoncat [uncons [] dip i] [map sum +] genrec
                                                                                             [23 []] [not] [0] [pop] . swap concat [uncons [] dip i] [map sum +] genrec
                                                                                             [23 []] [not] [pop] [0] . concat [uncons [] dip i] [map sum +] genrec
                                                                                               [23 []] [not] [pop 0] . [uncons [] dip i] [map sum +] genrec
                                                                             [23 []] [not] [pop 0] [uncons [] dip i] . [map sum +] genrec
                                                                 [23 []] [not] [pop 0] [uncons [] dip i] [map sum +] . genrec
              [23 []] [not] [pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] . ifte
    [23 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [[23 []]] [not] . infra first choice i
                                                                                                             [23 []] . not [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [23 []]] swaack first choice i
                                                                                                               False . [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [23 []]] swaack first choice i
            False [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [23 []]] . swaack first choice i
            [23 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [False] . first choice i
              [23 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] False . choice i
                            [23 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] . i
                                                                                                             [23 []] . uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                             23 [[]] . [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                          23 [[]] [] . dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                                  23 . [[]] i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                             23 [[]] . i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                                  23 . [] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                               23 [] . [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                          23 [] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] . map sum +
                                                                                                               23 [] . sum +
                                                                                                               23 [] . 0 [+] catamorphism +
                                                                                                             23 [] 0 . [+] catamorphism +
                                                                                                         23 [] 0 [+] . catamorphism +
                                                                                                         23 [] 0 [+] . [[] =] roll> [uncons swap] swap hylomorphism +
                                                                                                  23 [] 0 [+] [[] =] . roll> [uncons swap] swap hylomorphism +
                                                                                                  23 [] [[] =] 0 [+] . [uncons swap] swap hylomorphism +
                                                                                    23 [] [[] =] 0 [+] [uncons swap] . swap hylomorphism +
                                                                                    23 [] [[] =] 0 [uncons swap] [+] . hylomorphism +
                                                                                    23 [] [[] =] 0 [uncons swap] [+] . [unit [pop] swoncat] dipd [dip] swoncat genrec +
                                                               23 [] [[] =] 0 [uncons swap] [+] [unit [pop] swoncat] . dipd [dip] swoncat genrec +
                                                                                                      23 [] [[] =] 0 . unit [pop] swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                      23 [] [[] =] 0 . [] cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                   23 [] [[] =] 0 [] . cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                    23 [] [[] =] [0] . [pop] swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                              23 [] [[] =] [0] [pop] . swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                              23 [] [[] =] [0] [pop] . swap concat [uncons swap] [+] [dip] swoncat genrec +
                                                                                              23 [] [[] =] [pop] [0] . concat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                23 [] [[] =] [pop 0] . [uncons swap] [+] [dip] swoncat genrec +
                                                                                  23 [] [[] =] [pop 0] [uncons swap] . [+] [dip] swoncat genrec +
                                                                              23 [] [[] =] [pop 0] [uncons swap] [+] . [dip] swoncat genrec +
                                                                        23 [] [[] =] [pop 0] [uncons swap] [+] [dip] . swoncat genrec +
                                                                        23 [] [[] =] [pop 0] [uncons swap] [+] [dip] . swap concat genrec +
                                                                        23 [] [[] =] [pop 0] [uncons swap] [dip] [+] . concat genrec +
                                                                          23 [] [[] =] [pop 0] [uncons swap] [dip +] . genrec +
                              23 [] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte +
                      23 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[] 23] [[] =] . infra first choice i +
                                                                                                               23 [] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 23] swaack first choice i +
                                                                                                            23 [] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 23] swaack first choice i +
                                                                                                             23 True . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 23] swaack first choice i +
                           23 True [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 23] . swaack first choice i +
                           23 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [True 23] . first choice i +
                                23 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] True . choice i +
                                                                                                       23 [] [pop 0] . i +
                                                                                                               23 [] . pop 0 +
                                                                                                                  23 . 0 +
                                                                                                                23 0 . +
                                                                                                                  23 . 



```python
V('[23 [[2 []] [3 []]]] 0 [sum +] [] treestep')
```

                                                                                                                                                                      . [23 [[2 []] [3 []]]] 0 [sum +] [] treestep
                                                                                                                                                 [23 [[2 []] [3 []]]] . 0 [sum +] [] treestep
                                                                                                                                               [23 [[2 []] [3 []]]] 0 . [sum +] [] treestep
                                                                                                                                       [23 [[2 []] [3 []]]] 0 [sum +] . [] treestep
                                                                                                                                    [23 [[2 []] [3 []]]] 0 [sum +] [] . treestep
                                                                                                                                    [23 [[2 []] [3 []]]] 0 [sum +] [] . swap [map] swoncat [TS1 [TS0] dip] dip genrec
                                                                                                                                    [23 [[2 []] [3 []]]] 0 [] [sum +] . [map] swoncat [TS1 [TS0] dip] dip genrec
                                                                                                                              [23 [[2 []] [3 []]]] 0 [] [sum +] [map] . swoncat [TS1 [TS0] dip] dip genrec
                                                                                                                              [23 [[2 []] [3 []]]] 0 [] [sum +] [map] . swap concat [TS1 [TS0] dip] dip genrec
                                                                                                                              [23 [[2 []] [3 []]]] 0 [] [map] [sum +] . concat [TS1 [TS0] dip] dip genrec
                                                                                                                                [23 [[2 []] [3 []]]] 0 [] [map sum +] . [TS1 [TS0] dip] dip genrec
                                                                                                                [23 [[2 []] [3 []]]] 0 [] [map sum +] [TS1 [TS0] dip] . dip genrec
                                                                                                                                            [23 [[2 []] [3 []]]] 0 [] . TS1 [TS0] dip [map sum +] genrec
                                                                                                                                            [23 [[2 []] [3 []]]] 0 [] . [dip i] cons [uncons] swoncat [TS0] dip [map sum +] genrec
                                                                                                                                    [23 [[2 []] [3 []]]] 0 [] [dip i] . cons [uncons] swoncat [TS0] dip [map sum +] genrec
                                                                                                                                    [23 [[2 []] [3 []]]] 0 [[] dip i] . [uncons] swoncat [TS0] dip [map sum +] genrec
                                                                                                                           [23 [[2 []] [3 []]]] 0 [[] dip i] [uncons] . swoncat [TS0] dip [map sum +] genrec
                                                                                                                           [23 [[2 []] [3 []]]] 0 [[] dip i] [uncons] . swap concat [TS0] dip [map sum +] genrec
                                                                                                                           [23 [[2 []] [3 []]]] 0 [uncons] [[] dip i] . concat [TS0] dip [map sum +] genrec
                                                                                                                             [23 [[2 []] [3 []]]] 0 [uncons [] dip i] . [TS0] dip [map sum +] genrec
                                                                                                                       [23 [[2 []] [3 []]]] 0 [uncons [] dip i] [TS0] . dip [map sum +] genrec
                                                                                                                                               [23 [[2 []] [3 []]]] 0 . TS0 [uncons [] dip i] [map sum +] genrec
                                                                                                                                               [23 [[2 []] [3 []]]] 0 . [not] swap unit [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                                                         [23 [[2 []] [3 []]]] 0 [not] . swap unit [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                                                         [23 [[2 []] [3 []]]] [not] 0 . unit [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                                                         [23 [[2 []] [3 []]]] [not] 0 . [] cons [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                                                      [23 [[2 []] [3 []]]] [not] 0 [] . cons [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                                                       [23 [[2 []] [3 []]]] [not] [0] . [pop] swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                                                 [23 [[2 []] [3 []]]] [not] [0] [pop] . swoncat [uncons [] dip i] [map sum +] genrec
                                                                                                                                 [23 [[2 []] [3 []]]] [not] [0] [pop] . swap concat [uncons [] dip i] [map sum +] genrec
                                                                                                                                 [23 [[2 []] [3 []]]] [not] [pop] [0] . concat [uncons [] dip i] [map sum +] genrec
                                                                                                                                   [23 [[2 []] [3 []]]] [not] [pop 0] . [uncons [] dip i] [map sum +] genrec
                                                                                                                 [23 [[2 []] [3 []]]] [not] [pop 0] [uncons [] dip i] . [map sum +] genrec
                                                                                                     [23 [[2 []] [3 []]]] [not] [pop 0] [uncons [] dip i] [map sum +] . genrec
                                                  [23 [[2 []] [3 []]]] [not] [pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] . ifte
                           [23 [[2 []] [3 []]]] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [[23 [[2 []] [3 []]]]] [not] . infra first choice i
                                                                                                                                                 [23 [[2 []] [3 []]]] . not [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [23 [[2 []] [3 []]]]] swaack first choice i
                                                                                                                                                                False . [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [23 [[2 []] [3 []]]]] swaack first choice i
                                                False [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [23 [[2 []] [3 []]]]] . swaack first choice i
                                                [23 [[2 []] [3 []]]] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [False] . first choice i
                                                  [23 [[2 []] [3 []]]] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] False . choice i
                                                                [23 [[2 []] [3 []]]] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] . i
                                                                                                                                                 [23 [[2 []] [3 []]]] . uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                                                                 23 [[[2 []] [3 []]]] . [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                                                              23 [[[2 []] [3 []]]] [] . dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                                                                                   23 . [[[2 []] [3 []]]] i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                                                                 23 [[[2 []] [3 []]]] . i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                                                                                   23 . [[2 []] [3 []]] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                                                                                   23 [[2 []] [3 []]] . [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +
                                                                                              23 [[2 []] [3 []]] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] . map sum +
    23 [] [[[3 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first] . infra sum +
                                                                                                                                                                      . [[3 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                          [[3 []] 23] . [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                     [[3 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] . infra first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                            23 [3 []] . [not] [pop 0] [uncons [] dip i] [map sum +] genrec [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                      23 [3 []] [not] . [pop 0] [uncons [] dip i] [map sum +] genrec [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                              23 [3 []] [not] [pop 0] . [uncons [] dip i] [map sum +] genrec [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                            23 [3 []] [not] [pop 0] [uncons [] dip i] . [map sum +] genrec [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                23 [3 []] [not] [pop 0] [uncons [] dip i] [map sum +] . genrec [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                             23 [3 []] [not] [pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] . ifte [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                 23 [3 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [[3 []] 23] [not] . infra first choice i [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                            23 [3 []] . not [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [3 []] 23] swaack first choice i [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                             23 False . [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [3 []] 23] swaack first choice i [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                        23 False [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [3 []] 23] . swaack first choice i [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                        23 [3 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [False 23] . first choice i [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                             23 [3 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] False . choice i [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                           23 [3 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] . i [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                            23 [3 []] . uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                            23 3 [[]] . [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                         23 3 [[]] [] . dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                                 23 3 . [[]] i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                            23 3 [[]] . i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                                 23 3 . [] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                              23 3 [] . [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                         23 3 [] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] . map sum + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                              23 3 [] . sum + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                              23 3 [] . 0 [+] catamorphism + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                            23 3 [] 0 . [+] catamorphism + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                        23 3 [] 0 [+] . catamorphism + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                        23 3 [] 0 [+] . [[] =] roll> [uncons swap] swap hylomorphism + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                 23 3 [] 0 [+] [[] =] . roll> [uncons swap] swap hylomorphism + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                 23 3 [] [[] =] 0 [+] . [uncons swap] swap hylomorphism + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                   23 3 [] [[] =] 0 [+] [uncons swap] . swap hylomorphism + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                   23 3 [] [[] =] 0 [uncons swap] [+] . hylomorphism + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                   23 3 [] [[] =] 0 [uncons swap] [+] . [unit [pop] swoncat] dipd [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                              23 3 [] [[] =] 0 [uncons swap] [+] [unit [pop] swoncat] . dipd [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                     23 3 [] [[] =] 0 . unit [pop] swoncat [uncons swap] [+] [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                     23 3 [] [[] =] 0 . [] cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                  23 3 [] [[] =] 0 [] . cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                   23 3 [] [[] =] [0] . [pop] swoncat [uncons swap] [+] [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                             23 3 [] [[] =] [0] [pop] . swoncat [uncons swap] [+] [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                             23 3 [] [[] =] [0] [pop] . swap concat [uncons swap] [+] [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                             23 3 [] [[] =] [pop] [0] . concat [uncons swap] [+] [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                               23 3 [] [[] =] [pop 0] . [uncons swap] [+] [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                 23 3 [] [[] =] [pop 0] [uncons swap] . [+] [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                             23 3 [] [[] =] [pop 0] [uncons swap] [+] . [dip] swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                       23 3 [] [[] =] [pop 0] [uncons swap] [+] [dip] . swoncat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                       23 3 [] [[] =] [pop 0] [uncons swap] [+] [dip] . swap concat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                       23 3 [] [[] =] [pop 0] [uncons swap] [dip] [+] . concat genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                         23 3 [] [[] =] [pop 0] [uncons swap] [dip +] . genrec + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                             23 3 [] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                   23 3 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[] 3 23] [[] =] . infra first choice i + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                              23 3 [] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 3 23] swaack first choice i + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                           23 3 [] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 3 23] swaack first choice i + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                            23 3 True . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 3 23] swaack first choice i + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                        23 3 True [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 3 23] . swaack first choice i + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                        23 3 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [True 3 23] . first choice i + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                               23 3 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] True . choice i + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                      23 3 [] [pop 0] . i + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                              23 3 [] . pop 0 + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                                 23 3 . 0 + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                               23 3 0 . + [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                                 23 3 . [] swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                              23 3 [] . swaack first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                               [3 23] . first [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                                    3 . [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                                                                        3 [[2 []] 23] . [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] infra first [23] swaack sum +
                                                                                                   3 [[2 []] 23] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] . infra first [23] swaack sum +
                                                                                                                                                            23 [2 []] . [not] [pop 0] [uncons [] dip i] [map sum +] genrec [3] swaack first [23] swaack sum +
                                                                                                                                                      23 [2 []] [not] . [pop 0] [uncons [] dip i] [map sum +] genrec [3] swaack first [23] swaack sum +
                                                                                                                                              23 [2 []] [not] [pop 0] . [uncons [] dip i] [map sum +] genrec [3] swaack first [23] swaack sum +
                                                                                                                            23 [2 []] [not] [pop 0] [uncons [] dip i] . [map sum +] genrec [3] swaack first [23] swaack sum +
                                                                                                                23 [2 []] [not] [pop 0] [uncons [] dip i] [map sum +] . genrec [3] swaack first [23] swaack sum +
                                                             23 [2 []] [not] [pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] . ifte [3] swaack first [23] swaack sum +
                                                 23 [2 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [[2 []] 23] [not] . infra first choice i [3] swaack first [23] swaack sum +
                                                                                                                                                            23 [2 []] . not [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [2 []] 23] swaack first choice i [3] swaack first [23] swaack sum +
                                                                                                                                                             23 False . [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [2 []] 23] swaack first choice i [3] swaack first [23] swaack sum +
                                                        23 False [[pop 0] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [2 []] 23] . swaack first choice i [3] swaack first [23] swaack sum +
                                                        23 [2 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] [False 23] . first choice i [3] swaack first [23] swaack sum +
                                                             23 [2 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] [pop 0] False . choice i [3] swaack first [23] swaack sum +
                                                                           23 [2 []] [uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum +] . i [3] swaack first [23] swaack sum +
                                                                                                                                                            23 [2 []] . uncons [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [3] swaack first [23] swaack sum +
                                                                                                                                                            23 2 [[]] . [] dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [3] swaack first [23] swaack sum +
                                                                                                                                                         23 2 [[]] [] . dip i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [3] swaack first [23] swaack sum +
                                                                                                                                                                 23 2 . [[]] i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [3] swaack first [23] swaack sum +
                                                                                                                                                            23 2 [[]] . i [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [3] swaack first [23] swaack sum +
                                                                                                                                                                 23 2 . [] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [3] swaack first [23] swaack sum +
                                                                                                                                                              23 2 [] . [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] map sum + [3] swaack first [23] swaack sum +
                                                                                                         23 2 [] [[not] [pop 0] [uncons [] dip i] [map sum +] genrec] . map sum + [3] swaack first [23] swaack sum +
                                                                                                                                                              23 2 [] . sum + [3] swaack first [23] swaack sum +
                                                                                                                                                              23 2 [] . 0 [+] catamorphism + [3] swaack first [23] swaack sum +
                                                                                                                                                            23 2 [] 0 . [+] catamorphism + [3] swaack first [23] swaack sum +
                                                                                                                                                        23 2 [] 0 [+] . catamorphism + [3] swaack first [23] swaack sum +
                                                                                                                                                        23 2 [] 0 [+] . [[] =] roll> [uncons swap] swap hylomorphism + [3] swaack first [23] swaack sum +
                                                                                                                                                 23 2 [] 0 [+] [[] =] . roll> [uncons swap] swap hylomorphism + [3] swaack first [23] swaack sum +
                                                                                                                                                 23 2 [] [[] =] 0 [+] . [uncons swap] swap hylomorphism + [3] swaack first [23] swaack sum +
                                                                                                                                   23 2 [] [[] =] 0 [+] [uncons swap] . swap hylomorphism + [3] swaack first [23] swaack sum +
                                                                                                                                   23 2 [] [[] =] 0 [uncons swap] [+] . hylomorphism + [3] swaack first [23] swaack sum +
                                                                                                                                   23 2 [] [[] =] 0 [uncons swap] [+] . [unit [pop] swoncat] dipd [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                              23 2 [] [[] =] 0 [uncons swap] [+] [unit [pop] swoncat] . dipd [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                                                     23 2 [] [[] =] 0 . unit [pop] swoncat [uncons swap] [+] [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                                                     23 2 [] [[] =] 0 . [] cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                                                  23 2 [] [[] =] 0 [] . cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                                                   23 2 [] [[] =] [0] . [pop] swoncat [uncons swap] [+] [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                                             23 2 [] [[] =] [0] [pop] . swoncat [uncons swap] [+] [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                                             23 2 [] [[] =] [0] [pop] . swap concat [uncons swap] [+] [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                                             23 2 [] [[] =] [pop] [0] . concat [uncons swap] [+] [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                                               23 2 [] [[] =] [pop 0] . [uncons swap] [+] [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                                 23 2 [] [[] =] [pop 0] [uncons swap] . [+] [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                             23 2 [] [[] =] [pop 0] [uncons swap] [+] . [dip] swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                       23 2 [] [[] =] [pop 0] [uncons swap] [+] [dip] . swoncat genrec + [3] swaack first [23] swaack sum +
                                                                                                                       23 2 [] [[] =] [pop 0] [uncons swap] [+] [dip] . swap concat genrec + [3] swaack first [23] swaack sum +
                                                                                                                       23 2 [] [[] =] [pop 0] [uncons swap] [dip] [+] . concat genrec + [3] swaack first [23] swaack sum +
                                                                                                                         23 2 [] [[] =] [pop 0] [uncons swap] [dip +] . genrec + [3] swaack first [23] swaack sum +
                                                                             23 2 [] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte + [3] swaack first [23] swaack sum +
                                                                   23 2 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[] 2 23] [[] =] . infra first choice i + [3] swaack first [23] swaack sum +
                                                                                                                                                              23 2 [] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 2 23] swaack first choice i + [3] swaack first [23] swaack sum +
                                                                                                                                                           23 2 [] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 2 23] swaack first choice i + [3] swaack first [23] swaack sum +
                                                                                                                                                            23 2 True . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 2 23] swaack first choice i + [3] swaack first [23] swaack sum +
                                                                        23 2 True [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 2 23] . swaack first choice i + [3] swaack first [23] swaack sum +
                                                                        23 2 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [True 2 23] . first choice i + [3] swaack first [23] swaack sum +
                                                                               23 2 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] True . choice i + [3] swaack first [23] swaack sum +
                                                                                                                                                      23 2 [] [pop 0] . i + [3] swaack first [23] swaack sum +
                                                                                                                                                              23 2 [] . pop 0 + [3] swaack first [23] swaack sum +
                                                                                                                                                                 23 2 . 0 + [3] swaack first [23] swaack sum +
                                                                                                                                                               23 2 0 . + [3] swaack first [23] swaack sum +
                                                                                                                                                                 23 2 . [3] swaack first [23] swaack sum +
                                                                                                                                                             23 2 [3] . swaack first [23] swaack sum +
                                                                                                                                                             3 [2 23] . first [23] swaack sum +
                                                                                                                                                                  3 2 . [23] swaack sum +
                                                                                                                                                             3 2 [23] . swaack sum +
                                                                                                                                                             23 [2 3] . sum +
                                                                                                                                                             23 [2 3] . 0 [+] catamorphism +
                                                                                                                                                           23 [2 3] 0 . [+] catamorphism +
                                                                                                                                                       23 [2 3] 0 [+] . catamorphism +
                                                                                                                                                       23 [2 3] 0 [+] . [[] =] roll> [uncons swap] swap hylomorphism +
                                                                                                                                                23 [2 3] 0 [+] [[] =] . roll> [uncons swap] swap hylomorphism +
                                                                                                                                                23 [2 3] [[] =] 0 [+] . [uncons swap] swap hylomorphism +
                                                                                                                                  23 [2 3] [[] =] 0 [+] [uncons swap] . swap hylomorphism +
                                                                                                                                  23 [2 3] [[] =] 0 [uncons swap] [+] . hylomorphism +
                                                                                                                                  23 [2 3] [[] =] 0 [uncons swap] [+] . [unit [pop] swoncat] dipd [dip] swoncat genrec +
                                                                                                             23 [2 3] [[] =] 0 [uncons swap] [+] [unit [pop] swoncat] . dipd [dip] swoncat genrec +
                                                                                                                                                    23 [2 3] [[] =] 0 . unit [pop] swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                                                                    23 [2 3] [[] =] 0 . [] cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                                                                 23 [2 3] [[] =] 0 [] . cons [pop] swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                                                                  23 [2 3] [[] =] [0] . [pop] swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                                                            23 [2 3] [[] =] [0] [pop] . swoncat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                                                            23 [2 3] [[] =] [0] [pop] . swap concat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                                                            23 [2 3] [[] =] [pop] [0] . concat [uncons swap] [+] [dip] swoncat genrec +
                                                                                                                                              23 [2 3] [[] =] [pop 0] . [uncons swap] [+] [dip] swoncat genrec +
                                                                                                                                23 [2 3] [[] =] [pop 0] [uncons swap] . [+] [dip] swoncat genrec +
                                                                                                                            23 [2 3] [[] =] [pop 0] [uncons swap] [+] . [dip] swoncat genrec +
                                                                                                                      23 [2 3] [[] =] [pop 0] [uncons swap] [+] [dip] . swoncat genrec +
                                                                                                                      23 [2 3] [[] =] [pop 0] [uncons swap] [+] [dip] . swap concat genrec +
                                                                                                                      23 [2 3] [[] =] [pop 0] [uncons swap] [dip] [+] . concat genrec +
                                                                                                                        23 [2 3] [[] =] [pop 0] [uncons swap] [dip +] . genrec +
                                                                            23 [2 3] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte +
                                                                 23 [2 3] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[2 3] 23] [[] =] . infra first choice i +
                                                                                                                                                             23 [2 3] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [2 3] 23] swaack first choice i +
                                                                                                                                                          23 [2 3] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [2 3] 23] swaack first choice i +
                                                                                                                                                             23 False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [2 3] 23] swaack first choice i +
                                                                        23 False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [2 3] 23] . swaack first choice i +
                                                                        23 [2 3] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False 23] . first choice i +
                                                                             23 [2 3] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i +
                                                                                           23 [2 3] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i +
                                                                                                                                                             23 [2 3] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + +
                                                                                                                                                             23 2 [3] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + +
                                                                                                                                                             23 [3] 2 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + +
                                                                                                               23 [3] 2 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + +
                                                                                                                                                               23 [3] . [[] =] [pop 0] [uncons swap] [dip +] genrec 2 + +
                                                                                                                                                        23 [3] [[] =] . [pop 0] [uncons swap] [dip +] genrec 2 + +
                                                                                                                                                23 [3] [[] =] [pop 0] . [uncons swap] [dip +] genrec 2 + +
                                                                                                                                  23 [3] [[] =] [pop 0] [uncons swap] . [dip +] genrec 2 + +
                                                                                                                          23 [3] [[] =] [pop 0] [uncons swap] [dip +] . genrec 2 + +
                                                                              23 [3] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 2 + +
                                                                     23 [3] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[3] 23] [[] =] . infra first choice i 2 + +
                                                                                                                                                               23 [3] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [3] 23] swaack first choice i 2 + +
                                                                                                                                                            23 [3] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [3] 23] swaack first choice i 2 + +
                                                                                                                                                             23 False . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [3] 23] swaack first choice i 2 + +
                                                                          23 False [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [3] 23] . swaack first choice i 2 + +
                                                                          23 [3] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [False 23] . first choice i 2 + +
                                                                               23 [3] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] False . choice i 2 + +
                                                                                             23 [3] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . i 2 + +
                                                                                                                                                               23 [3] . uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 2 + +
                                                                                                                                                              23 3 [] . swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 2 + +
                                                                                                                                                              23 [] 3 . [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip + 2 + +
                                                                                                                23 [] 3 [[[] =] [pop 0] [uncons swap] [dip +] genrec] . dip + 2 + +
                                                                                                                                                                23 [] . [[] =] [pop 0] [uncons swap] [dip +] genrec 3 + 2 + +
                                                                                                                                                         23 [] [[] =] . [pop 0] [uncons swap] [dip +] genrec 3 + 2 + +
                                                                                                                                                 23 [] [[] =] [pop 0] . [uncons swap] [dip +] genrec 3 + 2 + +
                                                                                                                                   23 [] [[] =] [pop 0] [uncons swap] . [dip +] genrec 3 + 2 + +
                                                                                                                           23 [] [[] =] [pop 0] [uncons swap] [dip +] . genrec 3 + 2 + +
                                                                               23 [] [[] =] [pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] . ifte 3 + 2 + +
                                                                       23 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [[] 23] [[] =] . infra first choice i 3 + 2 + +
                                                                                                                                                                23 [] . [] = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 23] swaack first choice i 3 + 2 + +
                                                                                                                                                             23 [] [] . = [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 23] swaack first choice i 3 + 2 + +
                                                                                                                                                              23 True . [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 23] swaack first choice i 3 + 2 + +
                                                                            23 True [[pop 0] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [] 23] . swaack first choice i 3 + 2 + +
                                                                            23 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] [True 23] . first choice i 3 + 2 + +
                                                                                 23 [] [uncons swap [[[] =] [pop 0] [uncons swap] [dip +] genrec] dip +] [pop 0] True . choice i 3 + 2 + +
                                                                                                                                                        23 [] [pop 0] . i 3 + 2 + +
                                                                                                                                                                23 [] . pop 0 3 + 2 + +
                                                                                                                                                                   23 . 0 3 + 2 + +
                                                                                                                                                                 23 0 . 3 + 2 + +
                                                                                                                                                               23 0 3 . + 2 + +
                                                                                                                                                                 23 3 . 2 + +
                                                                                                                                                               23 3 2 . + +
                                                                                                                                                                 23 5 . +
                                                                                                                                                                   28 . 



```python
J('[23 [[2 [[23 [[2 []] [3 []]]][23 [[2 []] [3 []]]]]] [3 [[23 [[2 []] [3 []]]][23 [[2 []] [3 []]]]]]]] 0 [sum +] [] treestep')
```

    140



```python
J('[] [] [unit cons] [23 +] treestep')
```

    []



```python
J('[23 []] [] [unit cons] [23 +] treestep')
```

    [46 []]



```python
J('[23 [[2 []] [3 []]]] [] [unit cons] [23 +] treestep')
```

    [46 [[25 []] [26 []]]]



```python
define('treemap == [] [unit cons] roll< treestep')
```


```python
J('[23 [[2 []] [3 []]]] [23 +] treemap')
```

    [46 [[25 []] [26 []]]]

