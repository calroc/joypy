# -*- coding: utf-8 -*-
#
#    Copyright © 2017 Simon Forman
#
#    This file is part of Joypy
#
#    Joypy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Joypy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Joypy.  If not see <http://www.gnu.org/licenses/>.
#
from traceback import print_exc, format_exc
from joy.joy import run
from joy.library import initialize, DefinitionWrapper
from joy.utils.stack import stack_to_string
from joy.utils.pretty_print import TracePrinter


D = initialize()
S = ()


def J(text, stack=S, dictionary=D):
    print stack_to_string(run(text, stack, dictionary)[0])


def V(text, stack=S, dictionary=D):
    tp = TracePrinter()
    try:
        run(text, stack, dictionary, tp.viewer)
    except:
        exc = format_exc()
        tp.print_()
        print '-' * 73
        print exc
    else:
        tp.print_()


define = lambda text: DefinitionWrapper.add_def(text, D)
