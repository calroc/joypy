#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright © 2014, 2015, 2017 Simon Forman
#
#    This file is part of joy.py
#
#    joy.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    joy.py is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with joy.py.  If not see <http://www.gnu.org/licenses/>.
#
from joy.library import initialize
from joy.joy import repl
from joy.library import DefinitionWrapper


D = initialize()


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



DefinitionWrapper.add_definitions('''






     TS0 == [not] swap unit [pop] swoncat
     TS1 == [dip] cons [uncons] swoncat
treestep == swap [map] swoncat [TS1 [TS0] dip] dip genrec

Q == [tuck / + 2 /] unary
eps == [sqr - abs] nullary
K == [<] [popop swap pop] [popd [Q eps] dip] primrec



get_value == [roll< at] nullary
incr_value == [[popd incr_at] unary] dip
add_value == [+] cons dipd
incr_step_count == [++] dip

F == [popop 5 >=] [roll< popop] [get_value incr_value add_value incr_step_count] primrec

G == [first % not] [first /] [rest [not] [popop 0]] [ifte] genrec

''', D)


print '''\
Joypy - Copyright © 2017 Simon Forman
This program comes with ABSOLUTELY NO WARRANTY; for details type "warranty".
This is free software, and you are welcome to redistribute it
under certain conditions; type "sharing" for details.
Type "words" to see a list of all words, and "[<name>] help" to print the
docs for a word.
'''
stack = repl(dictionary=D)

