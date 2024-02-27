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
from tk_treeview_table import TreeviewTable

class FrameScroll(tk.Frame):
    '''
    This class nests several Tk objects to
    creates a vertical scroll bar in a frame.

        FrameScroll - tk frame containing
            'canvas' w/scroll bar containing
                'interior' - tk frame that can be populated

    Parameters:
        parent -> the parent Tk object
        ttk.Frame args or kwargs
    '''

    def __init__(self, parent: ttk.Frame | ttk.Notebook,
            *args,
            **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.canvas = tk.Canvas(self, bd=0,
                highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        self.interior = ttk.Frame(self.canvas, padding= "2 2 12 12")
        self.interior_id = self.canvas.create_window(0,0,
                window=self.interior,
                anchor=tk.NW)

        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL,
                command=self.canvas.yview)
        self.canvas['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(fill=tk.Y, side= tk.RIGHT, expand= tk.FALSE)


        self.interior.bind('<Configure>', self.configure_interior)
        self.canvas.bind('<Configure>', self.configure_canvas)
        self.bind('<Enter>', self.bound_to_mousewheel)
        self.bind('<Leave>', self.unbound_to_mousewheel)

        self.pack()

    def configure_interior(self, event) -> None:
            _size = (self.interior.winfo_reqwidth(),
                     self.interior.winfo_reqheight())
            self.canvas.config(scrollregion=(0, 0, _size[0], _size[1]))
            if (self.interior.winfo_reqwidth() !=
                    self.canvas.winfo_width()):
                self.canvas.config(
                        width=self.interior.winfo_reqwidth())

    def configure_canvas(self, event) -> None:
            if (self.interior.winfo_reqwidth() !=
                    self.canvas.winfo_width()):
                self.canvas.itemconfigure(self.interior_id,
                        width=self.canvas.winfo_width())

    def bound_to_mousewheel(self, event):
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)

    def unbound_to_mousewheel(self, event):
        self.canvas.unbind_all('<MouseWheel>')

    def on_mousewheel(self, event) -> None:
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


def end_program(event, root) -> None:
    root.destroy()

def notebook_example(root: tk.Tk) -> None:

    mainframe = ttk.Notebook(root, padding = "2 2 12 12")
    mainframe.pack(expand=1, fill="both")
    tabs: Dict[str, FrameScroll] = {}
    for i in range(5):
        tabs[f"framescroll{i}"] = FrameScroll(mainframe)
        mainframe.add(tabs[f"framescroll{i}"], text=f"Scroll {i}")
        buttons = []
        for j in range(20):
            buttons.append(
                    ttk.Button(tabs[f"framescroll{i}"].interior,
                    text=f"Button {j}"))
            buttons[-1].pack()
    ttk.Label(root, text="Shrink the window to activate the scrollbar")

    root.mainloop()


def frame_example(root: tk.Tk) -> None:
    mainframe = ttk.Frame(root, padding = "2 2 12 12")
    mainframe.pack(expand=1, fill="both")
    frame= FrameScroll(mainframe)
    #frame.pack()
    label = ttk.Label(root, text="Shrink the window to scroll")
    label.pack()
    buttons = []
    for i in range(20):
        buttons.append(ttk.Button(frame.interior, text=f"Button {i}"))
        buttons[-1].pack()

    root.mainloop()

def main() -> int:
    '''example program'''
    root = tk.Tk()
    root.bind('<Escape>', lambda e: end_program(e, root)) #end program
    notebook_example(root)
    #frame_example(root)

    return 0

if __name__ == '__main__':
    main()
