# Some Jupyter Notebooks and other material.

All of the notebooks are also available as HTML and Markdown files (generated using nbconvert) so you can view them without running Jupyter.

In order to run the [Jupyter Notebooks](https://jupyter.org/index.html) you need Jupyter (obviously) and you should install `Joypy`.  Here's an example using `virtualenv` from the `joypy/` directory:

    virtualenv --system-site-packages <DIRNAME>
    . ./<DIRNAME>/bin/activate
    python ./setup.py install

Once that's done you should be able to start Jupyter Notebook server with, e.g.:

    python -n notebook

This starts it using the `virtualenv` version of Python so `joy` will be available.  Navigate to the `joypy/docs` directory and the notebooks should be able to import the `notebook_preamble.py` file.

## Table of Contents

- 1. Basic Use of Joy in a Notebook
- 2. Library Examples - Short examples of each word in the dictionary.  Various formats.
- 3. Developing a Program - Working with the first problem from Project Euler, "Find the sum of all the multiples of 3 or 5 below 1000", several forms of the program are derived.
- 4. Replacing Functions in the Dictionary - Shows the basics of defining new "primitive" functions in Python or as definitions and adding them to the dictionary.
- Factorial Function and Paramorphisms - A basic pattern of recursive control-flow.
- Generator Programs - Using the x combinator to make generator programs which can be used to create unbounded streams of values.
- Hylo-, Ana-, Cata-morphisms - Some basic patterns of recursive control-flow structures.
- Quadratic - Not-so-annoying Quadratic Formula.
- Trees - Ordered Binary Trees in Joy and more recursion.
- Zipper - A preliminary examination of the idea of data-structure "zippers" for traversing datastructures.
- notebook_preamble.py - Imported into notebooks to simplify the preamble code.
- pe1.py pe1.txt - Set up and execute a Joy program for the first problem from Project Euler. The pe1.txt file is the trace.  It's 2.8M uncompressed.  Compressed with gzip it becomes just 0.12M.
- repl.py - Run this script to start a REPL.  Useful for e.g. running Joy code in a debugger.

## Notes

One of the things that interests me about Joy is how programming becomes
less about writing code and more about sound reasoning about simple
(almost geometric) programs.  Many of the notebooks in this collection
consist of several pages of discussion to arrive at a few lines of Joy
definitions.  I think this is a good thing.  This is "literate
programming".  The "programs" resemble mathematical proofs.  You aren't
implementing so much as deriving.  The structure of Joy seems to force
you to think clearly about the task in a way that is reliable but
extremely flexible.  It feels like a puzzle game, and the puzzles are
often simple, and the solutions build on each other.
