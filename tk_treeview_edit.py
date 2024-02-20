from typing import Any, List
import tkinter as tk
from tkinter import ttk

class TreeviewEdit(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        self.bind("<Double-1>", self.on_double_click)
        #self.bind("<ButtonRelease-1>", self.select_item)
        self.bind("<Delete>", self.delete_items)

        self.tag_configure("odd", background="lightblue")
        self.tag_configure("even", background="white")
        self.tag_configure("tree", background="#06428B")
        self.root = master

        # set column sort:
        for col in self['columns']:
            self.heading(col, command= lambda _col=col:
                    self.sort_by_col(_col, False))


    def parse_new(self, text) -> List[List[str]]:
        ''' parse the new enterered text'''
        text_array = [t.split('\t') for t in text.split('\n')]
        print(f"Parsed text: {text_array}")
        return text_array


    def select_item(self) -> None:
        '''Some development code'''
        cur_item = self.focus()
        cur_items = self.selection()
        print("self.selection:\n")
        print([self.item(i) for i in cur_items])
        print("self.focus:\n")
        print(self.item(cur_item))


    def redo_row_colors(self) -> None:
        _parent_list = self.get_children()
        for p in _parent_list:
            for i, _item in enumerate(self.get_children(p)):
                _tags = list(self.item(_item, 'tags'))
                if i % 2 == 0 and 'odd' in _tags:
                    _tags.remove('odd')
                    _tags.append('even')
                elif i % 2 != 0 and 'even' in _tags:
                    _tags.remove('even')
                    _tags.append('odd')
                self.item(_item, tags=_tags)


    def insert_rows(self,*,parent,text="",index,values=(), open=False):
        '''Returns a new node in a Treview object'''
        if parent == "":
            if text in self.get_children():
                text +="1"
            return self.insert(parent=parent,
                               text=text,
                               index=index,
                               values=values,
                               iid=text,
                               tags=("tree",),
                               open=open)

        elif len(self.get_children(parent)) % 2 == 0:
            return self.insert(parent=parent,
                               index=index,
                               values=values,
                               tags=("even",))
        else:
            return self.insert(parent=parent,
                               index=index,
                               values=values,
                               tags=("odd",))


    #Event driven functions

    def delete_items(self, event) -> None:
        '''delete multiple rows'''
        cur_items = self.selection()
        for i in cur_items:
            self.delete(i)
        self.redo_row_colors()


    def sort_by_col(self, col, reverse) -> None:
        '''sort children based on values in a column'''
        print(f'Sorting: {col}')

        if col == '#0':
            _parent_list = ''
        else:
            _parent_list = self.get_children()
        for p in _parent_list:
            _child_list = [(self.set(k, col), k) for k in self.get_children(p)]
            _child_list.sort(reverse = reverse)

            # rearrange items in sorted positions:
            for i, (val, k) in enumerate(_child_list):
                self.move(k, p, i)

            # redo colors
            self.redo_row_colors()

            # reverse sort next time
            self.heading(col, command=lambda _col=col:
                    self.sort_by_col(_col, not reverse))


    def nextfocus(self, event) -> None:
        ''' currently doesn't work'''
        event.widget.tk_focusNext().focus_set()


    def on_double_click(self, event) -> None:
        '''creates an entry box over the cell
           region. This will accept single and multiple
           values copy/pasted from excel or a csv file
           using \t and \n.'''
        region_clicked = self.identify_region(event.x, event.y)
        print(region_clicked)

        # we're only interested in tree, cell, or nothing
        if region_clicked not in ("tree", "cell", "nothing"):
            return

        # this gives column in string format: #0, #1, etc
        column = self.identify_column(event.x)

        # converts the string to an int for indexing
        column_index = int(column[1:])

        # what's currently active
        self.selected_iid = self.focus()

        #new row region
        if region_clicked == "nothing":
            _parent = list(self.get_children())[-1]
            _values = [""] * len(self['columns'])
            self.insert_rows(parent=_parent,
                    values= _values,
                    index=tk.END)
            self.selected_iid = self.get_children(_parent)[-1]

        # the current active iid's items (text, values, parent, etc)
        self.selected_items = self.item(self.selected_iid)
        self.selected_text = self.selected_items.get("text")
        self.selected_values = self.selected_items.get("values")
        self.selected_parent = self.parent(self.selected_iid)

        if self.selected_text is None:
            self.selected_text = ""
        # declare new local variable
        _text = ""

        # select the text to put in the entry box
        # parent region
        if region_clicked == "tree":
            _text = self.selected_text

        # child region
        elif region_clicked == "cell" and len(self.selected_values) != 0:
            if len(self.selected_values) < column_index:
                # fill in blanks. This will also be used in 'accept_new_text'
                while len(self.selected_values) < column_index:
                    if type(self.selected_values) == list:
                        self.selected_values.append("")
                    else:
                        print("Warning! self.selected_values is not type 'list'")
                        print(f"Type:\t{type(self.selected_values)}")
                        print(f"Value:\t{self.selected_values}")

            _text = self.selected_values[column_index - 1]

        column_box = self.bbox(self.selected_iid, column)
        entry_edit = tk.Entry(self.root, width =int(column_box[2]))

        # adding methods to record column index and item iid
        entry_edit.editing_column_index = column_index
        entry_edit.editing_item_iid = self.selected_iid

        # insert the existing text into the entry box
        entry_edit.insert(0, _text)
        entry_edit.select_range(0, tk.END)

        entry_edit.focus()

        entry_edit.bind("<FocusOut>", self.accept_new_text_array)

        entry_edit.bind("<Return>", self.accept_new_text_array)

        entry_edit.place(x=column_box[0],
                         y=column_box[1],
                         w=column_box[2],
                         h=column_box[3])


    def accept_new_text_single(self, event) -> Any:
        '''treeview insert new text'''
        new_text = event.widget.get()
        print(f'new text: {new_text}')

        # Such as I002
        selected_iid = event.widget.editing_item_iid
        self.selected_parent = self.parent(selected_iid)

        # Such as 0 (tree column), 1 (first self defined column)
        column_index = event.widget.editing_column_index

        if column_index == 0:
            self.item(selected_iid, text= new_text)
        else:
            current_values = self.selected_values
            if type(current_values) == list:
                current_values[column_index - 1] = new_text
            elif type(current_values) == None:
                current_values=list('')
            if type(current_values) != list:
                current_values = list(current_values)
            self.item(selected_iid, values=current_values)

        event.widget.destroy()


    def accept_new_text_array(self, event) -> Any:
        '''treeview insert new text by array
           this function parses csv object structures
           which use \t and \n as dividers'''

        new_text = event.widget.get()
        print(f'new text: {new_text}')

        parsed_text = self.parse_new(new_text)

        # example return: 'I002'
        selected_iid = event.widget.editing_item_iid
        self.selected_parent = self.parent(selected_iid)

        # example return: 0 (tree column), 1..n (value columns)
        _colloc0 = event.widget.editing_column_index - 1
        print(f'_colloc0: {_colloc0}')

        if _colloc0 == -1:
            self.item(selected_iid, text= new_text)
        else:
            # checked a few cases and this does return an 'ordered' tuple
            # matching the order of children.
            _iid_list = list(self.get_children(self.parent(selected_iid)))
            print(f'_iid_list:\t{_iid_list}')

            _rowloc0 = _iid_list.index(selected_iid)
            print(f'_rowloc0:\t{_rowloc0}')

            for i, row in enumerate(parsed_text):

                if len(row) + _colloc0 > len(self['columns']):
                    # truncate row
                    row = row[0:(len(self['columns']) + _colloc0)]
                    print(f'row truncated:\t{row}')

                if i + _rowloc0 > len(_iid_list) - 1:
                    print(f'inserting row')
                    row = [""] * _colloc0 + row
                    print(f'row: {row}')
                    self.insert_rows(parent=self.parent(selected_iid),
                            values=row,
                            index=tk.END)
                else:
                    _current_values = self.item(_iid_list[i + _rowloc0]).get("values")
                    print(f'current_values:\t{_current_values}')

                    if type(_current_values) == None:
                        _current_values = list('')
                    elif type(_current_values) != list:
                        _current_values = list(_current_values)

                    for j, obj in enumerate(row):
                        if type(_current_values) == list:
                            if len(_current_values) - 1 < j + _colloc0:
                                print(f'appending {obj} to end of row')
                                _current_values.append(obj)
                            else:
                                print(f'replacing {_current_values[j + _colloc0]} with {obj}')
                                _current_values[j + _colloc0] = obj
                    print(f'_iid_list item:\t{_iid_list[i + _rowloc0]}')
                    self.item(_iid_list[i + _rowloc0], values=_current_values)

        event.widget.destroy()


def endprogram(event, root):
    '''kill tk with a keystroke'''
    root.destroy()

def main() -> int:
    '''example program with car models'''
    root = tk.Tk()

    root.bind("<Escape>", lambda event: endprogram(event, root))

    column_names = ("column1", "column2", "column3", "column4")

    treeview_test = TreeviewEdit(root, columns = column_names)
    treeview_test.heading("#0", text="Vehicle Type")
    treeview_test.heading("#1", text="Vehicle Name")
    treeview_test.heading("#2", text="Year")
    treeview_test.heading("#3", text="Color")
    treeview_test.heading("#4", text="Problem")

    treeview_test.insert_rows(parent="",
                        index=tk.END,
                        text="Sedan",
                        open=True)

    treeview_test.insert_rows(parent="Sedan",
                        index=tk.END,
                        values=("Nissan Altama",
                            "2010",
                            "Silver",
                            "Expired Paper Plates"))

    treeview_test.insert_rows(parent="Sedan",
                        index=tk.END,
                        values=("Subaru Loyal",
                            "1990",
                            "White",
                            "Total S-Box"))

    suv_row = treeview_test.insert_rows(parent="",
                        index=tk.END,
                        text="SUVs",
                        open=True)

    treeview_test.insert_rows(parent="SUVs",
                        index=tk.END,
                        values=("Blue Whale",
                            "1995",
                            "Broken Door Handle"))

    treeview_test.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

    return 0

if __name__ == "__main__":
    main()
