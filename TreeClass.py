from tkinter import *
from tkinter import ttk
from DirCommandParser import DirCommandParser
from anytree.search import find, findall
class Window:

    def __init__(self, path):
        self.nodes = DirCommandParser(path).nodes
        self.root = Tk()
        self.my_tree = ttk.Treeview(self.root)
        self.desgin_root()
        self.design_tree()
        self.design_buttons()
        self.reset_filter()
        self.root.mainloop()



    def desgin_root(self):
        self.root.title('MyDir')
        self.root.geometry('600x600')
        self.my_menu = Menu(self.root)
        self.root.config(menu=self.my_menu)
        style = ttk.Style()
        style.map('Treeview', foreground=self.fixed_map(style, 'foreground'),
                  background=self.fixed_map(style, 'background'))

    def design_tree(self):
        self.my_tree["columns"] = ("Name", "Size", "Modified Date")
        # my_tree.column("#0", width=120, minwidth=10)
        self.my_tree.column("Name", anchor=W, width=120)
        self.my_tree.column("Size", anchor=CENTER, width=120)
        self.my_tree.column("Modified Date", anchor=W, width=120)

        # my_tree.heading("#0", text="Label")
        self.my_tree.heading("Name", text="Name", anchor=W)
        self.my_tree.heading("Size", text="Size", anchor=CENTER)
        self.my_tree.heading("Modified Date", text="Modified Date", anchor=W)
        self.my_tree.tag_configure('geo', foreground='green')
        self.my_tree.pack(pady=20)

    def design_buttons(self):
        search_menu = Menu(self.my_menu, tearoff=0)
        self.my_menu.add_cascade(label="Search", menu=search_menu)
        search_menu.add_command(label="Search", command=self.lookup_records)
        reset_button = Button(self.root, text="Reset Tree", command=self.reset_filter)
        geo_button = Button(self.root, text="Geo Filter", command=self.geo_filter)
        reset_button.pack(pady=30)
        geo_button.pack()

    def populate_tree(self, selections):
        for record in self.my_tree.get_children():
            self.my_tree.delete(record)
        for curr_node in selections:
            parent = ''
            open = 0
            values = [curr_node.name]
            tags = ["all"]
            if curr_node.level != 0:
                parent = curr_node.parent.id
            else:
                open = 1
            if not curr_node.is_dir:
                values.extend([curr_node.size_in_kb, curr_node.modified_date])
            if curr_node.is_geo:
                tags.append("geo")
                temp = curr_node.parent
                while temp:
                    self.my_tree.item(temp.id, tags=("all", "geo"))
                    temp = temp.parent
            self.my_tree.insert(parent=parent, index='end', iid=curr_node.id, values=values, tags=tags, open=open)

    def get_current_nodes(self):
        nodes_ids = list(self.my_tree.get_children())
        for curr_id in nodes_ids:
            nodes_ids.extend(self.my_tree.get_children(curr_id))
        nodes = [find(self.nodes[0], lambda node: node.id == int(curr_id)) for curr_id in nodes_ids]
        return list(sorted(nodes, key=lambda  node: node.level))

    def add_parents(self, selections):
        for index in range(len(selections)):
            temp = selections[index]
            while temp.level != 0:
                parent = find(self.nodes[0], lambda node: node.id == temp.parent.id)
                if parent not in selections:
                    selections.append(parent)
                temp = parent
        selections = list(sorted(selections, key=lambda node: node.level))
        return selections

    def lookup_records(self):
        global search_entry, search
        search = Toplevel(self.root)
        search.title("Lookup Records")
        search.geometry('400x200')

        search_frame = LabelFrame(search, text="text")
        search_frame.pack(padx=10, pady=10)

        search_entry = Entry(search_frame, font=('David', 18))
        search_entry.pack(padx=20, pady=20)

        search_button = Button(search, text="Search Records", command=self.search_records)
        search_button.pack(padx=20, pady=20)

    def search_records(self):
        lookup_record = search_entry.get()
        current_nodes = self.get_current_nodes()
        selections = list(findall(current_nodes[0], filter_=lambda node: (lookup_record.lower() in node.name.lower()) and node in current_nodes))
        selections = self.add_parents(selections)
        self.populate_tree(selections)
        search.destroy()

    def reset_filter(self):
        self.populate_tree(self.nodes)

    def geo_filter(self):
        current_nodes = self.get_current_nodes()
        selections = list(findall(current_nodes[0], lambda node: (node.is_geo and node in current_nodes)))
        selections = self.add_parents(selections)
        self.populate_tree(selections)

    def fixed_map(self, style, option):
        return [elm for elm in style.map('Treeview', query_opt=option) if
                elm[:2] != ('!disabled', '!selected')]

t = Window(path=r"C:\Users\user\Desktop\Courses\Python\dir2\test.txt")
