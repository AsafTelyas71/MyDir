import re
import random
import os
import hashlib
from anytree import AnyNode, RenderTree
from anytree.search import find, findall


class DirCommandParser:
    def __init__(self, path):
        self.nodes = []
        self.data = self.get_data(path)
        self.directories = re.finditer(pattern="Directory of (.+)", string=self.data)
        self.below_data = re.split(pattern="Directory of .+\n\n", string=self.data)[1:]

        do_root = True
        for curr_directory, curr_below_data in zip(self.directories, self.below_data):
            if do_root:
                r = Record(curr_directory.group(1), is_dir=True, is_root=do_root).export()
                do_root = False
                self.root_index = len(self.nodes)
                self.update_nodes(r)
            else:
                r = Record(curr_directory.group(1), root=self.nodes[0], is_dir=True, is_root=do_root).export()
                self.update_nodes(r)
            self.process_files(curr_directory.group(1), curr_below_data)

    def process_files(self, mother_line ,current_data):
        files_list = re.findall(pattern='(\d{2}/\d{2}/\d{4}  \d{2}:\d{2}) \S{2}\s+([,0-9]+) (.+)', string=current_data)
        for modified_date, size, file in files_list:
            r = Record(value=file, root=self.nodes[0], mother_line=mother_line, modified_date=modified_date,
                       size_in_kb=int(size.replace(",", ""))).export()
            self.update_nodes(r)
    def update_nodes(self, record):
        self.nodes.append(AnyNode(**record))

    def get_data(self, path):
        file_obj = open(path, "r")
        data = file_obj.read()
        file_obj.close()
        return data

class Record:

    def __init__(self, value, root=None, is_dir=False, mother_line="", is_root=False, modified_date="----------------", size_in_kb=0):
        self.is_dir = is_dir
        if self.is_dir:
            self.value = value
        else:
            self.value = os.path.join(mother_line, value)
            self.modified_date = modified_date
            self.size_in_kb = str(round(size_in_kb / 1024, 2))
        self.is_geo = self.get_ext()
        self.id = self.get_id(self.value)
        if not is_root:
            self.root_count = root.full_path.count("\\")
            self.level = self.get_level()
            self.parent = self.get_parent(root)
        else:
            self.parent = None
            self.level = 0

    def get_ext(self):
        return self.value.endswith('.dat')

    def get_parent(self, root):
        if self.level == 0:
            return None
        father_id = self.get_id(os.path.dirname(self.value))
        return find(root, lambda node: node.id == father_id)

    def get_id(self, value):
        return int(hashlib.md5(value.encode()).hexdigest(), 16)

    def get_level(self):
        return self.value.count("\\") - self.root_count

    def export(self):
        base_export = {"full_path": self.value,
                    "name": os.path.split(self.value)[1],
                    "dirname": os.path.dirname(self.value),
                    "is_dir": self.is_dir,
                    "parent": self.parent,
                    "level": self.level,
                    "id": self.id,
                    "is_geo": self.is_geo}
        if not self.is_dir:
            base_export.update({"modified_date": self.modified_date, "size_in_kb": self.size_in_kb})
        return base_export


