from typing import Any, List
import tkinter as tk
from tkinter import ttk

class TreeviewEdit(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        self.bind("<Double-1>", self.on_double_click)
        self.bind("<Tab>", self.nextfocus)
        '''
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                background="white",
                foreground="black",
                rowheight=25,
                fieldbackground="white"
                )
        self.tag_configure("odd", background="white")
        self.tag_configure("even", background="#cecece")
        self.tag_configure("tree", background="#06428B", foreground="white")
        '''
        self.tag_configure("odd")
        self.tag_configure("even")
        self.tag_configure("tree")

    def on_double_click(self, event):
        region_clicked = self.identify_region(event.x, event.y)

        # we're only interested in tree, cell, or nothing
        if region_clicked not in ("tree", "cell", "nothing"):
            return

        print(region_clicked)

        column = self.identify_column(event.x)
        column_index = int(column[1:])

        selected_iid = self.focus()
        selected_items = self.item(selected_iid)
        selected_text = selected_items.get("text")
        selected_values = selected_items.get("values")
        _text = ""

        #new row region
        if selected_text == "" and selected_values == "":
            self.add_row(event)

        #parent region
        elif column == "#0":
            _text = selected_text

        #child region
        elif len(selected_values) != 0:
            _text = selected_values[column_index - 1]

        print(_text)

        column_box = self.bbox(selected_iid, column)
        entry_edit = ttk.Entry(root, width =column_box[2])

        #adding methods to record column index and item iid
        entry_edit.editing_column_index = column_index
        entry_edit.editing_item_iid = selected_iid

        entry_edit.insert(0, _text)
        entry_edit.select_range(0, tk.END)

        entry_edit.focus()

        entry_edit.bind("<FocusOut>", self.accept_new_text)

        entry_edit.bind("<Return>", self.accept_new_text)

        entry_edit.place(x=column_box[0],
                         y=column_box[1],
                         w=column_box[2],
                         h=column_box[3])

    # add a new row to the treeview object
    def add_row(self, event) -> None:
        pass

    # parse the new enterered stuff
    def parse_new(self, text) -> None:
        pass

    def nextfocus(self, event) -> None:
        event.widget.tk_focusNext().focus_set()

    def accept_new_text(self, event) -> Any: #treeview insert object
        new_text = event.widget.get()

        # Such as I002
        selected_iid = event.widget.editing_item_iid

        # Such as 0 (tree column), 1 (first self defined column)
        column_index = event.widget.editing_column_index

        if column_index == 0:
            self.item(selected_iid, text= new_text)
        else:
            current_values = self.item(selected_iid).get("values")
            if type(current_values) == list:
                current_values[column_index - 1] = new_text
            elif type(current_values) == None:
                current_values=''
            self.item(selected_iid, values=current_values)

        event.widget.destroy()

    def insert_rows(self,*,parent,text="",index,values=()):
        if parent == "":
            if text in self.get_children():
                text +="1"
            return self.insert(parent=parent,
                               text=text,
                               index=index,
                               values=values,
                               iid=text,
                               tags=("tree",))

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


# kill tk with a keystroke
def endprogram(event, root):
    root.destroy()

if __name__ == "__main__":
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
                        text="Sedan")

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
                        text="SUVs")


    treeview_test.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
