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
from distutils.core import setup
from textwrap import dedent


setup(
  name='Joypy',
  version='0.1',
  description='Python Implementation of Joy',
  long_description=dedent('''\
    Joy is a programming language created by Manfred von Thun that is easy to
    use and understand and has many other nice properties.  This Python
    package implements an interpreter for a dialect of Joy that attempts to
    stay very close to the spirit of Joy but does not precisely match the
    behaviour of the original version written in C.'''),
  author='Simon Forman',
  author_email='forman.simon@gmail.com',
  url='https://github.com/calroc/joypy',
  packages=['joy', 'joy.utils'],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 2.7',
    ],
  )
