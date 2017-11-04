
# Factorial Function and Paramorphisms


```python
from notebook_preamble import J, V, define
```

# `loop` Form


```python
define('factorial == 1 swap dup 1 > [[*] dupdip -- dup 1 >] loop pop')
```


```python
V('3 factorial')
```

                                      . 3 factorial
                                    3 . factorial
                                    3 . 1 swap dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                  3 1 . swap dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                  1 3 . dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                1 3 3 . 1 > [[*] dupdip -- dup 1 >] loop pop
                              1 3 3 1 . > [[*] dupdip -- dup 1 >] loop pop
                             1 3 True . [[*] dupdip -- dup 1 >] loop pop
     1 3 True [[*] dupdip -- dup 1 >] . loop pop
                                  1 3 . [*] dupdip -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                              1 3 [*] . dupdip -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                  1 3 . * 3 -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                    3 . 3 -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                  3 3 . -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                  3 2 . dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                3 2 2 . 1 > [[*] dupdip -- dup 1 >] loop pop
                              3 2 2 1 . > [[*] dupdip -- dup 1 >] loop pop
                             3 2 True . [[*] dupdip -- dup 1 >] loop pop
     3 2 True [[*] dupdip -- dup 1 >] . loop pop
                                  3 2 . [*] dupdip -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                              3 2 [*] . dupdip -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                  3 2 . * 2 -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                    6 . 2 -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                  6 2 . -- dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                  6 1 . dup 1 > [[*] dupdip -- dup 1 >] loop pop
                                6 1 1 . 1 > [[*] dupdip -- dup 1 >] loop pop
                              6 1 1 1 . > [[*] dupdip -- dup 1 >] loop pop
                            6 1 False . [[*] dupdip -- dup 1 >] loop pop
    6 1 False [[*] dupdip -- dup 1 >] . loop pop
                                  6 1 . pop
                                    6 . 



```python
define('P == dup 1 >')
define('factorial == 1 swap P [[*] dupdip -- P] loop pop')
```


```python
J('3 factorial')
```

    6


We have a form:

    1 swap P [[*] dupdip -- P] loop pop
    n swap P [[A] dupdip B  P] loop pop

With
- `n` is the "identity" for `A`
- `A :: (a, a) -> a`
- `B :: a -> a` generates the next value `a`
- and lastly `P :: a -> Bool` detects the end of the series.

The form starts with some value on the stack and duplicates it.  One copy is combined with the current value by `A`, and the other is modified by `B` to generate the next value for the loop, which continues until `P` returns `False`.

    n [A] [B] [P] paramorphism
    ...
    n swap P [[A] dupdip B P] loop pop



    n  [A] [B] [P] concat
    n  [A] [B P] [dupdip] swoncat
    n  [A] [dupdip B P] cons
    n [[A] dupdip B P]

Introduce the other `[P]`:

    n swap P [[A] dupdip B P]                        loop pop
    n        [[A] dupdip B P] [swap P]           dip loop pop
    n        [[A] dupdip B P] [P] [swap] swoncat dip loop pop

Putting them together:

    n [A] [B] [P] [concat [dupdip] swoncat cons] dipdup [swap] swoncat dip loop pop
    n [A] [B] [P]  concat [dupdip] swoncat cons [P] [swap] swoncat dip loop pop
    n [A] [B   P]         [dupdip] swoncat cons [P] [swap] swoncat dip loop pop
    n [A] [dupdip B P]                    cons [P] [swap] swoncat dip loop pop
    n [[A] dupdip B P] [P] [swap] swoncat dip loop pop
    n [[A] dupdip B P] [swap P]           dip loop pop
    n swap P [[A] dupdip B P] loop pop




```python
define('paramorphism == [concat [dupdip] swoncat cons] dupdip [swap] swoncat dip loop pop')
define('factorial == 1 [*] [--] [P] paramorphism')
```


```python
V('3 factorial')
```

                                                    . 3 factorial
                                                  3 . factorial
                                                  3 . 1 [*] [--] [P] paramorphism
                                                3 1 . [*] [--] [P] paramorphism
                                            3 1 [*] . [--] [P] paramorphism
                                       3 1 [*] [--] . [P] paramorphism
                                   3 1 [*] [--] [P] . paramorphism
                                   3 1 [*] [--] [P] . [concat [dupdip] swoncat cons] dupdip [swap] swoncat dip loop pop
    3 1 [*] [--] [P] [concat [dupdip] swoncat cons] . dupdip [swap] swoncat dip loop pop
                                   3 1 [*] [--] [P] . concat [dupdip] swoncat cons [P] [swap] swoncat dip loop pop
                                     3 1 [*] [-- P] . [dupdip] swoncat cons [P] [swap] swoncat dip loop pop
                            3 1 [*] [-- P] [dupdip] . swoncat cons [P] [swap] swoncat dip loop pop
                            3 1 [*] [-- P] [dupdip] . swap concat cons [P] [swap] swoncat dip loop pop
                            3 1 [*] [dupdip] [-- P] . concat cons [P] [swap] swoncat dip loop pop
                              3 1 [*] [dupdip -- P] . cons [P] [swap] swoncat dip loop pop
                              3 1 [[*] dupdip -- P] . [P] [swap] swoncat dip loop pop
                          3 1 [[*] dupdip -- P] [P] . [swap] swoncat dip loop pop
                   3 1 [[*] dupdip -- P] [P] [swap] . swoncat dip loop pop
                   3 1 [[*] dupdip -- P] [P] [swap] . swap concat dip loop pop
                   3 1 [[*] dupdip -- P] [swap] [P] . concat dip loop pop
                     3 1 [[*] dupdip -- P] [swap P] . dip loop pop
                                                3 1 . swap P [[*] dupdip -- P] loop pop
                                                1 3 . P [[*] dupdip -- P] loop pop
                                                1 3 . dup 1 > [[*] dupdip -- P] loop pop
                                              1 3 3 . 1 > [[*] dupdip -- P] loop pop
                                            1 3 3 1 . > [[*] dupdip -- P] loop pop
                                           1 3 True . [[*] dupdip -- P] loop pop
                         1 3 True [[*] dupdip -- P] . loop pop
                                                1 3 . [*] dupdip -- P [[*] dupdip -- P] loop pop
                                            1 3 [*] . dupdip -- P [[*] dupdip -- P] loop pop
                                                1 3 . * 3 -- P [[*] dupdip -- P] loop pop
                                                  3 . 3 -- P [[*] dupdip -- P] loop pop
                                                3 3 . -- P [[*] dupdip -- P] loop pop
                                                3 2 . P [[*] dupdip -- P] loop pop
                                                3 2 . dup 1 > [[*] dupdip -- P] loop pop
                                              3 2 2 . 1 > [[*] dupdip -- P] loop pop
                                            3 2 2 1 . > [[*] dupdip -- P] loop pop
                                           3 2 True . [[*] dupdip -- P] loop pop
                         3 2 True [[*] dupdip -- P] . loop pop
                                                3 2 . [*] dupdip -- P [[*] dupdip -- P] loop pop
                                            3 2 [*] . dupdip -- P [[*] dupdip -- P] loop pop
                                                3 2 . * 2 -- P [[*] dupdip -- P] loop pop
                                                  6 . 2 -- P [[*] dupdip -- P] loop pop
                                                6 2 . -- P [[*] dupdip -- P] loop pop
                                                6 1 . P [[*] dupdip -- P] loop pop
                                                6 1 . dup 1 > [[*] dupdip -- P] loop pop
                                              6 1 1 . 1 > [[*] dupdip -- P] loop pop
                                            6 1 1 1 . > [[*] dupdip -- P] loop pop
                                          6 1 False . [[*] dupdip -- P] loop pop
                        6 1 False [[*] dupdip -- P] . loop pop
                                                6 1 . pop
                                                  6 . 


# `primrec` Recursive Form
    n swap [P] [pop] [[A] dupdip B] primrec
    
(Note that `P` is inverted from above, becoming `1 <=`.  Also it no longer requires `dup` because in the `primrec` combinator it is executed with its own copy of the stack so it can consume items so long as it leaves a Boolean on top when it's finished.)


```python
define('factorial == 1 swap [1 <=] [pop] [[*] dupdip --] primrec')
```


```python
V('3 factorial')
```

                                                                                       . 3 factorial
                                                                                     3 . factorial
                                                                                     3 . 1 swap [1 <=] [pop] [[*] dupdip --] primrec
                                                                                   3 1 . swap [1 <=] [pop] [[*] dupdip --] primrec
                                                                                   1 3 . [1 <=] [pop] [[*] dupdip --] primrec
                                                                            1 3 [1 <=] . [pop] [[*] dupdip --] primrec
                                                                      1 3 [1 <=] [pop] . [[*] dupdip --] primrec
                                                      1 3 [1 <=] [pop] [[*] dupdip --] . primrec
                                                      1 3 [1 <=] [pop] [[*] dupdip --] . [i] genrec
                                                  1 3 [1 <=] [pop] [[*] dupdip --] [i] . genrec
          1 3 [1 <=] [pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . ifte
    1 3 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [3 1] [1 <=] . infra first choice i
                                                                                   1 3 . 1 <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 3 1] swaack first choice i
                                                                                 1 3 1 . <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 3 1] swaack first choice i
                                                                               1 False . [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 3 1] swaack first choice i
       1 False [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 3 1] . swaack first choice i
       1 3 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [False 1] . first choice i
           1 3 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] False . choice i
                       1 3 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . i
                                                                                   1 3 . [*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                               1 3 [*] . dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   1 3 . * 3 -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                     3 . 3 -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   3 3 . -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   3 2 . [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                         3 2 [[1 <=] [pop] [[*] dupdip --] [i] genrec] . i
                                                                                   3 2 . [1 <=] [pop] [[*] dupdip --] [i] genrec
                                                                            3 2 [1 <=] . [pop] [[*] dupdip --] [i] genrec
                                                                      3 2 [1 <=] [pop] . [[*] dupdip --] [i] genrec
                                                      3 2 [1 <=] [pop] [[*] dupdip --] . [i] genrec
                                                  3 2 [1 <=] [pop] [[*] dupdip --] [i] . genrec
          3 2 [1 <=] [pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . ifte
    3 2 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [2 3] [1 <=] . infra first choice i
                                                                                   3 2 . 1 <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 2 3] swaack first choice i
                                                                                 3 2 1 . <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 2 3] swaack first choice i
                                                                               3 False . [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 2 3] swaack first choice i
       3 False [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 2 3] . swaack first choice i
       3 2 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [False 3] . first choice i
           3 2 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] False . choice i
                       3 2 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . i
                                                                                   3 2 . [*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                               3 2 [*] . dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   3 2 . * 2 -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                     6 . 2 -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   6 2 . -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   6 1 . [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                         6 1 [[1 <=] [pop] [[*] dupdip --] [i] genrec] . i
                                                                                   6 1 . [1 <=] [pop] [[*] dupdip --] [i] genrec
                                                                            6 1 [1 <=] . [pop] [[*] dupdip --] [i] genrec
                                                                      6 1 [1 <=] [pop] . [[*] dupdip --] [i] genrec
                                                      6 1 [1 <=] [pop] [[*] dupdip --] . [i] genrec
                                                  6 1 [1 <=] [pop] [[*] dupdip --] [i] . genrec
          6 1 [1 <=] [pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . ifte
    6 1 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [1 6] [1 <=] . infra first choice i
                                                                                   6 1 . 1 <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 1 6] swaack first choice i
                                                                                 6 1 1 . <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 1 6] swaack first choice i
                                                                                6 True . [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 1 6] swaack first choice i
        6 True [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 1 6] . swaack first choice i
        6 1 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [True 6] . first choice i
            6 1 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] True . choice i
                                                                             6 1 [pop] . i
                                                                                   6 1 . pop
                                                                                     6 . 


### Derive `paramorphism` form the form above.
    n swap [P]       [pop]     [[A] dupdip B]                  primrec
    n [P] [swap] dip [pop]     [[A] dupdip B]                  primrec
    n [P] [[A] dupdip B]                [[swap] dip [pop]] dip primrec
    n [P] [A] [dupdip B]           cons [[swap] dip [pop]] dip primrec
    n [P] [A] [B] [dupdip] swoncat cons [[swap] dip [pop]] dip primrec

(Note the order of arguments is different, `[P]` is no longer at the top of the stack.)

    paramorphism == [dupdip] swoncat cons [[swap] dip [pop]] dip primrec


```python
define('paramorphism == [dupdip] swoncat cons [[swap] dip [pop]] dip primrec')
define('factorial == 1 [1 <=] [*] [--] paramorphism')
```


```python
V('3 factorial')
```

                                                                                       . 3 factorial
                                                                                     3 . factorial
                                                                                     3 . 1 [1 <=] [*] [--] paramorphism
                                                                                   3 1 . [1 <=] [*] [--] paramorphism
                                                                            3 1 [1 <=] . [*] [--] paramorphism
                                                                        3 1 [1 <=] [*] . [--] paramorphism
                                                                   3 1 [1 <=] [*] [--] . paramorphism
                                                                   3 1 [1 <=] [*] [--] . [dupdip] swoncat cons [[swap] dip [pop]] dip primrec
                                                          3 1 [1 <=] [*] [--] [dupdip] . swoncat cons [[swap] dip [pop]] dip primrec
                                                          3 1 [1 <=] [*] [--] [dupdip] . swap concat cons [[swap] dip [pop]] dip primrec
                                                          3 1 [1 <=] [*] [dupdip] [--] . concat cons [[swap] dip [pop]] dip primrec
                                                            3 1 [1 <=] [*] [dupdip --] . cons [[swap] dip [pop]] dip primrec
                                                            3 1 [1 <=] [[*] dupdip --] . [[swap] dip [pop]] dip primrec
                                         3 1 [1 <=] [[*] dupdip --] [[swap] dip [pop]] . dip primrec
                                                                            3 1 [1 <=] . [swap] dip [pop] [[*] dupdip --] primrec
                                                                     3 1 [1 <=] [swap] . dip [pop] [[*] dupdip --] primrec
                                                                                   3 1 . swap [1 <=] [pop] [[*] dupdip --] primrec
                                                                                   1 3 . [1 <=] [pop] [[*] dupdip --] primrec
                                                                            1 3 [1 <=] . [pop] [[*] dupdip --] primrec
                                                                      1 3 [1 <=] [pop] . [[*] dupdip --] primrec
                                                      1 3 [1 <=] [pop] [[*] dupdip --] . primrec
                                                      1 3 [1 <=] [pop] [[*] dupdip --] . [i] genrec
                                                  1 3 [1 <=] [pop] [[*] dupdip --] [i] . genrec
          1 3 [1 <=] [pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . ifte
    1 3 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [3 1] [1 <=] . infra first choice i
                                                                                   1 3 . 1 <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 3 1] swaack first choice i
                                                                                 1 3 1 . <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 3 1] swaack first choice i
                                                                               1 False . [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 3 1] swaack first choice i
       1 False [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 3 1] . swaack first choice i
       1 3 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [False 1] . first choice i
           1 3 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] False . choice i
                       1 3 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . i
                                                                                   1 3 . [*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                               1 3 [*] . dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   1 3 . * 3 -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                     3 . 3 -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   3 3 . -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   3 2 . [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                         3 2 [[1 <=] [pop] [[*] dupdip --] [i] genrec] . i
                                                                                   3 2 . [1 <=] [pop] [[*] dupdip --] [i] genrec
                                                                            3 2 [1 <=] . [pop] [[*] dupdip --] [i] genrec
                                                                      3 2 [1 <=] [pop] . [[*] dupdip --] [i] genrec
                                                      3 2 [1 <=] [pop] [[*] dupdip --] . [i] genrec
                                                  3 2 [1 <=] [pop] [[*] dupdip --] [i] . genrec
          3 2 [1 <=] [pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . ifte
    3 2 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [2 3] [1 <=] . infra first choice i
                                                                                   3 2 . 1 <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 2 3] swaack first choice i
                                                                                 3 2 1 . <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 2 3] swaack first choice i
                                                                               3 False . [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 2 3] swaack first choice i
       3 False [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 2 3] . swaack first choice i
       3 2 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [False 3] . first choice i
           3 2 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] False . choice i
                       3 2 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . i
                                                                                   3 2 . [*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                               3 2 [*] . dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   3 2 . * 2 -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                     6 . 2 -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   6 2 . -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                                                                   6 1 . [[1 <=] [pop] [[*] dupdip --] [i] genrec] i
                                         6 1 [[1 <=] [pop] [[*] dupdip --] [i] genrec] . i
                                                                                   6 1 . [1 <=] [pop] [[*] dupdip --] [i] genrec
                                                                            6 1 [1 <=] . [pop] [[*] dupdip --] [i] genrec
                                                                      6 1 [1 <=] [pop] . [[*] dupdip --] [i] genrec
                                                      6 1 [1 <=] [pop] [[*] dupdip --] . [i] genrec
                                                  6 1 [1 <=] [pop] [[*] dupdip --] [i] . genrec
          6 1 [1 <=] [pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] . ifte
    6 1 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [1 6] [1 <=] . infra first choice i
                                                                                   6 1 . 1 <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 1 6] swaack first choice i
                                                                                 6 1 1 . <= [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 1 6] swaack first choice i
                                                                                6 True . [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 1 6] swaack first choice i
        6 True [[pop] [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] 1 6] . swaack first choice i
        6 1 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] [True 6] . first choice i
            6 1 [[*] dupdip -- [[1 <=] [pop] [[*] dupdip --] [i] genrec] i] [pop] True . choice i
                                                                             6 1 [pop] . i
                                                                                   6 1 . pop
                                                                                     6 . 


# `tails`
An example of a paramorphism for lists given in the ["Bananas..." paper](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.41.125) is `tails` which returns the list of "tails" of a list.

    [1 2 3] tails == [[] [3] [2 3]]
    
Using `paramorphism` we would write:

    tails == [] [not] [rest swons] [rest] paramorphism


```python
define('tails == [] [not] [rest swons] [rest] paramorphism')
```


```python
J('[1 2 3] tails')
```

    [[] [3] [2 3]]


### Factoring `rest`
Right before the recursion begins we have:
    
    [] [1 2 3] [not] [pop] [[rest swons] dupdip rest] primrec
    
But we might prefer to factor `rest` in the quote:

    [] [1 2 3] [not] [pop] [rest [swons] dupdip] primrec

There's no way to do that with the `paramorphism` combinator as defined.  We would have to write and use a slightly different recursion combinator or just write it manually.  This is yet another place where the *sufficiently smart compiler* will one day automatically refactor the code.


```python
J('[] [1 2 3] [not] [pop] [rest [swons] dupdip] primrec')
```

    [[] [3] [2 3]]

