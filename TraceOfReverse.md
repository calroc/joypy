# Reversing a Sequence #

If we want to reverse the order of items in a sequence we can make use of the functions `swap` and `cons` and the combinator `step`.

## Definitions ##

We can take the items in the sequence one-by-one with the help of the `step` combinator, and then we just need to `cons` them onto a new sequence and they will be in reverse order.

```
    swons == swap cons ;
    shunt == [swons] step ;
  reverse == [] swap shunt ;
```

## Operation ##

Here is the `reverse` function in operation (the • gives the "location" of the interpreter in the processing):

```
  joy? [1 2 3] reverse
   • [1 2 3] reverse
  [1 2 3] • reverse
  # reverse == [] swap shunt
  [1 2 3] • [] swap shunt
  [1 2 3] [] • swap shunt
  [] [1 2 3] • shunt
  # shunt == [swons] step
  [] [1 2 3] • [swons] step
  [] [1 2 3] [swons] • step
  [] 1 • swons
  # swons == swap cons
  [] 1 • swap cons
  1 [] • cons
  # swons done.
  [1] 2 • swons
  # swons == swap cons
  [1] 2 • swap cons
  2 [1] • cons
  # swons done.
  [2 1] 3 • swons
  # swons == swap cons
  [2 1] 3 • swap cons
  3 [2 1] • cons
  # swons done.
  # shunt done.
  # reverse done.

  -> [3 2 1]

  joy? 
```