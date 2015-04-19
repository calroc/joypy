BTree
=================================

This is a simple Binary Tree implementation that uses tuples in such a
way as to permit "persistant" usage, i.e. all previous versions of the
btree datastructures are retained and available (provided you don't throw
them away yourself.)

The empty tree is represented as an empty tuple.  Nodes are a tuple
consisting of a key, a value, and two (possible empty) sub-nodes for the
lower and higher branches of the tree.

This module defines the following functions:

    insert(node, key, value)

    get(node, key)

    delete(node, key)

Both insert() and delete() return a new tuple that is the result of
applying the operation to the existing node.  (And both get() and delete()
will raise KeyErrors if the key is not in the tree.)

Because of the way that insert() and delete() are written, only as much
of the tree is changed as necessary and the rest of it is reused. This
provides persistance without using up memory for each version of the
tree.

These functions are implemented recursively so they have the potential to
raise a RuntimeError if the maximum recursion depth is exceeded.  This
should only be a problem if used with very large trees.  To avoid this
issue you can use sys.setrecursionlimit(), but I think I might just
rewrite these to not use recursion.

## insert()

Return a tree with value stored under key. Replaces old value if any.

~~~~ {.python .numberLines startFrom="60"}
def insert(node, key, value):
  if not node:
    return key, (value, ((), ((), ())))

  node_key, (node_value, (lower, (higher, _))) = node

  if key < node_key:
    return node_key, (node_value, (insert(lower, key, value), (higher, ())))

  if key > node_key:
    return node_key, (node_value, (lower, (insert(higher, key, value), ())))

  return key, (value, (lower, (higher, ())))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## get()

Return the value stored under key or raise KeyError if not found.

~~~~ {.python .numberLines startFrom="80"}
def get(node, key):
  if not node:
    raise KeyError, key

  node_key, (value, (lower, (higher, _))) = node

  if key == node_key:
    return value

  return get(lower if key < node_key else higher, key)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## delete()

Return a tree with the value (and key) removed or raise KeyError if
not found.

~~~~ {.python .numberLines startFrom="98"}
def delete(node, key):
  if not node:
    raise KeyError, key

  node_key, (value, (lower, (higher, _))) = node

  if key < node_key:
    return node_key, (value, (delete(lower, key), (higher, ())))

  if key > node_key:
    return node_key, (value, (lower, (delete(higher, key), ())))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

So, key == node_key, delete this node itself.

  If we only have one non-empty child node return it.  If both child
  nodes are empty return an empty node (one of the children.)

~~~~ {.python .numberLines startFrom="115"}
  if not lower:
    return higher
  if not higher:
    return lower
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If both child nodes are non-empty, we find the highest node in our
  lower sub-tree, take its key and value to replace (delete) our own,
  then get rid of it by recursively calling delete() on our lower
  sub-node with our new key.

  (We could also find the lowest node in our higher sub-tree and take
  its key and value and delete it. I only implemented one of these
  two symmetrical options. Over a lot of deletions this might make
  the tree more unbalanced.  Oh well.)

~~~~ {.python .numberLines startFrom="130"}
  node = lower
  while node[1][1][1][0]:
    node = node[1][1][1][0]
  key, value = node[0], node[1][0]

  return key, (value, (delete(lower, key), (higher, ())))
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The above functions are the "core" functionality for dealing with this
tuple-based persistant BTree datastructure.  The rest of this module is
just helper functions.

## items()

Iterate in order over the (key, value) pairs in a tree.

~~~~ {.python .numberLines startFrom="148"}
def items(node):
  if not node:
    return

  key, (value, (lower, (higher, _))) = node

  for kv in items(lower):
    yield kv

  yield key, value

  for kv in items(higher):
    yield kv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### yield_balanced()

Recursive generator function to yield the items in a sorted sequence
in such a way as to fill a btree in a balanced fashion.

~~~~ {.python .numberLines startFrom="169"}
def _yield_balanced(sorted_items):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For empty sequences do nothing.

~~~~ {.python .numberLines startFrom="173"}
  if not sorted_items:
    return
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find the index of the middle item (rounding down for even-length
  sequences due to integer division.)

~~~~ {.python .numberLines startFrom="179"}
  i = len(sorted_items) / 2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yield the middle item.

~~~~ {.python .numberLines startFrom="183"}
  yield sorted_items[i]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shortcut in case the length of `sorted_items` is one.

~~~~ {.python .numberLines startFrom="187"}
  if not i:
    return
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now recurse on lower and higher halves of the sequence.

~~~~ {.python .numberLines startFrom="192"}
  for low in _yield_balanced(sorted_items[:i]):
    yield low
  for high in _yield_balanced(sorted_items[i+1:]):
    yield high
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## fill_tree()

Add the (key, value) pairs in items to a btree in a balanced way.

You can balance a tree like so:

    tree = fill_tree((), items(tree))

This iterates through the tree and returns a new, balanced tree from
its contents.

~~~~ {.python .numberLines startFrom="210"}
def fill_tree(node, items):
  for key, value in _yield_balanced(sorted(items)):
    node = insert(node, key, value)
  return node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



