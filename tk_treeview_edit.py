from typing import Any, List, Dict, Tuple, Literal
import tkinter as tk
from tkinter import ttk

UPARROW = "⬆"
DOWNARROW = "⬇"

class TreeviewEdit(ttk.Treeview):
    def __init__(self, master, **kw):
        '''
        Extension of a Treeview object.
        Has some similar functionality to Excel.

        Parameters:
            master(root) -> the parent Tk object
        '''
        super().__init__(master, **kw)

        self.selected_iid: str = ''
        self.selected_column: str = '#0'

        self.bind("<Double-1>", lambda event: self.create_edit_box(event.x, event.y))
        self.bind("<Shift-Double-1>", self.clear_cells_column)
        self.bind("<Delete>", self.delete_items)
        self.bind("<Tab>", self.next_cell_tab)

        # config options are: background, foreground, font, image
        self.tag_configure("odd", background="lightblue")
        self.tag_configure("even", background="white")
        self.tag_configure("tree", background="#06428B")
        self.tag_configure("selected", foreground = "yellow") # for testing
        self.root = master

        # set column sort:
        for col in self['columns']:
            self.heading(col, command= lambda _col=col:
                    self.sort_by_col(_col, False))

    @property
    def sel_column_index(self) -> int:
        '''numeric value of column'''
        return int(self.selected_column[1:])

    @property
    def selected_parent(self) -> str:
        '''parent of selected_iid'''
        return self.parent(self.selected_iid)

    @property
    def selected_item(self):
        '''item of selected_iid'''
        return self.item(self.selected_iid)

    @property
    def selected_text(self) -> str:
        '''text of selected_iid'''
        if self.selected_item.get("text") == None:
            return ""
        return self.selected_item.get("text")

    @property
    def selected_values(self) -> list[Any] | Literal['']:
        '''values of selected_iid'''
        return self.selected_item.get("values")

    @property
    def other_selected_options(self) -> list[str]:
        print(f'other selected options: {list(self.get_children(self.selected_parent))}')
        return list(self.get_children(self.selected_parent))

    @property
    def other_selected_options_index(self) -> int:
        return list(self.get_children(
            self.selected_parent)).index(self.selected_iid)

    def parse_new(self, text) -> List[List[str]]:
        ''' parse the new enterered text'''
        text_array = [t.split('\t') for t in text.split('\n')]
        #print(f"Parsed text: {text_array}")
        return text_array


    def select_item(self) -> None:
        '''Some useful development code'''
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


    def sort_by_col(self, col: str, reverse: bool) -> None:
        '''sort children based on values in a column'''
        print(f'Sorting: {col}. Has type {type(col)}')

        _parent_list = self.get_children()
        for p in _parent_list:
            _child_list = [(self.set(k, col), k) for k in self.get_children(p)]
            _child_list.sort(reverse = reverse)

            # rearrange items in sorted positions:
            for i, (_, k) in enumerate(_child_list):
                self.move(k, p, i)

            # redo colors
            self.redo_row_colors()

            # reverse sort next time
            self.heading(col, command=lambda _col=col:
                    self.sort_by_col(_col, not reverse))


    #Event driven functions

    def delete_items(self, event) -> None:
        '''delete multiple rows'''
        cur_items = self.selection()
        for i in cur_items:
            self.delete(i)
        self.redo_row_colors()


    def clear_cells_column(self, event) -> None:
        '''
        Clear all cells in a column.
        '''
        _region = self.identify_region(event.x, event.y)
        if _region not in ("heading"):
            return
        _col = self.identify_column(event.x)
        print(_col)
        _parent_list = self.get_children()

        for p in _parent_list:
            for k in self.get_children(p):
                self.set(k, _col, '')


    def next_cell_tab(self, event) -> None:
        '''
        selects the next cell in a group of values.
        This cycles - after the last item it will wrap
        around to the first item.
        '''

        if self.selected_iid == "":
            # select the first cell in the group
            print(f'self.selected_iid is empty string. using first parent: {self.get_children()[0]}')
            self.selected_iid = self.get_children()[0]
            self.selected_column = '#0'
            self.focus(self.selected_iid)
        else:
            # if at the end of a list of values, move to next row
            if self.sel_column_index >= len(self.selected_values):
                _iid_list = self.other_selected_options
                _next_row = (_iid_list.index(self.selected_iid) + 1) % len(_iid_list)
                self.selected_iid = _iid_list[_next_row]
                self.focus(self.selected_iid)
                self.selected_column = '#1'
            # otherwise, move to next value
            else:
                self.selected_column = f'#{self.sel_column_index + 1}'
            if (self.selected_iid in self.get_children() and
                    self.selected_values == '' and
                    len(self.get_children(self.selected_iid)) != 0):
                self.selected_column = '#0'
        _col_box = self.bbox(self.selected_iid, self.selected_column)
        self.create_edit_box(int(_col_box[0]) + 5, int(_col_box[1]) + 5)


    def create_edit_box(self, coordx, coordy) -> None:
        '''creates an entry box over the cell
           region. This will accept single and multiple
           values copy/pasted from excel or a csv file
           using \t and \n.'''
        _region_clicked = self.identify_region(coordx, coordy)

        # we're only interested in tree, cell, or nothing
        if _region_clicked not in ("tree", "cell", "nothing"):
            return

        # this gives column in string format: #0, #1, etc
        self.selected_column = self.identify_column(coordx)

        # what's currently active
        self.selected_iid = self.focus()

        #new row region
        if _region_clicked == "nothing":
            _parent = list(self.get_children())[-1]
            _values = [""] * len(self['columns'])
            self.insert_rows(parent=_parent,
                    values= _values,
                    index=tk.END)
            self.selected_iid = self.get_children(_parent)[-1]

        # declare new local variable
        _text = ""

        # select the text to put in the entry box
        # parent region
        if _region_clicked == "tree":
            _text = self.selected_text

        # child region
        elif _region_clicked == "cell" and len(self.selected_values) != 0:
            if len(self.selected_values) < self.sel_column_index:
                # fill in blanks. This will also be used in 'accept_new_text'
                while len(self.selected_values) < self.sel_column_index:
                    if type(self.selected_values) == list:
                        self.selected_values.append("")
                    else:
                        print("Warning! self.selected_values is not type 'list'")
                        print(f"Type:\t{type(self.selected_values)}")
                        print(f"Value:\t{self.selected_values}")

            _text = self.selected_values[self.sel_column_index - 1]
        column_box = self.bbox(self.selected_iid, self.selected_column)
        entry_edit = tk.Entry(self.root, width =int(column_box[2]))

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
        _new_text = event.widget.get()

        if self.sel_column_index == 0:
            self.item(self.selected_iid, text= _new_text)
        else:
            current_values = self.selected_values
            if type(current_values) == list:
                current_values[self.sel_column_index - 1] = _new_text
            elif type(current_values) == None:
                current_values=list('')
            if type(current_values) != list:
                current_values = list(current_values)
            self.item(self.selected_iid, values=current_values)

        event.widget.destroy()


    def accept_new_text_array(self, event) -> Any:
        '''treeview insert new text by array
           this function parses csv/excel object structures
           which use \t and \n as dividers'''

        _new_text = event.widget.get()

        _parsed_text = self.parse_new(_new_text)

        # example return: 'I002'
        _selected_iid = self.selected_iid

        _colloc0 = self.sel_column_index - 1

        if _colloc0 == -1:
            self.item(_selected_iid, text= _new_text)
        else:
            # checked a few cases and this does return an 'ordered' tuple
            # matching the order of children.
            _iid_list = list(self.get_children(self.parent(_selected_iid)))

            _rowloc0 = _iid_list.index(_selected_iid)

            for i, row in enumerate(_parsed_text):

                if len(row) + _colloc0 > len(self['columns']):
                    # truncate row
                    row = row[0:(len(self['columns']) + _colloc0)]

                if i + _rowloc0 > len(_iid_list) - 1:
                    row = [""] * _colloc0 + row
                    self.insert_rows(parent=self.parent(_selected_iid),
                            values=row,
                            index=tk.END)
                else:
                    _current_values: list[Any] | Literal[''] = \
                        self.item(_iid_list[i + _rowloc0]).get("values")

                    if type(_current_values) == None:
                        _current_values = list('')

                    for j, obj in enumerate(row):
                        if type(_current_values) == list:
                            if len(_current_values) - 1 < j + _colloc0:
                                _current_values.append(obj)
                            else:
                                _current_values[j + _colloc0] = obj
                    self.item(_iid_list[i + _rowloc0], values=_current_values)

        event.widget.destroy()


class RightClickMenu(tk.Menu):
    '''A right-click menu object. Designed for TreeviewEdit'''

    def __init__(self, master: TreeviewEdit):
        '''
        Parameters:

            master(TreeviewEdit) -> the parent TreeviewEdit object

        #TODO: Should list:
            sort ascending/descending
            delete rows
            add row
            copy
            paste?
        '''
        super().__init__(master, tearoff=False)
        self.master = master
        self.cid = None
        self.iid = None

        config: Dict[str, Dict[str, Any]] = {
                "sortascending": {
                    "label": f"{UPARROW} Sort Ascending",
                    "command": self.sort_by_col_asc,
                    },
                "sortdescending": {
                    "label": f"{DOWNARROW} Sort Descending",
                    "command": self.sort_by_col_desc,
                    },
                "deleterows": {
                    "label": "Delete Selected Rows",
                    "command": self.master.delete_items,
                    },
                "addrow": {
                    "label": "Add New Row",
                    "command": self.insert_rows,
                    },
                "copy": {
                    "label": "Copy",
                    "command": print("TODO") #TODO
                    },
                "paste": {
                    "label": "Paste",
                    "command": print("TODO") #TODO
                    }
                }

        sort_menu = tk.Menu(self, tearoff=False)
        sort_menu.add_command(cnf=config["sortascending"])
        sort_menu.add_command(cnf=config["sortdescending"])
        self.add_cascade(menu=sort_menu, label=f'{UPARROW}{DOWNARROW} Sort')

        self.add_command(cnf=config["deleterows"])
        self.add_command(cnf=config["addrow"])
        self.add_command(cnf=config["copy"])
        self.add_command(cnf=config["paste"])

    def sort_by_col_desc(self, event) -> None:
        pass

    def sort_by_col_asc(self, event) -> None:
        pass

    def insert_rows(self, event) -> None:
        pass

    def tk_popup_wrapper(self, event):
        '''Display the menu below the selected cell'''
        self.event = event
        _iid = self.master.identify_row(event.y)
        _col = self.master.identify_column(event.x)

        # show the menu below the invoking cell
        print(self.master.bbox(_iid, _col))
        try:
            self.tk_popup(0, 0)
        except:
            print("Ran into an issue")
            return

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
