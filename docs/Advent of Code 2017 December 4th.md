
# Advent of Code 2017

## December 4th
To ensure security, a valid passphrase must contain no duplicate words.

For example:

* aa bb cc dd ee is valid.
* aa bb cc dd aa is not valid - the word aa appears more than once.
* aa bb cc dd aaa is valid - aa and aaa count as different words.

The system's full passphrase list is available as your puzzle input. How many passphrases are valid?


```python
from notebook_preamble import J, V, define
```

I'll assume the input is a Joy sequence of sequences of integers.

    [[5 1 9 5]
     [7 5 4 3]
     [2 4 6 8]]

So, obviously, the initial form will be a `step` function:

    AoC2017.4 == 0 swap [F +] step


    F == [size] [unique size] cleave =


The `step_zero` combinator includes the `0 swap` that would normally open one of these definitions:


```python
J('[step_zero] help')
```

    0 roll> step
    


    AoC2017.4 == [F +] step_zero


```python
define('AoC2017.4 == [[size] [unique size] cleave = +] step_zero')
```


```python
J('''

[[5 1 9 5]
 [7 5 4 3]
 [2 4 6 8]] AoC2017.4

''')
```

    2

