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
'''


A Graphical User Interface for a dialect of Joy in Python.


The GUI

  History
  Structure
  Commands
    Mouse Chords
    Keyboard
  Output from Joy


'''
from __future__ import print_function
try:
  import tkinter as tk
  from tkinter.font import families, Font
except ImportError:
  import Tkinter as tk
  from tkFont import families, Font

from re import compile as regular_expression
from traceback import format_exc
import sys
import os

from .misc import FileFaker, is_numerical
from .mousebindings import MouseBindingsMixin
from .world import World


def make_gui():
  t = TextViewerWidget(World())
  t['font'] = get_font()
  t._root().title('Joy')
  t.pack(expand=True, fill=tk.BOTH)
  return t


def get_font(family='EB Garamond', size=14):
  if family not in families():
    family = 'Times'
  return Font(family=family, size=size)


def main():
  t = make_gui()
  sys.stdout = FileFaker(t)
  return t


#: Define mapping between Tkinter events and functions or methods. The
#: keys are string Tk "event sequences" and the values are callables that
#: get passed the TextViewer instance (so you can bind to methods) and
#: must return the actual callable to which to bind the event sequence.
text_bindings = {

  #I want to ensure that these keyboard shortcuts work.
  '<Control-v>': lambda tv: tv._paste,
  '<Control-V>': lambda tv: tv._paste,
  '<Shift-Insert>': lambda tv: tv._paste,

  }


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
    self['state'] = tk.DISABLED
    try:
      return self.get('0.0', tk.END)[:-1]
    finally:
      self['state'] = tk.NORMAL

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


class TextViewerWidget(tk.Text, MouseBindingsMixin, SavingMixin):
  """
  This class is a Tkinter Text with special mousebindings to make
  it act as a Xerblin Text Viewer.
  """

  #This is a regular expression for finding commands in the text.
  command_re = regular_expression(r'[-a-zA-Z0-9_\\~/.:!@#$%&*?=+<>]+')

  #These are the config tags for command text when it's highlighted.
  command_tags = dict(
    underline = 1,
    bgstipple = "gray50",
    borderwidth = "1",
    foreground = "orange"
  )

  def __init__(self, world, master=None,  **kw):

    self.world = world
    if self.world.text_widget is None:
      self.world.text_widget = self

    #Turn on undo, but don't override a passed-in setting.
    kw.setdefault('undo', True)

#        kw.setdefault('bg', 'white')
    kw.setdefault('wrap', 'word')
    kw.setdefault('font', 'arial 12')

    #Create ourselves as a Tkinter Text
    tk.Text.__init__(self, master, **kw)

    #Initialize our mouse mixin.
    MouseBindingsMixin.__init__(self)

    #Initialize our saver mixin.
    SavingMixin.__init__(self)

    #Add tag config for command highlighting.
    self.tag_config('command', **self.command_tags)

    #Create us a command instance variable
    self.command = ''

    #Activate event bindings. Modify text_bindings in your config
    #file to affect the key bindings and whatnot here.
    for event_sequence, callback_finder in text_bindings.items():
      callback = callback_finder(self)
      self.bind(event_sequence, callback)

##        T.protocol("WM_DELETE_WINDOW", self.on_close)

  def find_command_in_line(self, line, index):
    '''
    Return the command at index in line and its begin and end indices.
    find_command_in_line(line, index) => command, begin, end
    '''
    for match in self.command_re.finditer(line):
      b, e = match.span()
      if b <= index <= e:
        return match.group(), b, e

  def paste_X_selection_to_mouse_pointer(self, event):
    '''Paste the X selection to the mouse pointer.'''
    try:
      text = self.selection_get()
    except tk.TclError:
      return 'break'
    self.insert_it(text)

  def update_command_word(self, event):
    '''Highlight the command under the mouse.'''
    self.unhighlight_command()
    self.command = ''
    index = '@%d,%d' % (event.x, event.y)
    linestart = self.index(index + 'linestart')
    lineend = self.index(index + 'lineend')
    line = self.get(linestart, lineend)
    row, offset = self._get_index(index)

    if offset >= len(line) or line[offset].isspace():
      # The mouse is off the end of the line or on a space so there's no
      # command, we're done.
      return

    cmd = self.find_command_in_line(line, offset)
    if cmd is None:
      return

    cmd, b, e = cmd
    if self.world.has(cmd) or is_numerical(cmd):
      self.command = cmd
      self.highlight_command(
        '%d.%d' % (row, b),
        '%d.%d' % (row, e),
        )

  def highlight_command(self, from_, to):
    '''Apply command style from from_ to to.'''
    cmdstart = self.index(from_)
    cmdend = self.index(to)
    self.tag_add('command', cmdstart, cmdend)

  def do_command(self, event):
    '''Do the currently highlighted command.'''
    self.unhighlight_command()
    if self.command:
      self.run_command(self.command)

  def run_command(self, command):
    '''Given a string run it on the stack, report errors.'''
    try:
      self.world.interpret(command)
    except SystemExit:
      raise
    except:
      self.popupTB(format_exc().rstrip())

  def unhighlight_command(self):
    '''Remove any command highlighting.'''
    self.tag_remove('command', 1.0, tk.END)

  def set_insertion_point(self, event):
    '''Set the insertion cursor to the current mouse location.'''
    self.focus()
    self.mark_set(tk.INSERT, '@%d,%d' % (event.x, event.y))

  def cut(self, event):
    '''Cut selection to stack.'''
    select_indices = self.tag_ranges(tk.SEL)
    if select_indices:
      s = self.get(select_indices[0], select_indices[1])
      self.world.push(s)
      # Let the pre-existing machinery take care of cutting the selection.
      self.event_generate("<<Cut>>")

  def copyto(self, event):
    '''Actually "paste" from TOS'''
    try:
      s = self.world.peek()
    except IndexError:
      return
    self.insert_it(s)

  def insert_it(self, s):
    if not isinstance(s, str):
      s = str(s)

    # When pasting from the mouse we have to remove the current selection
    # to prevent destroying it by the paste operation.
    select_indices = self.tag_ranges(tk.SEL)
    if select_indices:
      # Set two marks to remember the selection.
      self.mark_set('_sel_start', select_indices[0])
      self.mark_set('_sel_end', select_indices[1])
      self.tag_remove(tk.SEL, 1.0, tk.END)

    self.insert(tk.INSERT, s)

    if select_indices:
      self.tag_add(tk.SEL, '_sel_start', '_sel_end')
      self.mark_unset('_sel_start')
      self.mark_unset('_sel_end')

  def run_selection(self, event):
    '''Run the current selection if any on the stack.'''
    select_indices = self.tag_ranges(tk.SEL)
    if select_indices:
      selection = self.get(select_indices[0], select_indices[1])
      self.tag_remove(tk.SEL, 1.0, tk.END)
      self.run_command(selection)

  def pastecut(self, event):
    '''Cut the TOS item to the mouse.'''
    self.copyto(event)
    self.world.pop()

  def opendoc(self, event):
    '''OpenDoc the current command.'''
    if self.command:
      self.world.do_opendoc(self.command)

  def lookup(self, event):
    '''Look up the current command.'''
    if self.command:
      self.world.do_lookup(self.command)

  def cancel(self, event):
    '''Cancel whatever we're doing.'''
    self.leave(None)
    self.tag_remove(tk.SEL, 1.0, tk.END)
    self._sel_anchor = '0.0'
    self.mark_unset(tk.INSERT)

  def leave(self, event):
    '''Called when mouse leaves the Text window.'''
    self.unhighlight_command()
    self.command = ''

  def _get_index(self, index):
    '''Get the index in (int, int) form of index.'''
    return tuple(map(int, self.index(index).split('.')))

  def _paste(self, event):
    '''Paste the system selection to the current selection, replacing it.'''

    # If we're "key" pasting, we have to move the insertion point
    # to the selection so the pasted text gets inserted at the
    # location of the deleted selection.

    select_indices = self.tag_ranges(tk.SEL)
    if select_indices:
      # Mark the location of the current insertion cursor 
      self.mark_set('tmark', tk.INSERT)
      # Put the insertion cursor at the selection
      self.mark_set(tk.INSERT, select_indices[1])

    # Paste to the current selection, or if none, to the insertion cursor.
    self.event_generate("<<Paste>>")

    # If we mess with the insertion cursor above, fix it now.
    if select_indices:
      # Put the insertion cursor back where it was.
      self.mark_set(tk.INSERT, 'tmark')
      # And get rid of our unneeded mark.
      self.mark_unset('tmark')

    return 'break'

  def popupTB(self, tb):
    top = tk.Toplevel()
    T = TextViewerWidget(
      self.world,
      top,
      width=max(len(s) for s in tb.splitlines()) + 3,
      )

    T['background'] = 'darkgrey'
    T['foreground'] = 'darkblue'
    T.tag_config('err', foreground='yellow')

    T.insert(tk.END, tb)
    last_line = str(int(T.index(tk.END).split('.')[0]) - 1) + '.0'
    T.tag_add('err', last_line, tk.END)
    T['state'] = tk.DISABLED

    top.title(T.get(last_line, tk.END).strip())

    T.pack(expand=1, fill=tk.BOTH)
    T.see(tk.END)
