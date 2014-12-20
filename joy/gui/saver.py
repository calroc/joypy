# -*- coding: utf-8 -*-
#
#    Copyright © 2014, 2015 Simon Forman
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
import os


class SavingMixin:

  def __init__(self, saver=None, filename=None, save_delay=2000):
    self.saver = self._saver if saver is None else saver
    self.filename = filename
    self._save_delay = save_delay
    self.tk.call(self._w, 'edit', 'modified', 0)
    self.bind('<<Modified>>', self._beenModified)
    self._resetting_modified_flag = False
    self._save = None

  def save(self):
    '''
    Call _saveFunc() after a certain amount of idle time.

    Called by _beenModified().
    '''
    self._cancelSave()
    if self.saver:
      self._saveAfter(self._save_delay)

  def _saveAfter(self, delay):
    '''
    Trigger a cancel-able call to _saveFunc() after delay milliseconds.
    '''
    self._save = self.after(delay, self._saveFunc)

  def _saveFunc(self):
    self._save = None
    self.saver(self._get_contents())

  def _saver(self, text):
    if not self.filename:
      return
    with open(self.filename, 'w') as f:
      f.write(text)
      f.flush()
      os.fsync(f.fileno())
    self.world.save()

  def _cancelSave(self):
    if self._save is not None:
      self.after_cancel(self._save)
      self._save = None

  def _get_contents(self):
    self['state'] = 'disabled'
    try:
      return self.get('0.0', 'end')[:-1]
    finally:
      self['state'] = 'normal'

  def _beenModified(self, event):
    if self._resetting_modified_flag:
      return
    self._clearModifiedFlag()
    self.save()

  def _clearModifiedFlag(self):
    self._resetting_modified_flag = True
    try:
      self.tk.call(self._w, 'edit', 'modified', 0)
    finally:
      self._resetting_modified_flag = False

##        tags = self._saveTags()
##        chunks = self.DUMP()
##        print chunks
