#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''


A Graphical User Interface for a dialect of Joy in Python.


    Copyright © 2014 Simon Forman

    This file is gui.py

    gui.py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    gui.py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with gui.py.  If not see <http://www.gnu.org/licenses/>.


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
from inspect import getdoc
import os

from functions import FUNCTIONS
from stack import strstack
from .joy import joy, run
import tracer


class WorldWrapper:

  def __init__(self, stack=(), text_widget=None):
    self.stack = stack
    self.text_widget = text_widget

  def do_lookup(self, name):
    word = FUNCTIONS[name]
    self.stack = word, self.stack
    self.print_stack()

  def do_opendoc(self, name):
    if isNumerical(name):
      print('The number', name)
    else:
      try:
        word = FUNCTIONS[name]
      except KeyError:
        print(repr(name), '???')
      else:
        print(getdoc(word))
    self.text_widget.see(tk.END)

  def pop(self):
    if self.stack:
      self.stack = self.stack[1]
    self.print_stack()

  def push(self, it):
    it = it.encode('utf8')
    self.stack = it, self.stack
    self.print_stack()

  def peek(self):
    if self.stack:
      return self.stack[0]

  def interpret(self, command):
    if tracer.TRACE: joy.reset()
    self.stack = run(command, self.stack)
    self.print_stack()
    if tracer.TRACE: joy.show_trace()

  def has(self, name):
    return name in FUNCTIONS

  def save(self):
    pass

  def print_stack(self):
    stack_out_index = self.text_widget.search('<' 'STACK', 1.0)
    if stack_out_index:
      self.text_widget.see(stack_out_index)
      s = strstack(self.stack) + '\n'
      self.text_widget.insert(stack_out_index, s)


#Do-nothing event handler.
nothing = lambda event: None


class mousebindingsmixin:
  """TextViewerWidget mixin class to provide mouse bindings."""

  def __init__(self):

    #Remember our mouse button state
    self.B1_DOWN = False
    self.B2_DOWN = False
    self.B3_DOWN = False

    #Remember our pending action.
    self.dothis = nothing

    #We'll need to remember whether or not we've been moving B2.
    self.beenMovingB2 = False

    #Unbind the events we're interested in.
    for sequence in (
      "<Button-1>", "<B1-Motion>", "<ButtonRelease-1>",
      "<Button-2>", "<B2-Motion>", "<ButtonRelease-2>",
      "<Button-3>", "<B3-Motion>", "<ButtonRelease-3>",
      "<B1-Leave>", "<B2-Leave>", "<B3-Leave>", "<Any-Leave>", "<Leave>"
      ):
      self.unbind(sequence)
      self.unbind_all(sequence)

    self.event_delete('<<PasteSelection>>') #I forgot what this was for! :-P  D'oh!

    #Bind our event handlers to their events.
    self.bind("<Button-1>", self.B1d)
    self.bind("<B1-Motion>", self.B1m)
    self.bind("<ButtonRelease-1>", self.B1r)

    self.bind("<Button-2>", self.B2d)
    self.bind("<B2-Motion>", self.B2m)
    self.bind("<ButtonRelease-2>", self.B2r)

    self.bind("<Button-3>", self.B3d)
    self.bind("<B3-Motion>", self.B3m)
    self.bind("<ButtonRelease-3>", self.B3r)

    self.bind("<Any-Leave>", self.leave)

  def B1d(self, event):
    '''button one pressed'''
    self.B1_DOWN = True

    if self.B2_DOWN:

      self.unhighlight_command()

      if self.B3_DOWN :
        self.dothis = self.cancel

      else:
        #copy TOS to the mouse (instead of system selection.)
        self.dothis = self.copyto #middle-left-interclick

    elif self.B3_DOWN :
      self.unhighlight_command()
      self.dothis = self.opendoc #right-left-interclick

    else:
      ##button 1 down, set insertion and begin selection.
      ##Actually, do nothing. Tk Text widget defaults take care of it.
      self.dothis = nothing
      return

    #Prevent further event handling by returning "break".
    return "break"

  def B2d(self, event):
    '''button two pressed'''
    self.B2_DOWN = 1

    if self.B1_DOWN :

      if self.B3_DOWN :
        self.dothis = self.cancel

      else:
        #left-middle-interclick - cut selection to stack
        self.dothis = self.cut

    elif self.B3_DOWN :
      self.unhighlight_command()
      self.dothis = self.lookup #right-middle-interclick - lookup

    else:
      #middle-click - paste X selection to mouse pointer
      self.set_insertion_point(event)
      self.dothis = self.paste_X_selection_to_mouse_pointer
      return

    return "break"

  def B3d(self, event):
    '''button three pressed'''
    self.B3_DOWN = 1

    if self.B1_DOWN :

      if self.B2_DOWN :
        self.dothis = self.cancel

      else:
        #left-right-interclick - copy selection to stack
        self.dothis = self.run_selection

    elif self.B2_DOWN :
      #middle-right-interclick - Pop/Cut from TOS to insertion cursor
      self.unhighlight_command()
      self.dothis = self.pastecut

    else:
      #right-click
      self.CommandFirstDown(event)

    return "break"

  def B1m(self, event):
    '''button one moved'''
    if self.B2_DOWN or self.B3_DOWN:
      return "break"

  def B2m(self, event):
    '''button two moved'''
    if self.dothis == self.paste_X_selection_to_mouse_pointer and \
       not (self.B1_DOWN or self.B3_DOWN):

      self.beenMovingB2 = True
      return

    return "break"

  def B3m(self, event):
    '''button three moved'''
    if self.dothis == self.do_command and \
       not (self.B1_DOWN or self.B2_DOWN):

      self.update_command_word(event)

    return "break"

  def B1r(self, event):
    '''button one released'''
    self.B1_DOWN = False

    if not (self.B2_DOWN or self.B3_DOWN):
      self.dothis(event)

    return "break"

  def B2r(self, event):
    '''button two released'''
    self.B2_DOWN = False

    if not (self.B1_DOWN or self.B3_DOWN or self.beenMovingB2):
      self.dothis(event)

    self.beenMovingB2 = False

    return "break"

  def B3r(self, event):
    '''button three released'''
    self.B3_DOWN = False

    if not (self.B1_DOWN or self.B2_DOWN) :
      self.dothis(event)

    return "break"

  def InsertFirstDown(self, event):
    self.focus()
    self.dothis = nothing
    self.set_insertion_point(event)

  def CommandFirstDown(self, event):
    self.dothis = self.do_command
    self.update_command_word(event)


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


class TextViewerWidget(tk.Text, mousebindingsmixin):
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

    # Get the filename associated with this widget's contents, if any.
    self.filename = kw.pop('filename', False)

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
    mousebindingsmixin.__init__(self)

    #Add tag config for command highlighting.
    self.tag_config('command', **self.command_tags)

    #Create us a command instance variable
    self.command = ''

    #Activate event bindings. Modify text_bindings in your config
    #file to affect the key bindings and whatnot here.
    for event_sequence, callback_finder in text_bindings.items():
      callback = callback_finder(self)
      self.bind(event_sequence, callback)

    self.tk.call(self._w, 'edit', 'modified', 0)
    self.bind('<<Modified>>', self._beenModified)
    self._resetting_modified_flag = False

##        T.protocol("WM_DELETE_WINDOW", self.on_close)

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

  _saveDelay = 2000

  def save(self):
    '''
    Call _saveFunc() after a certain amount of idle time.

    Called by _beenModified().
    '''
    self._cancelSave()
    self._saveAfter(self._saveDelay)

  def _saveFunc(self):
    self._save = None
    if not self.filename:
      return
    self['state'] = tk.DISABLED
    try:
      text = self.get_contents()
      with open(self.filename, 'w') as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
      self.world.save()
    finally:
      self['state'] = tk.NORMAL

##        tags = self._saveTags()
##        chunks = self.DUMP()
##        print chunks

  def _saveAfter(self, delay):
    '''
    Trigger a cancel-able call to _saveFunc() after delay milliseconds.
    '''
    self._save = self.after(delay, self._saveFunc)

  def _cancelSave(self):
    try:
      save = self._save
    except AttributeError:
      pass
    else:
      if save:
        self.after_cancel(save)
        save = None

  def get_contents(self):
    return self.get('0.0', tk.END)[:-1]

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
    if self.world.has(cmd) or isNumerical(cmd):
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


def make_gui():
  t = TextViewerWidget(WorldWrapper())
  t['font'] = get_font()
  t._root().title('Joy')
  t.pack(expand=True, fill=tk.BOTH)
  return t


class FileFaker(object):
  def __init__(self, T):
    self.T = T
  def write(self, text):
    self.T.insert(tk.END, text)
  def flush(self):
    pass


def isNumerical(s):
  try:
    float(s)
  except ValueError:
    return False
  return True


def get_font(family='EB Garamond', size=14):
  if family not in families():
    family = 'Times'
  return Font(family=family, size=size)


def main():
  import sys
  t = make_gui()
  sys.stdout = FileFaker(t)
  return t
