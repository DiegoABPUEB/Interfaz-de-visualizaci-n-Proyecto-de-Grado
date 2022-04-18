import tkinter as tk
from pathlib import Path
from tkinter import Frame, ttk

import pandas as pd
from tkinterdnd2 import DND_FILES, TkinterDnD


class Application(TkinterDnD.Tk):
    
    def __init__(self) -> None:
        super().__init__()
        self.title("Visualizador")
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both",expand="true")
        self.geometry("900x500")

        #Creating the parent
        self.search_page = SearchPage(parent=self.main_frame)

class DataTable(ttk.Treeview):
    def __init__(self,parent):
        super().__init__(parent)
        scrollXbar = tk.Scrollbar(self,orient="horizontal", command=self.xview)
        scrollYbar = tk.Scrollbar(self,orient="vertical", command=self.yview)
        self.configure(yscrollcommand=scrollYbar.set, xscrollcommand=scrollXbar.set)
        scrollXbar.pack(side="bottom", fill="x")
        scrollYbar.pack(side="right", fill="y")
        self.dataFrame = pd.DataFrame()

    def set_dataTable(self,dataframe):
        self.dataFrame = dataframe
        self.draw_datatable(dataframe)

    def draw_datatable(self, dataframe):
        self.delete(*self.get_children())
        columns = list(dataframe.columns)
        self.__setitem__("column", columns)
        self.__setitem__("show", "headings")

        for col in columns:
            self.heading(col, text=col)

        df_rows = dataframe.values.tolist()

        for row in df_rows:
            self.insert("","end", values=row)
        
        return None
    
    def reset_table(self):
        self.draw_datatable(self.dataFrame)

    def find_values(self, pairs):
        aux_dataframe = self.dataFrame
        for col, value in pairs.items():
            query_string = f"{col}.str.contains('{value}')"
            aux_dataframe = aux_dataframe.query(query_string, engine = "python")
        
        self.draw_datatable(aux_dataframe)

class SearchPage(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.file_names_listbox = tk.Listbox(parent, selectmode=tk.SINGLE, background='darkgrey')
        self.file_names_listbox.place(relheight=1,relwidth=0.25)
        self.file_names_listbox.drop_target_register(DND_FILES)
        # TODO BINDING
        self.file_names_listbox.dnd_bind('<<Drop>>', self.drop_in_listbox)
        self.file_names_listbox.bind('<Double-1>',self.display_file)

        self.search_entrybox = tk.Entry(parent)
        self.search_entrybox.place(relx=0.25, relwidth=0.75)
        self.search_entrybox.bind('<Return>', self.search_table)

        #Treeview
        self.data_table = DataTable(parent)
        self.data_table.place(relx=0.25,rely=0.05,relheight=0.95,relwidth=0.75)

        self.path_map = {}

    def drop_in_listbox(self, event):
        file_paths = self.parse_file(event.data)
        actual_items = set(self.file_names_listbox.get(0, "end"))
        for file_path in file_paths:
            if file_path.endswith(".csv"):
                file_object = Path(file_path)
                file_name = file_object.name
                if file_name not in actual_items:
                    self.file_names_listbox.insert("end",file_name)
                    self.path_map[file_name] = file_path

    def display_file(self, event):
        file_name = self.file_names_listbox.get(self.file_names_listbox.curselection())
        path = self.path_map[file_name]
        df = pd.read_csv(path, on_bad_lines='skip', delimiter=';', header=0) #Take care of this later
        self.data_table.set_dataTable(dataframe=df)

    def parse_file(self,filename):
        size_filename = len(filename)
        result = []
        name = ""
        index = 0

        while index < size_filename:
            if filename[index] == '{':
                auxidx = index + 1
                while filename[auxidx] != '}':
                    name+=filename[auxidx]
                    auxidx+=1
                result.append(name)
                name = ""
                index = auxidx
            elif filename[index] == " " and name != "":
                result.append(name)
                name = ""
            elif filename[index] != " ":
                name +=  filename[index]
            index+=1 
        if name != "":
            result.append(name)

        return result

    def search_table(self, event):
        entry = self.search_entrybox.get()

        if entry == "":
            self.data_table.reset_table()
        else:
            entry_split = entry.split(",")
            column_value_pairs = {}

            for pair in entry_split:
                pair_split = pair.split("=")
                if len(pair_split) == 2:
                    col = pair_split[0]
                    lookup_value = pair_split[1]
                    column_value_pairs[col] = lookup_value
            self.data_table.find_values(pairs=column_value_pairs)

if __name__ == '__main__':
    root = Application()
    root.mainloop()
