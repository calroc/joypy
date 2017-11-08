
This notebook is about using the "zipper" with joy datastructures.  See the [Zipper wikipedia entry](https://en.wikipedia.org/wiki/Zipper_%28data_structure%29) or the original paper: ["FUNCTIONAL PEARL The Zipper" by Gérard Huet](https://www.st.cs.uni-saarland.de/edu/seminare/2005/advanced-fp/docs/huet-zipper.pdf)

Given a datastructure on the stack we can navigate through it, modify it, and rebuild it using the "zipper" technique.

### Preamble


```python
from notebook_preamble import J, V, define
```

## Trees
In Joypy there aren't any complex datastructures, just ints, floats, strings, Symbols (strings that are names of functions) and sequences (aka lists, aka quoted literals, aka aggregates, etc...), but we can build [trees](https://en.wikipedia.org/wiki/Tree_%28data_structure%29) out of sequences.


```python
J('[1 [2 [3 4 25 6] 7] 8]')
```

    [1 [2 [3 4 25 6] 7] 8]


## Zipper in Joy
Zippers work by keeping track of the current item, the already-seen items, and the yet-to-be seen items as you traverse a datastructure (the datastructure used to keep track of these items is the zipper.)

In Joy we can do this with the following words:

    z-down == [] swap uncons swap
    z-up == swons swap shunt
    z-right == [swons] cons dip uncons swap
    z-left == swons [uncons swap] dip swap

Let's use them to change 25 into 625.  The first time a word is used I show the trace so you can see how it works.  If we were going to use these a lot it would make sense to write Python versions for efficiency, but see below.


```python
define('z-down == [] swap uncons swap')
define('z-up == swons swap shunt')
define('z-right == [swons] cons dip uncons swap')
define('z-left == swons [uncons swap] dip swap')
```


```python
V('[1 [2 [3 4 25 6] 7] 8] z-down')
```

                              . [1 [2 [3 4 25 6] 7] 8] z-down
       [1 [2 [3 4 25 6] 7] 8] . z-down
       [1 [2 [3 4 25 6] 7] 8] . [] swap uncons swap
    [1 [2 [3 4 25 6] 7] 8] [] . swap uncons swap
    [] [1 [2 [3 4 25 6] 7] 8] . uncons swap
    [] 1 [[2 [3 4 25 6] 7] 8] . swap
    [] [[2 [3 4 25 6] 7] 8] 1 . 



```python
V('[] [[2 [3 4 25 6] 7] 8] 1 z-right')
```

                                      . [] [[2 [3 4 25 6] 7] 8] 1 z-right
                                   [] . [[2 [3 4 25 6] 7] 8] 1 z-right
              [] [[2 [3 4 25 6] 7] 8] . 1 z-right
            [] [[2 [3 4 25 6] 7] 8] 1 . z-right
            [] [[2 [3 4 25 6] 7] 8] 1 . [swons] cons dip uncons swap
    [] [[2 [3 4 25 6] 7] 8] 1 [swons] . cons dip uncons swap
    [] [[2 [3 4 25 6] 7] 8] [1 swons] . dip uncons swap
                                   [] . 1 swons [[2 [3 4 25 6] 7] 8] uncons swap
                                 [] 1 . swons [[2 [3 4 25 6] 7] 8] uncons swap
                                 [] 1 . swap cons [[2 [3 4 25 6] 7] 8] uncons swap
                                 1 [] . cons [[2 [3 4 25 6] 7] 8] uncons swap
                                  [1] . [[2 [3 4 25 6] 7] 8] uncons swap
             [1] [[2 [3 4 25 6] 7] 8] . uncons swap
             [1] [2 [3 4 25 6] 7] [8] . swap
             [1] [8] [2 [3 4 25 6] 7] . 



```python
J('[1] [8] [2 [3 4 25 6] 7] z-down')
```

    [1] [8] [] [[3 4 25 6] 7] 2



```python
J('[1] [8] [] [[3 4 25 6] 7] 2 z-right')
```

    [1] [8] [2] [7] [3 4 25 6]



```python
J('[1] [8] [2] [7] [3 4 25 6] z-down')
```

    [1] [8] [2] [7] [] [4 25 6] 3



```python
J('[1] [8] [2] [7] [] [4 25 6] 3 z-right')
```

    [1] [8] [2] [7] [3] [25 6] 4



```python
J('[1] [8] [2] [7] [3] [25 6] 4 z-right')
```

    [1] [8] [2] [7] [4 3] [6] 25



```python
J('[1] [8] [2] [7] [4 3] [6] 25 sqr')
```

    [1] [8] [2] [7] [4 3] [6] 625



```python
V('[1] [8] [2] [7] [4 3] [6] 625 z-up')
```

                                  . [1] [8] [2] [7] [4 3] [6] 625 z-up
                              [1] . [8] [2] [7] [4 3] [6] 625 z-up
                          [1] [8] . [2] [7] [4 3] [6] 625 z-up
                      [1] [8] [2] . [7] [4 3] [6] 625 z-up
                  [1] [8] [2] [7] . [4 3] [6] 625 z-up
            [1] [8] [2] [7] [4 3] . [6] 625 z-up
        [1] [8] [2] [7] [4 3] [6] . 625 z-up
    [1] [8] [2] [7] [4 3] [6] 625 . z-up
    [1] [8] [2] [7] [4 3] [6] 625 . swons swap shunt
    [1] [8] [2] [7] [4 3] [6] 625 . swap cons swap shunt
    [1] [8] [2] [7] [4 3] 625 [6] . cons swap shunt
    [1] [8] [2] [7] [4 3] [625 6] . swap shunt
    [1] [8] [2] [7] [625 6] [4 3] . shunt
      [1] [8] [2] [7] [3 4 625 6] . 



```python
J('[1] [8] [2] [7] [3 4 625 6] z-up')
```

    [1] [8] [2 [3 4 625 6] 7]



```python
J('[1] [8] [2 [3 4 625 6] 7] z-up')
```

    [1 [2 [3 4 625 6] 7] 8]


## `dip` and `infra`
In Joy we have the `dip` and `infra` combinators which can "target" or "address" any particular item in a Joy tree structure.


```python
V('[1 [2 [3 4 25 6] 7] 8] [[[[[[sqr] dipd] infra] dip] infra] dip] infra')
```

                                                                    . [1 [2 [3 4 25 6] 7] 8] [[[[[[sqr] dipd] infra] dip] infra] dip] infra
                                             [1 [2 [3 4 25 6] 7] 8] . [[[[[[sqr] dipd] infra] dip] infra] dip] infra
    [1 [2 [3 4 25 6] 7] 8] [[[[[[sqr] dipd] infra] dip] infra] dip] . infra
                                               8 [2 [3 4 25 6] 7] 1 . [[[[[sqr] dipd] infra] dip] infra] dip [] swaack
            8 [2 [3 4 25 6] 7] 1 [[[[[sqr] dipd] infra] dip] infra] . dip [] swaack
                                                 8 [2 [3 4 25 6] 7] . [[[[sqr] dipd] infra] dip] infra 1 [] swaack
                      8 [2 [3 4 25 6] 7] [[[[sqr] dipd] infra] dip] . infra 1 [] swaack
                                                     7 [3 4 25 6] 2 . [[[sqr] dipd] infra] dip [8] swaack 1 [] swaack
                                7 [3 4 25 6] 2 [[[sqr] dipd] infra] . dip [8] swaack 1 [] swaack
                                                       7 [3 4 25 6] . [[sqr] dipd] infra 2 [8] swaack 1 [] swaack
                                          7 [3 4 25 6] [[sqr] dipd] . infra 2 [8] swaack 1 [] swaack
                                                           6 25 4 3 . [sqr] dipd [7] swaack 2 [8] swaack 1 [] swaack
                                                     6 25 4 3 [sqr] . dipd [7] swaack 2 [8] swaack 1 [] swaack
                                                               6 25 . sqr 4 3 [7] swaack 2 [8] swaack 1 [] swaack
                                                               6 25 . dup mul 4 3 [7] swaack 2 [8] swaack 1 [] swaack
                                                            6 25 25 . mul 4 3 [7] swaack 2 [8] swaack 1 [] swaack
                                                              6 625 . 4 3 [7] swaack 2 [8] swaack 1 [] swaack
                                                            6 625 4 . 3 [7] swaack 2 [8] swaack 1 [] swaack
                                                          6 625 4 3 . [7] swaack 2 [8] swaack 1 [] swaack
                                                      6 625 4 3 [7] . swaack 2 [8] swaack 1 [] swaack
                                                      7 [3 4 625 6] . 2 [8] swaack 1 [] swaack
                                                    7 [3 4 625 6] 2 . [8] swaack 1 [] swaack
                                                7 [3 4 625 6] 2 [8] . swaack 1 [] swaack
                                                8 [2 [3 4 625 6] 7] . 1 [] swaack
                                              8 [2 [3 4 625 6] 7] 1 . [] swaack
                                           8 [2 [3 4 625 6] 7] 1 [] . swaack
                                            [1 [2 [3 4 625 6] 7] 8] . 


If you read the trace carefully you'll see that about half of it is the `dip` and `infra` combinators de-quoting programs and "digging" into the subject datastructure.  Instead of maintaining temporary results on the stack they are pushed into the pending expression (continuation).  When `sqr` has run the rest of the pending expression  rebuilds the datastructure.

## `Z`
Imagine a function `Z` that accepts a sequence of `dip` and `infra` combinators, a quoted program `[Q]`, and a datastructure to work on.  It would effectively execute the quoted program as if it had been embedded in a nested series of quoted programs, e.g.:

       [...] [Q] [dip dip infra dip infra dip infra] Z
    -------------------------------------------------------------
       [...] [[[[[[[Q] dip] dip] infra] dip] infra] dip] infra
       
The `Z` function isn't hard to make.


```python
define('Z == [[] cons cons] step i')
```

Here it is in action in a simplified scenario.


```python
V('1 [2 3 4] Z')
```

                                 . 1 [2 3 4] Z
                               1 . [2 3 4] Z
                       1 [2 3 4] . Z
                       1 [2 3 4] . [[] cons cons] step i
        1 [2 3 4] [[] cons cons] . step i
              1 2 [[] cons cons] . i [3 4] [[] cons cons] step i
                             1 2 . [] cons cons [3 4] [[] cons cons] step i
                          1 2 [] . cons cons [3 4] [[] cons cons] step i
                           1 [2] . cons [3 4] [[] cons cons] step i
                           [1 2] . [3 4] [[] cons cons] step i
                     [1 2] [3 4] . [[] cons cons] step i
      [1 2] [3 4] [[] cons cons] . step i
          [1 2] 3 [[] cons cons] . i [4] [[] cons cons] step i
                         [1 2] 3 . [] cons cons [4] [[] cons cons] step i
                      [1 2] 3 [] . cons cons [4] [[] cons cons] step i
                       [1 2] [3] . cons [4] [[] cons cons] step i
                       [[1 2] 3] . [4] [[] cons cons] step i
                   [[1 2] 3] [4] . [[] cons cons] step i
    [[1 2] 3] [4] [[] cons cons] . step i
      [[1 2] 3] 4 [[] cons cons] . i i
                     [[1 2] 3] 4 . [] cons cons i
                  [[1 2] 3] 4 [] . cons cons i
                   [[1 2] 3] [4] . cons i
                   [[[1 2] 3] 4] . i
                                 . [[1 2] 3] 4
                       [[1 2] 3] . 4
                     [[1 2] 3] 4 . 


And here it is doing the main thing.


```python
J('[1 [2 [3 4 25 6] 7] 8] [sqr] [dip dip infra dip infra dip infra] Z')
```

    [1 [2 [3 4 625 6] 7] 8]


## Addressing
Because we are only using two combinators we could replace the list with a string made from only two characters.

       [...] [Q] 'ddididi' Zstr
    -------------------------------------------------------------
       [...] [[[[[[[Q] dip] dip] infra] dip] infra] dip] infra

The string can be considered a name or address for an item in the subject datastructure.

## Determining the right "path" for an item in a tree.
It's easy to read off (in reverse) the right sequence of "d" and "i" from the subject datastructure:

    [ n [ n [ n n x ...
    i d i d i d d Bingo!
