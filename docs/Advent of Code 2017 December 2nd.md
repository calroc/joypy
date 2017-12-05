
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
define('AoC2017.2 == 0 swap [maxmin - +] step')
```


```python
J('''

[[5 1 9 5]
 [7 5 3]
 [2 4 6 8]] AoC2017.2

''')
```

    18

