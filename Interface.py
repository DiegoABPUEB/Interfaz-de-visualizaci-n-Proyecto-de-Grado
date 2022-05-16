import tkinter as tk
from pathlib import Path
from tkinter import Frame, ttk, Menu, messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
        self.menubar = MenuBar(parent=self.main_frame)
        self.config(menu=MenuBar)

class MenuBar(Menu):
    def __init__(self,parent):
        Menu.__init__(self,parent)

        file = Menu(self, tearoff=0)
        file.add_command(label="Abrir")
        file.add_command(label="Guardar")
        file.add_separator()
        file.add_command(label="Salir", underline=1, command=self.quit)
        self.add_cascade(label="Archivo", underline=0,menu=file)
    
        help = Menu(self, tearoff=0)  
        help.add_command(label="Sobre nosotros", command=self.about)  
        self.add_cascade(label="Ayuda", menu=help)

    def about(self):
        messagebox.showinfo('Universidad El Bosque', 'Extensión pensada para el software de procesamiento de vídeo deportivo Kinovea, con el fin de proveer una herramienta de visualización partiendo de la lectura de archivos .csv')

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
        self.file_names_listbox.place(rely=0.03,relheight=0.97,relwidth=0.25)
        self.file_names_listbox.drop_target_register(DND_FILES)
        # TODO BINDING
        self.file_names_listbox.dnd_bind('<<Drop>>', self.drop_in_listbox)
        self.file_names_listbox.bind('<Double-1>',self.display_file)

        #Treeview
        self.data_table = DataTable(parent)
        self.data_table.place(relx=0.25,rely=0.03,relheight=0.91,relwidth=0.75)

        self.graphButton = ttk.Button(text='Generar gráfica', command=self.graphWindow)
        self.graphButton.place(relx=0.6,rely=0.94,relheight=0.06)

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
    
    def graphWindow(self):
        try:
            self.path_map[self.file_names_listbox.get(self.file_names_listbox.curselection())]
        except Exception:
            messagebox.showerror('Error', 'Por favor seleccione un archivo válido')
            return
        
        file_path = self.path_map[self.file_names_listbox.get(self.file_names_listbox.curselection())]
        df = pd.read_csv(file_path, header=0, delimiter=';', decimal = ',')

        # print(df.columns[0]) #Da el nombre de los datos (header)
        # print(df.columns[1])

        fig, ax = plt.subplots()
        ax.plot(df[df.columns[0]], df[df.columns[1]])
        ax.set_xlabel(df.columns[0])
        ax.set_ylabel(df.columns[1])
        ax.set_title(self.file_names_listbox.get(self.file_names_listbox.curselection()))

        fig.set_size_inches(7,5)
        fig.set_dpi(100)
        plt.show()
            

if __name__ == '__main__':
    root = Application()
    root.iconbitmap('Universidad-El-Bosque_0.ico')
    root.mainloop()
