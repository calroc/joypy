
# Treating Trees
Although any expression in Joy can be considered to describe a [tree](https://en.wikipedia.org/wiki/Tree_structure) with the quotes as compound nodes and the non-quote values as leaf nodes, in this page I want to talk about [ordered binary trees](https://en.wikipedia.org/wiki/Binary_search_tree) and how to make and use them.

The basic structure, in a [crude type notation](https://en.wikipedia.org/wiki/Algebraic_data_type), is:

    BTree :: [] | [key value BTree BTree]
    
That says that a BTree is either the empty quote `[]` or a quote with four items: a key, a value, and two BTrees representing the left and right branches of the tree.

## A Function to Traverse this Structure
Let's take a crack at writing a function that can recursively iterate or traverse these trees.

#### Base case `[]`
The stopping predicate just has to detect the empty list:

    BTree-iter == [not] [E] [R0] [R1] genrec

And since there's nothing at this node, we just `pop` it:

    BTree-iter == [not] [pop] [R0] [R1] genrec

#### Node case `[key value left right]`
Now we need to figure out `R0` and `R1`: 

    BTree-iter == [not] [pop] [R0]            [R1] genrec
               == [not] [pop] [R0 [BTree-iter] R1] ifte

Let's look at it *in situ*:

    [key value left right] R0 [BTree-iter] R1

#### Processing the current node.

`R0` is almost certainly going to use `dup` to make a copy of the node and then `dip` on some function to process the copy with it:

    [key value left right] [F] dupdip                 [BTree-iter] R1
    [key value left right]  F  [key value left right] [BTree-iter] R1

For example, if we're getting all the keys `F` would be `first`:

    R0 == [first] dupdip

    [key value left right] [first] dupdip                 [BTree-iter] R1
    [key value left right]  first  [key value left right] [BTree-iter] R1
    key                            [key value left right] [BTree-iter] R1

#### Recur
Now `R1` needs to apply `[BTree-iter]` to `left` and `right`.  If we drop the key and value from the node using `rest` twice we are left with an interesting situation:

    key [key value left right] [BTree-iter] R1
    key [key value left right] [BTree-iter] [rest rest] dip
    key [key value left right] rest rest [BTree-iter]
    key [left right] [BTree-iter]

Hmm, will `step` do?

    key [left right] [BTree-iter] step
    key left BTree-iter [right] [BTree-iter] step
    key left-keys [right] [BTree-iter] step
    key left-keys right BTree-iter
    key left-keys right-keys

Wow. So:

    R1 == [rest rest] dip step

#### Parameterizing the `F` per-node processing function.

    [F] BTree-iter == [not] [pop] [[F] dupdip] [[rest rest] dip step] genrec

Working backward:

    [not] [pop] [[F] dupdip]            [[rest rest] dip step] genrec
    [not] [pop] [F]       [dupdip] cons [[rest rest] dip step] genrec
    [F] [not] [pop] roll< [dupdip] cons [[rest rest] dip step] genrec

Ergo:

    BTree-iter == [not] [pop] roll< [dupdip] cons [[rest rest] dip step] genrec


```python
from notebook_preamble import J, V, define
```


```python
define('BTree-iter == [not] [pop] roll< [dupdip] cons [[rest rest] dip step] genrec')
```


```python
J('[] [23] BTree-iter')  #  It doesn't matter what F is as it won't be used.
```

    



```python
J('["tommy" 23 [] []] [first] BTree-iter')
```

    'tommy'



```python
J('["tommy" 23 ["richard" 48 [] []] ["jenny" 18 [] []]] [first] BTree-iter')
```

    'tommy' 'richard' 'jenny'



```python
J('["tommy" 23 ["richard" 48 [] []] ["jenny" 18 [] []]] [second] BTree-iter')
```

    23 48 18


# Adding Nodes to the BTree
Let's consider adding nodes to a BTree structure.

    BTree value key BTree-add == BTree

#### Adding to an empty node.
If the current node is `[]` then you just return `[key value [] []]`:

    BTree-add == [popop not] [[pop] dipd BTree-new] [R0] [R1] genrec

Where `BTree-new` is:

    value key BTree-new == [key value [] []]

    value key swap [[] []] cons cons
    key value      [[] []] cons cons
    key      [value [] []]      cons
         [key value [] []]

    BTree-new == swap [[] []] cons cons


```python
define('BTree-new == swap [[] []] cons cons')
```


```python
V('"v" "k" BTree-new')
```

                    . 'v' 'k' BTree-new
                'v' . 'k' BTree-new
            'v' 'k' . BTree-new
            'v' 'k' . swap [[] []] cons cons
            'k' 'v' . [[] []] cons cons
    'k' 'v' [[] []] . cons cons
    'k' ['v' [] []] . cons
    ['k' 'v' [] []] . 


(As an implementation detail, the `[[] []]` literal used in the definition of `BTree-new` will be reused to supply the *constant* tail for *all* new nodes produced by it.  This is one of those cases where you get amortized storage "for free" by using [persistent datastructures](https://en.wikipedia.org/wiki/Persistent_data_structure).  Because the tail, which is `((), ((), ()))` in Python, is immutable and embedded in the definition body for `BTree-new`, all new nodes can reuse it as their own tail without fear that some other code somewhere will change it.)

#### If the current node isn't empty.

We now have to derive `R0` and `R1`, consider:

    [key_n value_n left right] value key R0 [BTree-add] R1

In this case, there are three possibilites: the key can be greater or less than or equal to the node's key.  In two of those cases we will need to apply a copy of `BTree-add`, so `R0` is pretty much out of the picture.

    [R0] == []

#### A predicate to compare keys.
The first thing we need to do is compare the the key we're adding to see if it is greater than the node key and `branch` accordingly, although in this case it's easier to write a destructive predicate and then use `ifte` to apply it `nullary`:

    [key_n value_n left right] value key [BTree-add] R1
    [key_n value_n left right] value key [BTree-add] [P >] [T] [E] ifte

    [key_n value_n left right] value key [BTree-add] P                   >
    [key_n value_n left right] value key [BTree-add] pop roll> pop first >
    [key_n value_n left right] value key                 roll> pop first >
    key [key_n value_n left right] value                 roll> pop first >
    key key_n                                                            >
    Boolean

    P > == pop roll> pop first >
    P < == pop roll> pop first <
    P   == pop roll> pop first


```python
define('P == pop roll> pop first')
```


```python
V('["k" "v" [] []] "vv" "kk" [0] P >')
```

                                  . ['k' 'v' [] []] 'vv' 'kk' [0] P >
                  ['k' 'v' [] []] . 'vv' 'kk' [0] P >
             ['k' 'v' [] []] 'vv' . 'kk' [0] P >
        ['k' 'v' [] []] 'vv' 'kk' . [0] P >
    ['k' 'v' [] []] 'vv' 'kk' [0] . P >
    ['k' 'v' [] []] 'vv' 'kk' [0] . pop roll> pop first >
        ['k' 'v' [] []] 'vv' 'kk' . roll> pop first >
        'kk' ['k' 'v' [] []] 'vv' . pop first >
             'kk' ['k' 'v' [] []] . first >
                         'kk' 'k' . >
                             True . 


#### If the key we're adding is greater than the node's key.

Here the parantheses are meant to signify that the right-hand side (RHS) is not literal, the code in the parentheses is meant to have been evaluated:

    [key_n value_n left right] value key [BTree-add] T == [key_n value_n left (BTree-add key value right)]

#### Use `infra` on `K`.
So how do we do this?  We know we're going to want to use `infra` on some function `K` that has the key and value to work with, as well as the quoted copy of `BTree-add` to apply somehow:

    right left value_n key_n value key [BTree-add] K
        ...
    right value key BTree-add left value_n key_n

Pretty easy:

    right left value_n key_n value key [BTree-add] cons cons dipdd
    right left value_n key_n [value key BTree-add]           dipdd
    right value key BTree-add left value_n key_n

So:

    K == cons cons dipdd

And:

    [key_n value_n left right] [value key [BTree-add] K] infra

#### Derive `T`.
So now we're at getting from this to this:

    [key_n value_n left right]  value key [BTree-add] T
        ...
    [key_n value_n left right] [value key [BTree-add] K] infra

And so `T` is just:

    value key [BTree-add] T == [value key [BTree-add] K]                infra
                          T == [                      K] cons cons cons infra


```python
define('K == cons cons dipdd')
define('T == [K] cons cons cons infra')
```


```python
V('"r" "l" "v" "k" "vv" "kk" [0] K')
```

                                  . 'r' 'l' 'v' 'k' 'vv' 'kk' [0] K
                              'r' . 'l' 'v' 'k' 'vv' 'kk' [0] K
                          'r' 'l' . 'v' 'k' 'vv' 'kk' [0] K
                      'r' 'l' 'v' . 'k' 'vv' 'kk' [0] K
                  'r' 'l' 'v' 'k' . 'vv' 'kk' [0] K
             'r' 'l' 'v' 'k' 'vv' . 'kk' [0] K
        'r' 'l' 'v' 'k' 'vv' 'kk' . [0] K
    'r' 'l' 'v' 'k' 'vv' 'kk' [0] . K
    'r' 'l' 'v' 'k' 'vv' 'kk' [0] . cons cons dipdd
    'r' 'l' 'v' 'k' 'vv' ['kk' 0] . cons dipdd
    'r' 'l' 'v' 'k' ['vv' 'kk' 0] . dipdd
                              'r' . 'vv' 'kk' 0 'l' 'v' 'k'
                         'r' 'vv' . 'kk' 0 'l' 'v' 'k'
                    'r' 'vv' 'kk' . 0 'l' 'v' 'k'
                  'r' 'vv' 'kk' 0 . 'l' 'v' 'k'
              'r' 'vv' 'kk' 0 'l' . 'v' 'k'
          'r' 'vv' 'kk' 0 'l' 'v' . 'k'
      'r' 'vv' 'kk' 0 'l' 'v' 'k' . 



```python
V('["k" "v" "l" "r"] "vv" "kk" [0] T')
```

                                        . ['k' 'v' 'l' 'r'] 'vv' 'kk' [0] T
                      ['k' 'v' 'l' 'r'] . 'vv' 'kk' [0] T
                 ['k' 'v' 'l' 'r'] 'vv' . 'kk' [0] T
            ['k' 'v' 'l' 'r'] 'vv' 'kk' . [0] T
        ['k' 'v' 'l' 'r'] 'vv' 'kk' [0] . T
        ['k' 'v' 'l' 'r'] 'vv' 'kk' [0] . [K] cons cons cons infra
    ['k' 'v' 'l' 'r'] 'vv' 'kk' [0] [K] . cons cons cons infra
    ['k' 'v' 'l' 'r'] 'vv' 'kk' [[0] K] . cons cons infra
    ['k' 'v' 'l' 'r'] 'vv' ['kk' [0] K] . cons infra
    ['k' 'v' 'l' 'r'] ['vv' 'kk' [0] K] . infra
                        'r' 'l' 'v' 'k' . 'vv' 'kk' [0] K [] swaack
                   'r' 'l' 'v' 'k' 'vv' . 'kk' [0] K [] swaack
              'r' 'l' 'v' 'k' 'vv' 'kk' . [0] K [] swaack
          'r' 'l' 'v' 'k' 'vv' 'kk' [0] . K [] swaack
          'r' 'l' 'v' 'k' 'vv' 'kk' [0] . cons cons dipdd [] swaack
          'r' 'l' 'v' 'k' 'vv' ['kk' 0] . cons dipdd [] swaack
          'r' 'l' 'v' 'k' ['vv' 'kk' 0] . dipdd [] swaack
                                    'r' . 'vv' 'kk' 0 'l' 'v' 'k' [] swaack
                               'r' 'vv' . 'kk' 0 'l' 'v' 'k' [] swaack
                          'r' 'vv' 'kk' . 0 'l' 'v' 'k' [] swaack
                        'r' 'vv' 'kk' 0 . 'l' 'v' 'k' [] swaack
                    'r' 'vv' 'kk' 0 'l' . 'v' 'k' [] swaack
                'r' 'vv' 'kk' 0 'l' 'v' . 'k' [] swaack
            'r' 'vv' 'kk' 0 'l' 'v' 'k' . [] swaack
         'r' 'vv' 'kk' 0 'l' 'v' 'k' [] . swaack
          ['k' 'v' 'l' 0 'kk' 'vv' 'r'] . 


#### If the key we're adding is less than the node's key.
This is very very similar to the above:

    [key_n value_n left right] value key [BTree-add] E
    [key_n value_n left right] value key [BTree-add] [P <] [Te] [Ee] ifte

In this case `Te` works that same as `T` but on the left child tree instead of the right, so the only difference is that it must use `dipd` instead of `dipdd`:

    Te == [cons cons dipd] cons cons cons infra

This suggests an alternate factorization:

    ccons == cons cons
    T == [ccons dipdd] ccons cons infra
    Te == [ccons dipd] ccons cons infra

But whatever.


```python
define('Te == [cons cons dipd] cons cons cons infra')
```


```python
V('["k" "v" "l" "r"] "vv" "kk" [0] Te')
```

                                                     . ['k' 'v' 'l' 'r'] 'vv' 'kk' [0] Te
                                   ['k' 'v' 'l' 'r'] . 'vv' 'kk' [0] Te
                              ['k' 'v' 'l' 'r'] 'vv' . 'kk' [0] Te
                         ['k' 'v' 'l' 'r'] 'vv' 'kk' . [0] Te
                     ['k' 'v' 'l' 'r'] 'vv' 'kk' [0] . Te
                     ['k' 'v' 'l' 'r'] 'vv' 'kk' [0] . [cons cons dipd] cons cons cons infra
    ['k' 'v' 'l' 'r'] 'vv' 'kk' [0] [cons cons dipd] . cons cons cons infra
    ['k' 'v' 'l' 'r'] 'vv' 'kk' [[0] cons cons dipd] . cons cons infra
    ['k' 'v' 'l' 'r'] 'vv' ['kk' [0] cons cons dipd] . cons infra
    ['k' 'v' 'l' 'r'] ['vv' 'kk' [0] cons cons dipd] . infra
                                     'r' 'l' 'v' 'k' . 'vv' 'kk' [0] cons cons dipd [] swaack
                                'r' 'l' 'v' 'k' 'vv' . 'kk' [0] cons cons dipd [] swaack
                           'r' 'l' 'v' 'k' 'vv' 'kk' . [0] cons cons dipd [] swaack
                       'r' 'l' 'v' 'k' 'vv' 'kk' [0] . cons cons dipd [] swaack
                       'r' 'l' 'v' 'k' 'vv' ['kk' 0] . cons dipd [] swaack
                       'r' 'l' 'v' 'k' ['vv' 'kk' 0] . dipd [] swaack
                                             'r' 'l' . 'vv' 'kk' 0 'v' 'k' [] swaack
                                        'r' 'l' 'vv' . 'kk' 0 'v' 'k' [] swaack
                                   'r' 'l' 'vv' 'kk' . 0 'v' 'k' [] swaack
                                 'r' 'l' 'vv' 'kk' 0 . 'v' 'k' [] swaack
                             'r' 'l' 'vv' 'kk' 0 'v' . 'k' [] swaack
                         'r' 'l' 'vv' 'kk' 0 'v' 'k' . [] swaack
                      'r' 'l' 'vv' 'kk' 0 'v' 'k' [] . swaack
                       ['k' 'v' 0 'kk' 'vv' 'l' 'r'] . 


#### Else the keys must be equal.
This means we must find:

    [key_n value_n left right] value key [BTree-add] Ee
        ...
    [key value left right]

This is another easy one:

    Ee == pop swap roll< rest rest cons cons

    [key_n value_n left right] value key [BTree-add] pop swap roll< rest rest cons cons
    [key_n value_n left right] value key                 swap roll< rest rest cons cons
    [key_n value_n left right] key value                      roll< rest rest cons cons
    key value [key_n value_n left right]                            rest rest cons cons
    key value [              left right]                                      cons cons
              [key   value   left right]


```python
define('Ee == pop swap roll< rest rest cons cons')
```


```python
V('["k" "v" "l" "r"] "vv" "k" [0] Ee')
```

                                   . ['k' 'v' 'l' 'r'] 'vv' 'k' [0] Ee
                 ['k' 'v' 'l' 'r'] . 'vv' 'k' [0] Ee
            ['k' 'v' 'l' 'r'] 'vv' . 'k' [0] Ee
        ['k' 'v' 'l' 'r'] 'vv' 'k' . [0] Ee
    ['k' 'v' 'l' 'r'] 'vv' 'k' [0] . Ee
    ['k' 'v' 'l' 'r'] 'vv' 'k' [0] . pop swap roll< rest rest cons cons
        ['k' 'v' 'l' 'r'] 'vv' 'k' . swap roll< rest rest cons cons
        ['k' 'v' 'l' 'r'] 'k' 'vv' . roll< rest rest cons cons
        'k' 'vv' ['k' 'v' 'l' 'r'] . rest rest cons cons
            'k' 'vv' ['v' 'l' 'r'] . rest cons cons
                'k' 'vv' ['l' 'r'] . cons cons
                'k' ['vv' 'l' 'r'] . cons
                ['k' 'vv' 'l' 'r'] . 



```python
define('E == [P <] [Te] [Ee] ifte')
```

#### Now we can define `BTree-add`
    BTree-add == [popop not] [[pop] dipd BTree-new] [] [[P >] [T] [E] ifte] genrec

Putting it all together:

    BTree-new == swap [[] []] cons cons
    P == pop roll> pop first
    T == [cons cons dipdd] cons cons cons infra
    Te == [cons cons dipd] cons cons cons infra
    Ee == pop swap roll< rest rest cons cons
    E == [P <] [Te] [Ee] ifte

    BTree-add == [popop not] [[pop] dipd BTree-new] [] [[P >] [T] [E] ifte] genrec


```python
define('BTree-add == [popop not] [[pop] dipd BTree-new] [] [[P >] [T] [E] ifte] genrec')
```


```python
J('[] 23 "b" BTree-add')  # Initial
```

    ['b' 23 [] []]



```python
J('["b" 23 [] []] 88 "c" BTree-add')  # Less than
```

    ['b' 23 [] ['c' 88 [] []]]



```python
J('["b" 23 [] []] 88 "a" BTree-add')  # Greater than
```

    ['b' 23 ['a' 88 [] []] []]



```python
J('["b" 23 [] []] 88 "b" BTree-add')  # Equal to
```

    ['b' 88 [] []]



```python
J('[] 23 "a" BTree-add 88 "b" BTree-add 44 "c" BTree-add')  # Series.
```

    ['a' 23 [] ['b' 88 [] ['c' 44 [] []]]]


We can use this to make a set-like datastructure by just setting values to e.g. 0 and ignoring them.  It's set-like in that duplicate items added to it will only occur once within it, and we can query it in [$O(\log_2 N)$](https://en.wikipedia.org/wiki/Binary_search_tree#cite_note-2) time.


```python
J('[] [3 9 5 2 8 6 7 8 4] [0 swap BTree-add] step')
```

    [3 0 [2 0 [] []] [9 0 [5 0 [4 0 [] []] [8 0 [6 0 [] [7 0 [] []]] []]] []]]



```python
define('to_set == [] swap [0 swap BTree-add] step')
```


```python
J('[3 9 5 2 8 6 7 8 4] to_set')
```

    [3 0 [2 0 [] []] [9 0 [5 0 [4 0 [] []] [8 0 [6 0 [] [7 0 [] []]] []]] []]]


And with that we can write a little program to remove duplicate items from a list.


```python
define('unique == [to_set [first] BTree-iter] cons run')
```


```python
J('[3 9 3 5 2 9 8 8 8 6 2 7 8 4 3] unique')  # Filter duplicate items.
```

    [7 6 8 4 5 9 2 3]


# `cmp` combinator
Instead of all this mucking about with nested `ifte` let's just go whole hog and define `cmp` which takes two values and three quoted programs on the stack and runs one of the three depending on the results of comparing the two values:

       a b [G] [E] [L] cmp
    ------------------------- a > b
            G

       a b [G] [E] [L] cmp
    ------------------------- a = b
                E

       a b [G] [E] [L] cmp
    ------------------------- a < b
                    L

We need a new non-destructive predicate `P`:

    [key_n value_n left right] value key [BTree-add] P
    [key_n value_n left right] value key [BTree-add] over [Q] nullary
    [key_n value_n left right] value key [BTree-add] key  [Q] nullary
    [key_n value_n left right] value key [BTree-add] key   Q
    [key_n value_n left right] value key [BTree-add] key   popop popop first
    [key_n value_n left right] value key                         popop first
    [key_n value_n left right]                                         first
     key_n
    [key_n value_n left right] value key [BTree-add] key  [Q] nullary
    [key_n value_n left right] value key [BTree-add] key key_n

    P == over [popop popop first] nullary

Here are the definitions again, pruned and renamed in some cases:

    BTree-new == swap [[] []] cons cons
    P == over [popop popop first] nullary
    T> == [cons cons dipdd] cons cons cons infra
    T< == [cons cons dipd] cons cons cons infra
    E == pop swap roll< rest rest cons cons

Using `cmp` to simplify [our code above at `R1`](#If-the-current-node-isn't-empty.):

    [key_n value_n left right] value key [BTree-add] R1
    [key_n value_n left right] value key [BTree-add] P [T>] [E] [T<] cmp

The line above becomes one of the three lines below:

    [key_n value_n left right] value key [BTree-add] T>
    [key_n value_n left right] value key [BTree-add] E
    [key_n value_n left right] value key [BTree-add] T<

The definition is a little longer but, I think, more elegant and easier to understand:

    BTree-add == [popop not] [[pop] dipd BTree-new] [] [P [T>] [E] [T<] cmp] genrec



```python
from joy.library import FunctionWrapper
from joy.utils.stack import pushback
from notebook_preamble import D


@FunctionWrapper
def cmp_(stack, expression, dictionary):
    L, (E, (G, (b, (a, stack)))) = stack
    expression = pushback(G if a > b else L if a < b else E, expression)
    return stack, expression, dictionary


D['cmp'] = cmp_
```


```python
J("1 0 ['G'] ['E'] ['L'] cmp")
```

    'G'



```python
J("1 1 ['G'] ['E'] ['L'] cmp")
```

    'E'



```python
J("0 1 ['G'] ['E'] ['L'] cmp")
```

    'L'



```python
from joy.library import DefinitionWrapper


DefinitionWrapper.add_definitions('''

P == over [popop popop first] nullary
T> == [cons cons dipdd] cons cons cons infra
T< == [cons cons dipd] cons cons cons infra
E == pop swap roll< rest rest cons cons

BTree-add == [popop not] [[pop] dipd BTree-new] [] [P [T>] [E] [T<] cmp] genrec

''', D)
```


```python
J('[] 23 "b" BTree-add')  # Initial
```

    ['b' 23 [] []]



```python
J('["b" 23 [] []] 88 "c" BTree-add')  # Less than
```

    ['b' 23 [] ['c' 88 [] []]]



```python
J('["b" 23 [] []] 88 "a" BTree-add')  # Greater than
```

    ['b' 23 ['a' 88 [] []] []]



```python
J('["b" 23 [] []] 88 "b" BTree-add')  # Equal to
```

    ['b' 88 [] []]



```python
J('[] 23 "a" BTree-add 88 "b" BTree-add 44 "c" BTree-add')  # Series.
```

    ['a' 23 [] ['b' 88 [] ['c' 44 [] []]]]


### Specializing `cmp` for >= <= !=

    a b [G] [E] [L] cmp
    a b [GE] dup [L] cmp
    a b [G] [LE] dup cmp
    a b [NE] [E] over cmp

But you wouldn't do this, you would just use `>=` or whatever.  The `cmp` combinator is useful when you have to do three different things depending on the >=< greater-than, equal-to, or less-than result of comparison.

# Factoring and naming
It may seem silly, but a big part of programming in Forth (and therefore in Joy) is the idea of small, highly-factored definitions.  If you choose names carefully the resulting definitions can take on a semantic role.

    get-node-key == popop popop first
    remove-key-and-value-from-node == rest rest
    pack-key-and-value == cons cons
    prep-new-key-and-value == pop swap roll<
    pack-and-apply == [pack-key-and-value] swoncat cons pack-key-and-value infra

    BTree-new == swap [[] []] pack-key-and-value
    P == over [get-node-key] nullary
    T> == [dipdd] pack-and-apply
    T< == [dipd] pack-and-apply
    E == prep-new-key-and-value remove-key-and-value-from-node pack-key-and-value


# A Version of `BTree-iter` that does In-Order Traversal

If you look back to the [non-empty case of the `BTree-iter` function](#Node-case-[key-value-left-right]) we can design a varient that first processes the left child, then the current node, then the right child.  This will allow us to traverse the tree in sort order.

    BTree-iter-order == [not] [pop] [R0 [BTree-iter] R1] ifte

To define `R0` and `R1` it helps to look at them as they will appear when they run:

    [key value left right] R0 [BTree-iter-order] R1

#### Process the left child.
Staring at this for a bit suggests `dup third` to start:

    [key value left right] R0        [BTree-iter-order] R1
    [key value left right] dup third [BTree-iter-order] R1
    [key value left right] left      [BTree-iter-order] R1

Now maybe:

    [key value left right] left [BTree-iter-order] [cons dip] dupdip
    [key value left right] left [BTree-iter-order] cons dip [BTree-iter-order]
    [key value left right] [left BTree-iter-order]      dip [BTree-iter-order]
    left BTree-iter-order [key value left right]            [BTree-iter-order]

#### Process the current node.
So far, so good.  Now we need to process the current node's values:

    left BTree-iter-order [key value left right] [BTree-iter-order] [[F] dupdip] dip
    left BTree-iter-order [key value left right] [F] dupdip [BTree-iter-order]
    left BTree-iter-order [key value left right] F [key value left right] [BTree-iter-order]

If `F` needs items from the stack below the left stuff it should have `cons`'d them before beginning maybe?  For functions like `first` it works fine as-is.

    left BTree-iter-order [key value left right] first [key value left right] [BTree-iter-order]
    left BTree-iter-order key [key value left right] [BTree-iter-order]

#### Process the right child.
First ditch the rest of the node and get the right child:

    left BTree-iter-order key [key value left right] [BTree-iter-order] [rest rest rest first] dip
    left BTree-iter-order key right [BTree-iter-order]

Then, of course, we just need `i` to run `BTree-iter-order` on the right side:

    left BTree-iter-order key right [BTree-iter-order] i
    left BTree-iter-order key right BTree-iter-order

#### Defining `BTree-iter-order`
The result is a little awkward:

    R1 == [cons dip] dupdip [[F] dupdip] dip [rest rest rest first] dip i

Let's do a little semantic factoring:

    fourth == rest rest rest first

    proc_left == [cons dip] dupdip
    proc_current == [[F] dupdip] dip
    proc_right == [fourth] dip i

    BTree-iter-order == [not] [pop] [dup third] [proc_left proc_current proc_right] genrec

Now we can sort sequences.


```python
define('BTree-iter-order == [not] [pop] [dup third] [[cons dip] dupdip [[first] dupdip] dip [rest rest rest first] dip i] genrec')
```


```python
J('[3 9 5 2 8 6 7 8 4] to_set BTree-iter-order')
```

    2 3 4 5 6 7 8 9


## Miscellaneous Crap

### Toy with it.
Let's reexamine:

    [key value left right] R0 [BTree-iter-order] R1
        ...
    left BTree-iter-order key value F right BTree-iter-order


    [key value left right] disenstacken swap
     key value left right               swap
     key value right left

    key value right left [BTree-iter-order] [cons dipdd] dupdip
    key value right left [BTree-iter-order] cons dipdd [BTree-iter-order]
    key value right [left BTree-iter-order]      dipdd [BTree-iter-order]
    left BTree-iter-order key value right              [BTree-iter-order]

    left BTree-iter-order key value   right [F] dip [BTree-iter-order]
    left BTree-iter-order key value F right         [BTree-iter-order] i
    left BTree-iter-order key value F right          BTree-iter-order

So:

    R0 == disenstacken swap
    R1 == [cons dipdd [F] dip] dupdip i

    [key value left right] R0                [BTree-iter-order] R1
    [key value left right] disenstacken swap [BTree-iter-order] [cons dipdd [F] dip] dupdip i
     key value right left                    [BTree-iter-order] [cons dipdd [F] dip] dupdip i

     key value right left [BTree-iter-order] cons dipdd [F] dip [BTree-iter-order] i
     key value right [left BTree-iter-order]      dipdd [F] dip [BTree-iter-order] i
     left BTree-iter-order key value   right            [F] dip [BTree-iter-order] i
     left BTree-iter-order key value F right                    [BTree-iter-order] i
     left BTree-iter-order key value F right                     BTree-iter-order


    BTree-iter-order == [not] [pop] [disenstacken swap] [[cons dipdd [F] dip] dupdip i] genrec

#### Refactor `cons cons`
    cons2 == cons cons

Refactoring:

    BTree-new == swap [[] []] cons2
    T == [cons2 dipdd] cons2 cons infra
    Te == [cons2 dipd] cons2 cons infra
    Ee == pop swap roll< rest rest cons2

It's used a lot because it's tied to the fact that there are two "data items" in each node.  This point to a more general factorization that would render a combinator that could work for other geometries of trees.

## A General Form for Trees
A general form for tree data with N children per node:

    [[data] [child0] ... [childN-1]]

Suggests a general form of recursive iterator, but I have to go walk the dogs at the mo'.

#### Just make `[F]` a parameter.
We can generalize to a sort of pure form:

    BTree-iter == [not] [pop] [[F]]            [R1] genrec
               == [not] [pop] [[F] [BTree-iter] R1] ifte

Putting `[F]` to the left as a given:

     [F] unit [not] [pop] roll< [R1] genrec
    [[F]]     [not] [pop] roll< [R1] genrec
              [not] [pop] [[F]] [R1] genrec

Let's us define a parameterized form:

    BTree-iter == unit [not] [pop] roll< [R1] genrec

So in the general case of non-empty nodes:

    [key value left right] [F] [BTree-iter] R1

We just define `R1` to do whatever it has to to process the node.  For example:

    [key value left right] [F] [BTree-iter] R1
        ...
    key value F   left BTree-iter   right BTree-iter
    left BTree-iter   key value F   right BTree-iter
    left BTree-iter   right BTree-iter   key value F

Pre-, ??-, post-order traversals.

    [key value  left right] uncons uncons
     key value [left right]

For pre- and post-order we can use the `step` trick:

    [left right] [BTree-iter] step
        ...
    left BTree-iter right BTree-iter

We worked out one scheme for ?in-order? traversal above, but maybe we can do better?

    [key value left right]              [F] [BTree-iter] [disenstacken] dipd
    [key value left right] disenstacken [F] [BTree-iter]
     key value left right               [F] [BTree-iter]

    key value left right [F] [BTree-iter] R1.1

Hmm...

    key value left right              [F] [BTree-iter] tuck
    key value left right [BTree-iter] [F] [BTree-iter] 


    [key value left right]                          [F] [BTree-iter] [disenstacken [roll>] dip] dipd
    [key value left right] disenstacken [roll>] dip [F] [BTree-iter]
     key value left right               [roll>] dip [F] [BTree-iter]
     key value left roll> right                     [F] [BTree-iter]
     left key value right                           [F] [BTree-iter]

    left            key value   right              [F] [BTree-iter] tuck foo
    left            key value   right [BTree-iter] [F] [BTree-iter] foo
        ...
    left BTree-iter key value F right  BTree-iter

We could just let `[R1]` be a parameter too, for maximum flexibility.

#### Automatically deriving the recursion combinator for a data type?

If I understand it correctly, the "Bananas..." paper talks about a way to build the processor function automatically from the description of the type.  I think if we came up with an elegant way for the Joy code to express that, it would be cool.  In Joypy the definitions can be circular because lookup happens at evaluation, not parsing.  E.g.:

    A == ... B ...
    B == ... A ...

That's fine.  Circular datastructures can't be made though.


