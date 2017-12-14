
# Advent of Code 2017

## December 5th
...a list of the offsets for each jump. Jumps are relative: -1 moves to the previous instruction, and 2 skips the next one. Start at the first instruction in the list. The goal is to follow the jumps until one leads outside the list.

In addition, these instructions are a little strange; after each jump, the offset of that instruction increases by 1. So, if you come across an offset of 3, you would move three instructions forward, but change it to a 4 for the next time it is encountered.

For example, consider the following list of jump offsets:

    0
    3
    0
    1
    -3

Positive jumps ("forward") move downward; negative jumps move upward. For legibility in this example, these offset values will be written all on one line, with the current instruction marked in parentheses. The following steps would be taken before an exit is found:

*    (0) 3  0  1  -3  - before we have taken any steps.
*    (1) 3  0  1  -3  - jump with offset 0 (that is, don't jump at all). Fortunately, the instruction is then incremented to 1.
*     2 (3) 0  1  -3  - step forward because of the instruction we just modified. The first instruction is incremented again, now to 2.
*     2  4  0  1 (-3) - jump all the way to the end; leave a 4 behind.
*     2 (4) 0  1  -2  - go back to where we just were; increment -3 to -2.
*     2  5  0  1  -2  - jump 4 steps forward, escaping the maze.

In this example, the exit is reached in 5 steps.

How many steps does it take to reach the exit?

## Breakdown
For now, I'm going to assume a starting state with the size of the sequence pre-computed.  We need it to define the exit condition and it is a trivial preamble to generate it.  We then need and `index` and a `step-count`, which are both initially zero.  Then we have the sequence itself, and some recursive function `F` that does the work.

       size index step-count [...] F
    -----------------------------------
                step-count

    F == [P] [T] [R1] [R2] genrec

Later on I was thinking about it and the Forth heuristic came to mind, to wit: four things on the stack are kind of much.  Immediately I realized that the size properly belongs in the predicate of `F`!  D'oh!

       index step-count [...] F
    ------------------------------
             step-count

So, let's start by nailing down the predicate:

    F == [P] [T] [R1]   [R2] genrec
      == [P] [T] [R1 [F] R2] ifte

    0 0 [0 3 0 1 -3] popop 5 >=

    P == popop 5 >=

Now we need the else-part:

    index step-count [0 3 0 1 -3] roll< popop

    E == roll< popop

Last but not least, the recursive branch

    0 0 [0 3 0 1 -3] R1 [F] R2

The `R1` function has a big job:

    R1 == get the value at index
          increment the value at the index
          add the value gotten to the index
          increment the step count

The only tricky thing there is incrementing an integer in the sequence.  Joy sequences are not particularly good for random access.  We could encode the list of jump offsets in a big integer and use math to do the processing for a good speed-up, but it still wouldn't beat the performance of e.g. a mutable array.  This is just one of those places where "plain vanilla" Joypy doesn't shine (in default performance.  The legendary *Sufficiently-Smart Compiler* would of course rewrite this function to use an array "under the hood".)

In the meantime, I'm going to write a primitive function that just does what we need.


```python
from notebook_preamble import D, J, V, define
from joy.library import SimpleFunctionWrapper
from joy.utils.stack import list_to_stack


@SimpleFunctionWrapper
def incr_at(stack):
    '''Given a index and a sequence of integers, increment the integer at the index.

    E.g.:

       3 [0 1 2 3 4 5] incr_at
    -----------------------------
         [0 1 2 4 4 5]
    
    '''
    sequence, (i, stack) = stack
    mem = []
    while i >= 0:
        term, sequence = sequence
        mem.append(term)
        i -= 1
    mem[-1] += 1
    return list_to_stack(mem, sequence), stack


D['incr_at'] = incr_at
```


```python
J('3 [0 1 2 3 4 5] incr_at')
```

    [0 1 2 4 4 5]


### get the value at index

    3 0 [0 1 2 3 4] [roll< at] nullary
    3 0 [0 1 2 n 4] n

### increment the value at the index

    3 0 [0 1 2 n 4] n [Q] dip
    3 0 [0 1 2 n 4] Q n
    3 0 [0 1 2 n 4] [popd incr_at] unary n
    3 0 [0 1 2 n+1 4] n

### add the value gotten to the index

    3 0 [0 1 2 n+1 4] n [+] cons dipd
    3 0 [0 1 2 n+1 4] [n +]      dipd
    3 n + 0 [0 1 2 n+1 4]
    3+n   0 [0 1 2 n+1 4]

### increment the step count

    3+n 0 [0 1 2 n+1 4] [++] dip
    3+n 1 [0 1 2 n+1 4]

### All together now...

    get_value == [roll< at] nullary
    incr_value == [[popd incr_at] unary] dip
    add_value == [+] cons dipd
    incr_step_count == [++] dip

    R1 == get_value incr_value add_value incr_step_count

    F == [P] [T] [R1] primrec
    
    F == [popop !size! >=] [roll< pop] [get_value incr_value add_value incr_step_count] primrec


```python
from joy.library import DefinitionWrapper


DefinitionWrapper.add_definitions('''

      get_value == [roll< at] nullary
     incr_value == [[popd incr_at] unary] dip
      add_value == [+] cons dipd
incr_step_count == [++] dip

     AoC2017.5.0 == get_value incr_value add_value incr_step_count

''', D)
```


```python
define('F == [popop 5 >=] [roll< popop] [AoC2017.5.0] primrec')
```


```python
J('0 0 [0 3 0 1 -3] F')
```

    5


### Preamble for setting up predicate, `index`, and `step-count`

We want to go from this to this:

       [...] AoC2017.5.preamble
    ------------------------------
        0 0 [...] [popop n >=]

Where `n` is the size of the sequence.

The first part is obviously `0 0 roll<`, then `dup size`:

    [...] 0 0 roll< dup size
    0 0 [...] n

Then:

    0 0 [...] n [>=] cons [popop] swoncat

So:

    init-index-and-step-count == 0 0 roll<
    prepare-predicate == dup size [>=] cons [popop] swoncat

    AoC2017.5.preamble == init-index-and-step-count prepare-predicate


```python
DefinitionWrapper.add_definitions('''

init-index-and-step-count == 0 0 roll<
        prepare-predicate == dup size [>=] cons [popop] swoncat

       AoC2017.5.preamble == init-index-and-step-count prepare-predicate

                AoC2017.5 == AoC2017.5.preamble [roll< popop] [AoC2017.5.0] primrec

''', D)
```


```python
J('[0 3 0 1 -3] AoC2017.5')
```

    5



                    AoC2017.5 == AoC2017.5.preamble [roll< popop] [AoC2017.5.0] primrec

                  AoC2017.5.0 == get_value incr_value add_value incr_step_count
           AoC2017.5.preamble == init-index-and-step-count prepare-predicate

                    get_value == [roll< at] nullary
                   incr_value == [[popd incr_at] unary] dip
                    add_value == [+] cons dipd
              incr_step_count == [++] dip

    init-index-and-step-count == 0 0 roll<
            prepare-predicate == dup size [>=] cons [popop] swoncat


This is by far the largest program I have yet written in Joy.  Even with the `incr_at` function it is still a bear.  There may be an arrangement of the parameters that would permit more elegant definitions, but it still wouldn't be as efficient as something written in assembly, C, or even Python.
