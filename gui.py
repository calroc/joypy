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
  from tkinter import (
    Text,
    Toplevel,
    TclError,
    END,
    INSERT,
    SEL,
    DISABLED,
    NORMAL,
    BOTH,
    )
  from tkinter.font import families, Font
except ImportError:
  from Tkinter import (
    Text,
    Toplevel,
    TclError,
    END,
    INSERT,
    SEL,
    DISABLED,
    NORMAL,
    BOTH,
    )
  from tkFont import families, Font
from re import compile as regular_expression
from traceback import format_exc
from inspect import getdoc
from joy import run, strstack, FUNCTIONS


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
    self.text_widget.see(END)

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
    self.stack = run(command, self.stack)
    self.print_stack()

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

      self.unset_command()

      if self.B3_DOWN :
        self.dothis = self.cancel

      else:
        #copy TOS to the mouse (instead of system selection.)
        self.dothis = self.copyto #middle-left-interclick

    elif self.B3_DOWN :
      self.unset_command()
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
      self.unset_command()
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
      self.unset_command()
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


class TextViewerWidget(Text, mousebindingsmixin):
  """
  This class is a Tkinter Text with special mousebindings to make
  it act as a Xerblin Text Viewer.
  """

  #This is a regular expression for finding commands in the text.
  command_re = regular_expression(r'[-a-zA-Z0-9_\\~/.:!@#$%&*?=+]+')

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
    Text.__init__(self, master, **kw)

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
    self['state'] = DISABLED
    try:
      text = self.get_contents()
      with open(self.filename, 'w') as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
      self.world.save()
    finally:
      self['state'] = NORMAL

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
    return self.get('0.0', END)[:-1]

  def findCommandInLine(self, line, index):
    '''findCommandInLine(line, index) => command, begin, end
    Return the command at index in line and its begin and end indices.'''

    #Iterate through the possible commands in the line...
    for match in self.command_re.finditer(line):

      #Pull out the indices of the possible command.
      b, e = match.span()

      #If the indices bracket the index return the result.
      if b <= index <= e:
        return match.group(), b, e

  def paste_X_selection_to_mouse_pointer(self, event):
    '''Paste the X selection to the mouse pointer.'''

    #Use the Tkinter method selection_get() to try to get the X selection.
    try:
      text = self.selection_get()

    #TclError gets raised if no current selection.
    except TclError:

      #So just carry on, there's nothing to do.
      return 'break'

    self.insert_it(text)

  def update_command_word(self, event):
    '''Highlight the command under the mouse.'''

    #Get rid of any old command highlighting.
    self.unset_command()

    #Get the index of the mouse.
    index = '@%d,%d' % (event.x, event.y)

    #Find coordinates for the line under the mouse.
    linestart = self.index(index + 'linestart')
    lineend = self.index(index + 'lineend')

    #Get the entire line under the mouse.
    line = self.get(linestart, lineend)

    #Parse out the row and offset of the mouse
    row, offset = self._get_index(index)

    #If the mouse is off the end of the line or on a space..
    if offset >= len(line) or line[offset].isspace():

      #There's no command, we're done.
      self.command = ''
      return

    #Get the command at the offset in the line.
    cmd = self.findCommandInLine(line, offset)

    if cmd and (self.world.has(cmd[0]) or isNumerical(cmd[0])):

      #Set self's command variable and extract the indices of it.
      self.command, b, e = cmd

      #Get the indices relative to the Text.
      cmdstart = self.index('%d.%d' % (row, b))
      cmdend = self.index('%d.%d' % (row, e))

      #Add the command highlighting tags to the command text.
      self.tag_add('command', cmdstart, cmdend)

    #If there was no command, clear our command variable.
    else:
      self.command = ''

  def do_command(self, event):
    '''Do the currently highlighted command.'''

    #Remove any old highlighting.
    self.unset_command()

    #If there is a current command..
    if self.command:

      #Interpret the current command.
      self.run_command(self.command)

  def run_command(self, command):
    '''Given a string run it on the stack, report errors.'''
    try:
      self.world.interpret(command)
    except SystemExit:
      raise
    except:
      self.popupTB(format_exc().rstrip())

  def unset_command(self):
    '''Remove any command highlighting.'''
    self.tag_remove('command', 1.0, END)

  def set_insertion_point(self, event):
    '''Set the insertion cursor to the current mouse location.'''
    self.focus()
    self.mark_set(INSERT, '@%d,%d' % (event.x, event.y))

  def cut(self, event):
    '''Cut selection to stack.'''

    #Get the indices of the current selection if any.
    select_indices = self.tag_ranges(SEL)

    #If there is a current selection..
    if select_indices:

      #Get the text of it.
      s = self.get(select_indices[0], select_indices[1])

      #Append the text to our interpreter's stack.
      self.world.push(s)

      #Let the pre-existing machinery take care of cutting the selection.
      self.event_generate("<<Cut>>")

  def copyto(self, event):
    '''Actually "paste" from TOS'''
    try:
      s = self.world.peek()
    except IndexError:
      return
    self.insert_it(s)

  def insert_it(self, s):

    #Make sure it's a string.
    if not isinstance(s, str):
      s = str(s)

    #When pasting from the mouse we have to remove the current selection
    #to prevent destroying it by the paste operation.

    #Find out if there's a current selection.
    select_indices = self.tag_ranges(SEL)

    #If there's a selection.
    if select_indices:

      #Remember that we have to reset it after pasting.
      reset_selection = True

      #Set two marks to remember the selection.
      self.mark_set('_sel_start', select_indices[0])
      self.mark_set('_sel_end', select_indices[1])

      #Remove the selection.
      self.tag_remove(SEL, 1.0, END)

    #If there's no selection we don't have to reset it
    else:
      reset_selection = False

    #Insert the TOS string.
    self.insert(INSERT, s)

    #If we have to reset the selection...
    if reset_selection:

      #Put the SEL tag back.
      self.tag_add(SEL, '_sel_start', '_sel_end')

      #Get rid of the marks we set.
      self.mark_unset('_sel_start')
      self.mark_unset('_sel_end')

    #Key pasting should still work fine, allowing one to select a piece
    #of text and paste to it, replacing the selection.

  def run_selection(self, event):
    '''Run the current selection if any on the stack.'''

    #Get the selection.
    select_indices = self.tag_ranges(SEL)

    #If there is a selection..
    if select_indices:

      #Get the text of the selection.
      selection = self.get(select_indices[0], select_indices[1])

      #Remove the SEL tag from the whole Text.
      self.tag_remove(SEL, 1.0, END)

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

    #Remove the SEL tag
    self.tag_remove(SEL, 1.0, END)

    #Reset the selection anchor.
    self._sel_anchor = '0.0'

    #I don't know if this helps, or even if it does anything. But what the heck.
    self.mark_unset(INSERT)

  def leave(self, event):
    '''Called when mouse leaves the Text window.'''

    #Remove any old highlighting.
    self.unset_command()

    #Unset our command variable
    self.command = ''

  def _get_index(self, index):
    '''Get the index in (int, int) form of index.'''
    return tuple(map(int, self.index(index).split('.')))

  def _paste(self, event):
    '''Paste the system selection to the current selection, replacing it.'''

    #If we're "key" pasting, we have to move the insertion point
    #to the selection so the pasted text gets inserted at the
    #location of the deleted selection.

    #Get the current selection's indices if any.
    select_indices = self.tag_ranges(SEL)

    #If the selection exists.
    if select_indices:

      #Mark the location of the current insertion cursor 
      self.mark_set('tmark', INSERT)

      #Put the insertion cursor at the selection
      self.mark_set(INSERT, select_indices[1])

    #Paste to the current selection, or if none, to the insertion cursor.
    self.event_generate("<<Paste>>")

    #If we mess with the insertion cursor above, fix it now.
    if select_indices:

      #Put the insertion cursor back where it was.
      self.mark_set(INSERT, 'tmark')

      #And get rid of our unneeded mark.
      self.mark_unset('tmark')

    #Tell Tkinter that event handling for this event is over.
    return 'break'

  def popupTB(self, tb):
    top = Toplevel()
    T = TextViewerWidget(
      self.world,
      top,
      width=max(len(s) for s in tb.splitlines()) + 3,
      )

    T['background'] = 'darkgrey'
    T['foreground'] = 'darkblue'
    T.tag_config('err', foreground='yellow')

    T.insert(END, tb)
    last_line = str(int(T.index(END).split('.')[0]) - 1) + '.0'
    T.tag_add('err', last_line, END)
    T['state'] = DISABLED

    top.title(T.get(last_line, END).strip())

    T.pack(expand=1, fill=BOTH)
    T.see(END)


def make_gui():
  t = TextViewerWidget(WorldWrapper())
  t['font'] = get_font()
  t._root().title('Joy')
  t.pack(expand=True, fill=BOTH)
  return t


class FileFaker(object):
  def __init__(self, T):
    self.T = T
  def write(self, text):
    self.T.insert(END, text)
  def flush(self):
    pass


def isNumerical(s):
  try:
    float(s)
  except ValueError:
    return False
  return True


def get_font(family='EB Garamond', size=18):
  if family not in families():
    family = 'Times'
  return Font(family=family, size=size)


def own_source():
  return getsource(modules[__name__])


if __name__ == "__main__":
  import sys
  from joy import print_words, initialize
  t = make_gui()
  sys.stdout = FileFaker(t)
  initialize()
  print_words(None)
  print()
  print('<STACK')
  # print own_source()
  t.mainloop()
