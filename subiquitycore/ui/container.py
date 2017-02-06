# Portions Copyright 2017 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This is adapted from
# https://github.com/pimutils/khal/commit/bd7c5f928a7670de9afae5657e66c6dc846688ac, which has this license:
#
# Copyright (c) 2013-2015 Christian Geier et al.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging

import urwid

log = logging.getLogger('subiquitycore.ui.container')


def _maybe_select_first_selectable(w):
    """If w implements _select_first_selectable, call it."""
    m = getattr(w.base_widget, "_select_first_selectable", None)
    if m is not None:
        m()

def _maybe_select_last_selectable(w):
    """If w implements _select_last_selectable, call it."""
    m = getattr(w.base_widget, "_select_last_selectable", None)
    if m is not None:
        m()


class TabCyclingMixin:
    """Tab-cycling implementation that works with Pile and Columns."""

    def _select_first_selectable(self):
        """Select first selectable child (possibily recursively)."""
        for i, (w, o) in enumerate(self.contents):
            if w.selectable():
                self.set_focus(i)
                _maybe_select_first_selectable(w)
                return

    def _select_last_selectable(self):
        """Select last selectable child (possibily recursively)."""
        for i, (w, o) in reversed(list(enumerate(self.contents))):
            if w.selectable():
                self.set_focus(i)
                _maybe_select_last_selectable(w)
                return

    def keypress(self, size, key):
        key = super(TabCyclingMixin, self).keypress(size, key)

        if key == 'tab':
            next_fp = self.focus_position + 1
            for i, (w, o) in enumerate(self._contents[next_fp:], next_fp):
                if w.selectable():
                    self.set_focus(i)
                    _maybe_select_first_selectable(w)
                    return
            self._select_first_selectable()
            return key
        elif key == 'shift tab':
            for i, (w, o) in reversed(list(enumerate(self._contents[:self.focus_position]))):
                if w.selectable():
                    self.set_focus(i)
                    _maybe_select_last_selectable(w)
                    return
            self._select_last_selectable()
            return key
        else:
            return key


class TabCyclingPile(TabCyclingMixin, urwid.Pile):
    pass

class TabCyclingColumns(TabCyclingMixin, urwid.Columns):
    pass


class TabCyclingListBox(urwid.ListBox):
    # It feels like it ought to be possible to write TabCyclingMixin
    # so it works for a ListBox as well, but it seems to be just
    # awkward enough to make the repeated code the easier and clearer
    # option.

    def __init__(self, body):
        # urwid.ListBox converts an arbitrary sequence argument to a
        # PollingListWalker, which doesn't work with the below code.
        if getattr(body, 'get_focus', None) is None:
            body = urwid.SimpleListWalker(body)
        super().__init__(body)

    def _set_focus_no_move(self, i):
        # We call set_focus twice because otherwise the listbox
        # attempts to do the minimal amount of scrolling required to
        # get the new focus widget into view, which is not what we
        # want, as if our first widget is a compound widget it results
        # its last widget being focused -- in fact the opposite of
        # what we want!
        self.set_focus(i)
        self.set_focus(i)
        # I don't really understand why this is required but it seems it is.
        self._invalidate()

    def _select_first_selectable(self):
        """Select first selectable child (possibily recursively)."""
        for i, w in enumerate(self.body):
            if w.selectable():
                self._set_focus_no_move(i)
                _maybe_select_first_selectable(w)
                return

    def _select_last_selectable(self):
        """Select last selectable child (possibily recursively)."""
        for i, w in reversed(list(enumerate(self.body))):
            if w.selectable():
                self._set_focus_no_move(i)
                _maybe_select_last_selectable(w)
                return

    def keypress(self, size, key):
        key = super(TabCyclingListBox, self).keypress(size, key)

        if key == 'tab':
            next_fp = self.focus_position + 1
            for i, w in enumerate(self.body[next_fp:], next_fp):
                if w.selectable():
                    self.set_focus(i)
                    _maybe_select_first_selectable(w)
                    return
            self._select_first_selectable()
            return key
        elif key == 'shift tab':
            for i, w in reversed(list(enumerate(self.body[:self.focus_position]))):
                if w.selectable():
                    self.set_focus(i)
                    _maybe_select_last_selectable(w)
                    return
            self._select_last_selectable()
            return key
        else:
            return key


Columns = TabCyclingColumns
Pile = TabCyclingPile
ListBox = TabCyclingListBox
