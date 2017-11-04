
# Using `x` to Generate Values

Cf. jp-reprod.html


```python
from notebook_preamble import J, V, define
```

Consider the `x` combinator `x == dup i`:

    [a B] x
    [a B] a B

Let `B` `swap` the `a` with the quote and run some function `[C]` on it.

    [a B] a B
    [a B] a swap [C] dip
    a [a B]      [C] dip
    a C [a B]

Now discard the quoted `a` with `rest` and `cons` the result of `C` on `a` whatever that is:

    aC [a B] rest cons
    aC [B] cons
    [aC B]

Altogether, this is the definition of `B`:

    B == swap [C] dip rest cons

We can create a quoted program that generates the Natural numbers (integers 0, 1, 2, ...) by using `0` for `a` and `[dup ++]` for `[C]`:

    [0 swap [dup ++] dip rest cons]

Let's try it:


```python
V('[0 swap [dup ++] dip rest cons] x')
```

                                               . [0 swap [dup ++] dip rest cons] x
               [0 swap [dup ++] dip rest cons] . x
               [0 swap [dup ++] dip rest cons] . 0 swap [dup ++] dip rest cons
             [0 swap [dup ++] dip rest cons] 0 . swap [dup ++] dip rest cons
             0 [0 swap [dup ++] dip rest cons] . [dup ++] dip rest cons
    0 [0 swap [dup ++] dip rest cons] [dup ++] . dip rest cons
                                             0 . dup ++ [0 swap [dup ++] dip rest cons] rest cons
                                           0 0 . ++ [0 swap [dup ++] dip rest cons] rest cons
                                           0 1 . [0 swap [dup ++] dip rest cons] rest cons
           0 1 [0 swap [dup ++] dip rest cons] . rest cons
             0 1 [swap [dup ++] dip rest cons] . cons
             0 [1 swap [dup ++] dip rest cons] . 


After one application of `x` the quoted program contains `1` and `0` is below it on the stack.


```python
J('[0 swap [dup ++] dip rest cons] x x x x x pop')
```

    4 3 2 1 0


### `direco`


```python
define('direco == dip rest cons')
```


```python
V('[0 swap [dup ++] direco] x')
```

                                        . [0 swap [dup ++] direco] x
               [0 swap [dup ++] direco] . x
               [0 swap [dup ++] direco] . 0 swap [dup ++] direco
             [0 swap [dup ++] direco] 0 . swap [dup ++] direco
             0 [0 swap [dup ++] direco] . [dup ++] direco
    0 [0 swap [dup ++] direco] [dup ++] . direco
    0 [0 swap [dup ++] direco] [dup ++] . dip rest cons
                                      0 . dup ++ [0 swap [dup ++] direco] rest cons
                                    0 0 . ++ [0 swap [dup ++] direco] rest cons
                                    0 1 . [0 swap [dup ++] direco] rest cons
           0 1 [0 swap [dup ++] direco] . rest cons
             0 1 [swap [dup ++] direco] . cons
             0 [1 swap [dup ++] direco] . 


# Generating Generators
We want to go from:

    a [C] G

to:

    [a swap [C] direco]

Working in reverse:

    [a swap   [C] direco] cons
    a [swap   [C] direco] concat
    a [swap] [[C] direco] swap
    a [[C] direco] [swap]
    a [C] [direco] cons [swap]

Reading from the bottom up:

    G == [direco] cons [swap] swap concat cons
    G == [direco] cons [swap] swoncat cons

We can try it out:

    0 [dup ++] G


```python
define('G == [direco] cons [swap] swoncat cons')
```


```python
V('0 [dup ++] G')
```

                               . 0 [dup ++] G
                             0 . [dup ++] G
                    0 [dup ++] . G
                    0 [dup ++] . [direco] cons [swap] swoncat cons
           0 [dup ++] [direco] . cons [swap] swoncat cons
           0 [[dup ++] direco] . [swap] swoncat cons
    0 [[dup ++] direco] [swap] . swoncat cons
    0 [[dup ++] direco] [swap] . swap concat cons
    0 [swap] [[dup ++] direco] . concat cons
      0 [swap [dup ++] direco] . cons
      [0 swap [dup ++] direco] . 



```python
V('0 [dup ++] G x')
```

                                        . 0 [dup ++] G x
                                      0 . [dup ++] G x
                             0 [dup ++] . G x
                             0 [dup ++] . [direco] cons [swap] swoncat cons x
                    0 [dup ++] [direco] . cons [swap] swoncat cons x
                    0 [[dup ++] direco] . [swap] swoncat cons x
             0 [[dup ++] direco] [swap] . swoncat cons x
             0 [[dup ++] direco] [swap] . swap concat cons x
             0 [swap] [[dup ++] direco] . concat cons x
               0 [swap [dup ++] direco] . cons x
               [0 swap [dup ++] direco] . x
               [0 swap [dup ++] direco] . 0 swap [dup ++] direco
             [0 swap [dup ++] direco] 0 . swap [dup ++] direco
             0 [0 swap [dup ++] direco] . [dup ++] direco
    0 [0 swap [dup ++] direco] [dup ++] . direco
    0 [0 swap [dup ++] direco] [dup ++] . dip rest cons
                                      0 . dup ++ [0 swap [dup ++] direco] rest cons
                                    0 0 . ++ [0 swap [dup ++] direco] rest cons
                                    0 1 . [0 swap [dup ++] direco] rest cons
           0 1 [0 swap [dup ++] direco] . rest cons
             0 1 [swap [dup ++] direco] . cons
             0 [1 swap [dup ++] direco] . 


### Powers of 2


```python
J('1 [dup 1 <<] G x x x x x x x x x')
```

    [512 swap [dup 1 <<] direco] 256 128 64 32 16 8 4 2 1


# `n [x] times`
If we have one of these quoted programs we can drive it using `times` with the `x` combinator.

Let's define a word `n_range` that takes a starting integer and a count and leaves that many consecutive integers on the stack.  For example:


```python
J('23 [dup ++] G 5 [x] times pop')
```

    27 26 25 24 23


We can use `dip` to untangle `[dup ++] G` from the arguments.


```python
J('23 5 [[dup ++] G] dip [x] times pop')
```

    27 26 25 24 23


Now that the givens (arguments) are on the left we have the definition we're looking for:


```python
define('n_range == [[dup ++] G] dip [x] times pop')
```


```python
J('450 10 n_range')
```

    459 458 457 456 455 454 453 452 451 450


This is better just using the `times` combinator though...


```python
J('450 9 [dup ++] times')
```

    459 458 457 456 455 454 453 452 451 450


# Generating Multiples of Three and Five
Look at the treatment of the Project Euler Problem One in [Developing a Program.ipynb](./Developing a Program.ipynb) and you'll see that we might be interested in generating an endless cycle of:

    3 2 1 3 1 2 3

To do this we want to encode the numbers as pairs of bits in a single int:

        3  2  1  3  1  2  3
    0b 11 10 01 11 01 10 11 == 14811

And pick them off by masking with 3 (binary 11) and then shifting the int right two bits.


```python
define('PE1.1 == dup [3 &] dip 2 >>')
```


```python
V('14811 PE1.1')
```

                      . 14811 PE1.1
                14811 . PE1.1
                14811 . dup [3 &] dip 2 >>
          14811 14811 . [3 &] dip 2 >>
    14811 14811 [3 &] . dip 2 >>
                14811 . 3 & 14811 2 >>
              14811 3 . & 14811 2 >>
                    3 . 14811 2 >>
              3 14811 . 2 >>
            3 14811 2 . >>
               3 3702 . 


If we plug `14811` and `[PE1.1]` into our generator form...


```python
J('[14811 swap [PE1.1] direco] x')
```

    [3702 swap [PE1.1] direco] 3


...we get a generator that works for seven cycles before it reaches zero:


```python
J('[14811 swap [PE1.1] direco] 7 [x] times')
```

    [0 swap [PE1.1] direco] 3 2 1 3 1 2 3


### Reset at Zero
We need a function that checks if the int has reached zero and resets it if so.


```python
define('PE1.1.check == dup [pop 14811] [] branch')
```


```python
J('[14811 swap [PE1.1.check PE1.1] direco] 21 [x] times')
```

    [0 swap [PE1.1.check PE1.1] direco] 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3


### Run 466 times
In the PE1 problem we are asked to sum all the multiples of three and five less than 1000.  It's worked out that we need to use all seven numbers sixty-six times and then four more.


```python
J('7 66 * 4 +')
```

    466


If we drive our generator 466 times and sum the stack we get 999.


```python
J('[14811 swap [PE1.1.check PE1.1] dip rest cons] 466 [x] times')
```

    [57 swap [PE1.1.check PE1.1] dip rest cons] 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3 3 2 1 3 1 2 3



```python
J('[14811 swap [PE1.1.check PE1.1] dip rest cons] 466 [x] times pop enstacken sum')
```

    999


# Project Euler Problem One


```python
define('PE1.2 == + dup [+] dip')
```

Now we can add `PE1.2` to the quoted program given to `times`.


```python
J('0 0 [0 swap [PE1.1.check PE1.1] direco] 466 [x [PE1.2] dip] times popop')
```

    233168


Or using `G` we can write:


```python
J('0 0 0 [PE1.1.check PE1.1] G 466 [x [PE1.2] dip] times popop')
```

    233168


# How to compile these?
You would probably start with a special version of `G`, and perhaps modifications to the default `x`?
