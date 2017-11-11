
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

Try it with input 3 (omitting predicate):

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


### Derive `paramorphism` form the form above.

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

## Appendix - Fun with Symbols

    |[ (c, F), (G, P) ]| == (|c, F|) • [(G, P)]

["Bananas, Lenses, & Barbed Wire"](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.41.125)

    (|...|)  [(...)]  [<...>]

I think they are having slightly too much fun with the symbols.

"Too much is always better than not enough."


## The `step` combinator will usually be better to use than `catamorphism`.

    sum == 0 swap [+] step
    sum == 0 [+] catamorphism


