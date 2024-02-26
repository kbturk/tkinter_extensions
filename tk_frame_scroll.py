# Copyright (c) 2024 kbt | terminus, LLC

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Any, List, Dict, Tuple, Literal
import tkinter as tk
from tkinter import ttk

class FrameScroll:
    '''
    **WIP/TODO**
    This class nests several Tk objects to
    creates a vertical scroll bar in a frame.

    parent contains
        outer_frame contains
            canvas w/scroll bar contains
                inner_frame

    Parameters:
        parent -> the parent Tk object
        master(root) -> the master Tk object
        inner_frame -> the inner Tk object
    TODO obj:
        lookup parent type in TK documentation
        test code
    '''

    def __init__(self, parent, master: tk.Tk):
        self.outer_frame = ttk.Frame(parent)
        self.canvas_frame = tk.Canvas(self.outer_frame, bd=0,
                highlightthickness=0)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        self.is_scrollbar = ttk.Scrollbar(self.outer_frame,
                orient=tk.VERTICAL, command=self.canvas_frame.yview)
        self.is_scrollbar.pack(fill=tk.Y, side= tk.RIGHT, expand= tk.FALSE)

        self.canvas_frame['yscrollcommand'] = self.is_scrollbar.set
        self.canvas_frame.xview_moveto(0)
        self.canvas_frame.yview_moveto(0)

        self.inner_frame = ttk.Frame(self.canvas_frame,
                padding= "2 2 12 12")
        self.is_interior = self.canvas_frame.create_window(0,0,
                window=self.inner_frame,
                anchor=tk.NW)

        self.inner_frame.bind('<Configure>', self.configure_is_interior)
        self.canvas_frame.bind('<Configure>', self.configure_canvas_frame)
        self.outer_frame.bind('<Enter>', self.bound_to_mousewheel)
        self.outer_frame.bind('<Leave>', self.unbound_to_mousewheel)

        self.canvas_frame['height'] = min(
                master.winfo_screenheight(),
                886)


    def configure_is_interior(self, event) -> None:
            _size = (self.inner_frame.winfo_reqwidth(),
                     self.inner_frame.winfo_reqheight())
            self.canvas_frame.config(scrollregion=(0, 0, _size[0], _size[1]))
            if (self.inner_frame.winfo_reqwidth() !=
                    self.canvas_frame.winfo_width()):
                self.canvas_frame.config(
                        width=self.inner_frame.winfo_reqwidth())

    def configure_canvas_frame(self, event) -> None:
            if (self.inner_frame.winfo_reqwidth() !=
                    self.canvas_frame.winfo_width()):
                self.canvas_frame.itemconfigure(self.is_interior,
                        width=self.canvas_frame.winfo_width())

    def bound_to_mousewheel(self, event):
        self.canvas_frame.bind_all('<MouseWheel>', self.on_mousewheel)

    def unbound_to_mousewheel(self, event):
        self.canvas_frame.unbind_all('<MouseWheel>')

    def on_mousewheel(self, event) -> None:
        self.canvas_frame.yview_scroll(int(-1*(event.delta/120)), "units")
