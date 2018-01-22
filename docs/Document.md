
# Joy

This document is written to capture, at least crudely, the scope of application for Joy and the Joypy implementation.  It kind of expects that you have some familiarity with Joy already.

It is vaguely organized, in a pile.


## Syntax

Very simple syntax.  Could be specified as a sequence of one or more terms:

    joy ::= term term*

Conceptually, all terms are unary functions `F :: stack -> stack` that accept a stack and return a stack.  But we immediately differentiate between literals (of a few kinds), functions, and combinators (which like higher-order functions.)


### In Joypy there are currently four literal types.

First we have the types borrowed from the underlying Python semantics. **Strings** (byte and Unicode with nuances depending on whether you're running under Python 2 or 3), **ints**, and **floats**.  Then there is the **sequence** type, aka "quote", "list", etc...  In joy it is represented by enclosing zero or more terms in square brackets:

    sequence :== '[' term* ']'

(In Joypy it is implemented as a cons-list.  All datastructures in Joypy are built out of this single sequence type, including the stack and expression.  I could include Python `frozenset` but I don't.)

    literal ::= string | int | float | sequence

Functions accept zero or more arguments from the stack and push back zero or more results.

Combinators are functions one or more of the arguments to which are quotes containing joy expressions, and which then execute one or more of their quoted arguments to effect their function.

    term ::= literal | function | combinator

The code for the parser is in `joy/parser.py`.


## Semantics

In Joy juxtaposition of symbols is composition of functions.  That means that `F G` syntactically is `G(F(...))` semantically.

As it says in the [Wikipedia entry for Joypy](https://en.wikipedia.org/wiki/Joy_%28programming_language%29):

    "In Joy, the meaning function is a homomorphism from the syntactic monoid onto the semantic monoid. That is, the syntactic relation of concatenation of symbols maps directly onto the semantic relation of composition of functions."

Isn't that nice?


## Joypy Continuation-Passing Style

In Joypy all the combinators work by modifying the pending expression.  We have enlarged the definition of function to be from a two-tuple of `(stack, expression)` to another such two-tuple:

    F :: (stack, expression) -> (stack, expression)

Simple functions ignore the expression and pass it through unchanged, combinators do not.  They can modify it and this is enough to define control-flow and other operators.

(Actually...  In Joypy the functions all also include a dictionary parameter.  This allows for functions like `print_words` and `help`.  It also allows for the definition of a `define` function which would let Joy code add new definitions to the dictionary during evaluation, but this is an area I am leaving unexplored at least for now.  It is essentially name-binding (variables) sneaking in, breaking the purity of the system.)


## Evaluation

The joy interpreter is a very simple loop.  As long as the expression is non-empty the interpreter pops the next term and checks it, if it's a literal it's pushed onto the stack, if it's a function or combinator the interpreter calls it passing the current stack and expression, which are then replaced by whatever the function or combinator returns.

There is no call stack.  All state is kept either on the stack or in the pending expression.  At each interpreter iteration the stack and expression are complete.  (They can be pickled, saved to disc or sent over the network, and reconstituted at any time, etc...)


# Methods of Meta-programming

Joy seems to lend itself to several complementary forms of meta-programming to develop more-efficient versions of functions.


## Compiling definitions.

Due to the fact that "juxtaposition of symbols is composition of functions" the *simplest* way to "compile" the Joy expression `F G` would be the Python expression:

    lambda s, e, d: G(*F(s, e, d))

This produces a new unnamed function that delivers the output of `F` directly to `G` without passing back through the interpreter loop.

If we wanted to do more work than that, we could inspect the bytecode of the two Python functions, figure out how they name their arguments, and attempt to produce new bytecode that corresponds to the composition of them.  This is a little beyond me at the moment, but it's not unrealistic given enough time and attention.

It will usually be easier to manually write new custom words. For example, the "plus or minus" operator `pm`, defined as:

    pm == [+] [-] cleave popdd

Can be implemented in Python as:

    @SimpleFunctionWrapper
    def pm(stack):
        a, (b, stack) = stack
        p = b + a
        m = b - a
        return m, (p, stack)

Code that uses `pm` will will work the same but more quickly if the "compiled" version is inscribed in the dictionary.

It would be remiss not to mention **Cython** in this connection.  Many Joy functions can be transparently compiled down to machine code.

Beyond the above, it should be possible to make use of much of the existing body of knowledge for compiling *functional programming* languages to machine code for making an actual Joy compiler.  Joy omits many "features" that are common to most other languages, lambda abstraction and `let` statements for example.  I have not had the time to investigate compilation of Joy in any depth so far, but I have high hopes.  It should be possible (and most of the details will have been already worked out in other languages) to go from e.g. the definition form of `pm` to the Python form automatically.


## Partial Evaluation

Cf. "Futamura projections"

["partial evaluation is a technique for several different types of program optimization by specialization. The most straightforward application is to produce new programs which run faster than the originals while being guaranteed to behave in the same way."](https://en.wikipedia.org/wiki/Partial_evaluation) ~Wikipedia

Given a function and some (but not all) of its arguments you can run the interpreter in a speculative fashion and derive new functions that are specializations of the original.

Example from [Futamura, 1983](https://repository.kulib.kyoto-u.ac.jp/dspace/bitstream/2433/103401/1/0482-14.pdf) of converting a power function to a "to the fifth power" function:

    F(k, u) -> u^k

I like to use a kind of crude [Gentzen notation](https://en.wikipedia.org/wiki/Natural_deduction) to describe a Joy function's semantics:

       k u F
    -----------
        u^k

Joy function implementation:

    F == 1 [popop 0 !=] [[popop 2 %] [over *] [] ifte [1 >>] dipd [sqr] dip] while [popop] dip

This is a bit longer than a definition should be.  In practice I would refactor it to be more concise and easily understood.

In Python for comparison:

    def power(k, u):
        z = 1
        while k != 0:
            if k % 2:
                z = z * u
            k = k >> 1
            u = u * u
        return z

Using 5 for `k` and pushing evaluation forward as far as it will go with a sort of "thunk" variable for `u` we arrive at:

    u u u * dup * *

We can replace the extra occurrences of `u` with `dup` to arrive at a definition for a Joy function that, given a number on the stack, returns that number raised to the fifth power:

    to-the-fifth == dup dup * dup * *

Here it is in action:

    u dup dup * dup * *
    u u   dup * dup * *
    u u u     * dup * *
    u u^2       dup * *
    u u^2 u^2       * *
    u u^4             *
    u^5

See the appendix below for the derivation of the specialized form from the general form.

It should be possible to write a program `FutamuraI` that works like this:

        [5] [F] FutamuraI
    -------------------------
       [dup dup * dup * *]


That is, given the quoted program `[F]` and the argument `5`, it returns the new `to-the-fifth` function in quoted form.


### First Futamura Projection

A joy interpreter written in Joy is described in the literature (available from the La Trobe archive or the mirror site) so we can apply the program `FutamuraI` to that to get a *residual* program `R` for some program `Q`:

       [Q] [joy] FutamuraI
    -------------------------
              [R]

The expected result is that, for a given input, the runtime of `R` is less than or equal to the runtime of `Q`.

If we had a partial evaluator for Python we could create a residual program in Python for the Joy program `Q`.


### Second Futamura Projection

       [joy] [FutamuraI] FutamuraI
    ---------------------------------
                [C]

Making a compiler by "specializing the specializer for the interpreter".


### Third Futamura Projection

       [FutamuraI] [FutamuraI] FutamuraI
    ---------------------------------------
                     [K]

"Specializing the specializer for itself yielding a tool that can convert any interpreter to an equivalent compiler"

       [joy] K
    -------------
         [C]



       [Q] [joy] K i 
    -------------------
           [Q] C
        -----------
            [R]




    [K] K -> [K]




## Super-Compilation

https://en.wikipedia.org/wiki/Metacompilation

https://themonadreader.files.wordpress.com/2014/04/super-final.pdf

This is a little hard to describe succinctly, but you are basically trying to figure out all possible paths through a program and then use that knowledge to improve the code, somehow.  (I forget the details, but it's worth including and revisiting.)


## Gödel Machine

http://people.idsia.ch/~juergen/goedelmachine.html

https://en.wikipedia.org/wiki/G%C3%B6del_machine

In Joy it often happens that a new general form is discovered that is semantically equivalent to some other form but that has greater efficiency (at least under some definite conditions.)  When this happens we can perform a kind of search-and-replace operation over the whole of the current dictionary (standard library in other languages) and achieve performance gains.

As an example, the function `[1 >>] dipd [sqr] dip` can be rewritten as `[[1 >>] dip sqr] dip` which, depending on the other optimizations some interpreter might make, could be more efficient.  We can generalize this to a pattern-matching rule, something like:

    [F] dipd [G] dip == [[F] dip G] dip

And we are justified rewriting any occurrence of the pattern on either side to the other if it improves things.

The above also suggests a new combinator, call it `dipdip` that abstracts the pattern:

       ... a b [F] [G] dipdip
    ----------------------------
           ... F a G b

This permits the compiler to make optimizations without having to work to notice the pattern.  The `dipdip` function and the interpreter can work together to do the more efficient thing.

Joy function definitions form Directed Graphs.  Not acyclical though, definition bodies do not contain references to other functions, but rather "Symbols" that name functions, so you can form e.g. two definitions that each make use of the other.  Generally speaking though, you don't do this, instead you write definitions that use e.g. `genrec` general recursion combinator. 

Anyway, because Joy code is just a graph it becomes pretty easy to rewrite the graph in ways that preserve the semantics but are more efficient.  Doing this in an automated fashion is essentially Schmidhuber's Gödel Machine:  Finding and applying provably-correct modifications to the whole system in a self-referential way to create a self-improving general problem solver.

Joy is intended as an effective vehicle for exploring this potential.


## Speculative pre-evaluation

If you examine the traces of Joy programs it's easy to find places in the pending expression where some speculative interpreter could pre-compute results while the main interpreter was prosecuting the main "thread" of the program.  For example consider (with the `.` indicating the current "location of the interpreter head" if you will, the split between the stack and the expression):

    ... a b c . F 2 3 + G H

The `2 3 +` between `F` and `G` is not at the interpreter "head" yet it is extremely unlikely that any function `F` will prevent it (eventually) being evaluated to `5`.  We can imagine an interpreter that detects this sort of thing, evaluates the sub-expression with a different CPU, and "tags" the expression at `2` with the result `5`.  If evaluation reaches `2` the interpreter can just use `5` without re-evaluating the whole sub-expression `2 3 +`.

This sort of thing happens all the time in Joy code.

For example, if you look at the appendix for the partial evaluation example there is a stage where we have this:

    5 u u [1 >>] dipd [sqr] dip

Which can be written with the `dipdip` combinator:

    5 u u [1 >>] [sqr] dipdip

Which then becomes this:

    5 1 >> u sqr u

The interpreter could notice that `5 1 >>` and `u sqr` can proceed in parallel without interfering with each other.  The `dipdip` combinator could be written to somehow hint to the interpreter that it should check for this posibility.


## JIT

Whatever eventually winds up converting Joy code to machine code is susceptible to Just-in-Time compilation.  For example, if you run Joypy on Pypy you take advantage of its JIT.


# Joy as UI


## Joy unifies CLI and GUI interfaces.

All Joy interaction consists of two basic actions:

1. Putting things onto the stack.
2. Executing functions.

In a command-line setting you perform both of these actions the same way: entering Joy expressions as text.  In a GUI you select items and copy or cut them to a user-visible stack (that is a first-class member of the UI, similar to the clipboard but with better visibility into contents and not restricted to one selection at a time.)  You then trigger the evaluation of functions by clicking on buttons or menu items.  *From the point-of-view of the underlying interpreter there is no difference between the input token streams for either UI modality.*


## Simple and Comprehensible Model

In order to use their system(s) users must be able to easily and quickly develop a mental model of the system that maps to the actual system abstractions well enough to support the achievement of their goals.

(Arguably current systems are pretty poor at this.  Even an abstraction as old and ubiquitous as "filesystem" is only incompletely understood by many computer users.  Many people do not understand the difference between RAM and disk storage!)

The Joy model consists of just these main concepts:

1. A stack of values
2. A dictionary of named commands
3. An interpreter

Each of these is very simple and the first two even have real-world analogs (e.g. a *stack* of dishes or boxes or whatever, and, well, *dictionaries*.)  It's easy to develop intuition for this system, resulting in a close match between the user's mental model and the actual system abstraction.


# Joy as AST for multi-language interop

IR for Compilation

Cf. Graal & Truffle

"Software is eating the world"; Joy eats software.

Universal Solvent

Can write front-ends for translating other languages into Joy, thence to be refactored and fulminated into more efficient forms.  "The Blob" of software.


# Minimal Basis

Cf. SKI combinators, Peano arithmentic, Church numerals et. al.,

Folks have done work on figuring out the minimal set of combinators that are Turing-complete.  Several of these sets are quite small.

Semantics can be defined in terms of Laws of Form for down-to-the-metal modeling of programs as logic circuits.  Hardware description language.



# Math, Physics, Computation

    Computational algorithms are used to communicate precisely
    some of the methods used in the analysis of dynamical phenomena.
    Expressing the methods of variational mechanics in a computer
    language forces them to be unambiguous and computationally
    effective. Computation requires us to be precise about the repre-
    sentation of mechanical and geometric notions as computational
    objects and permits us to represent explicitly the algorithms for
    manipulating these objects. Also, once formalized as a procedure,
    a mathematical idea becomes a tool that can be used directly to
    compute results.
       - "Structure and Interpretation of Classical Mechanics",
       Gerald Jay Sussman and Jack Wisdom with Meinhard E. Mayer

.



# Joy as glue language

Basically any existing code/programs can be exposed to Joy as a function or collection of functions.

## Shell command

Run a shell command.

        "stdin" "cmd line" system
    -----------------------------------
       "stderr" "stdout" return_code

Then you can create e.g.:

    foo == "awk {awk program}" system

Etc...

## Python libraries

## Ctypes (FFI) for loading binary libraries




# Git as File Store

The old-fashioned File System abstraction is no longer justified.  Joypy won't attempt to implement file and path operations.  Instead there are a few functions that accept three args: a sha1 checksum of a blob of data, an initial index, and an offset.  One function returns the string of data `blob[index:index+offset]`, while another accepts an additional quoted program and "runs it" with the data as the stack, for when you want to process a big ol' pile of data but don't want to load it into the interpreter.  I imagine a use case for a third-party wrapped library that expects some sort of file or socket and streams over it somehow.  Obviously, this is under-specified.

The sha1 checksum refers to data stored in some (global, universal) git repo, which is provided to the interpreter though some as-yet unimplemented meta-interpreter action.

**Git is a functional data type**, compatible with the semantic model of Joy.  Implies shared datastore with obvious connection to git-archive & Datalad.

Functions over static data (Wikipedia dump; MRI data &c.) can be considered timeless (however much time their first evaluation takes) and cached/archived in the global shared git repo.  (Large data in e.g. cloud & bittorrent, with meta-data in git-archive/Datalad)

Functions over streams (of possible mal-formed) data require a special stream-processing combinator and more care in their development.  I haven't developed this in any detail, but it can be shown in many cases that e.g. a given function cannot grow unbounded (for all possible unbounded input streams.)



# Sympy Library

The mathematical functions in the Joypy library wrap the `math` module and other built-ins for the most part.  It would be a simple matter to write wrapper functions for e.g. the Sympy packages' functions and provide symbolic math capabilities.

It would also be possible to make a dictionary that mapped the math functions to the Sympy versions.  Evaluating Joy code with this dictionary (and a special stack with Sympy variables on it) would result in symbolic execution without rewriting the Joy code.



# Stack-based laguages as Dataflow

If the "places" in a stack are considered first-class entities and tracked through "stack chatter" operations (like `swap`) we can draw flow-lines for the data and represent the functions as boxes with input and output lines.  Stack chatter becomes topological rearrangements of lines.  The resulting structure is conceptually identical with *Dataflow* paradigm of programming.

(Related to this I suspect that all stack chatter disappears during compilation but I haven't nailed that down yet.)

I'm unable to find the original webpage that describe the above.  :-(


# Appendix Partial Evaluation Example

       k u F
    -----------
        u^k


    k u 1 [popop 0 !=] [[popop odd][over *][]ifte [1 >>] dipd [sqr] dip] while [popop] dip

    F == 1 [popop 0 !=] [[popop odd][over *][]ifte [1 >>] dipd [sqr] dip] while [popop] dip

    5 u 1 [popop 0 !=] [[popop odd][over *][]ifte [1 >>] dipd [sqr] dip] while [popop] dip


    5 u 1 popop 0 !=
    5           0 !=
    True


    5 u 1 [popop odd][over *][]ifte [1 >>] dipd [sqr] dip
    5 u 1 popop odd
    True

    w/ sqr == dup *

    5 u 1 over * [1 >>] dipd [sqr] dip
    5 u 1 u    * [1 >>] dipd [sqr] dip
    5 u u        [1 >>] dipd [sqr] dip
    5 1 >> u sqr u
    2      u_dup_*   u
          --or--
    2      u_u_*   u

    2 u_u_* u popop 0 !=
    2               0 !=
    True
    
    2 u_u_* u [popop odd][over *][]ifte [1 >>] dipd [sqr] dip
    ...
    2 u_u_* u                           [1 >>] dipd [sqr] dip

    2 1 >> u_u_* sqr   u
    1      u_u_*_dup_* u


    1 u_u_*_dup_* u [popop odd][over *][]ifte [1 >>] dipd [sqr] dip
    1 u_u_*_dup_* u             over *        [1 >>] dipd [sqr] dip
    1 u_u_*_dup_* u u_u_*_dup_*      *        [1 >>] dipd [sqr] dip
    1 u_u_*_dup_* u_u_u_*_dup_*_*             [1 >>] dipd [sqr] dip

    1 1 >> u_u_*_dup_* sqr           u_u_u_*_dup_*_*
    0      u_u_*_dup_* dup *         u_u_u_*_dup_*_*
    0      u_u_*_dup_* u_u_*_dup_* * u_u_u_*_dup_*_*
    0      u_..._*                   u_u_u_*_dup_*_*

    0      u_..._*                   u_u_u_*_dup_*_* [popop] dip

    u_u_u_*_dup_*_*
    
    ^5 == dup dup * dup * *
