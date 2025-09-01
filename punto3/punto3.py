import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import os
from datetime import datetime


# ====================
# Clases para el Sistema de Archivos
# ====================
class FileSystemNode:
    def __init__(self, name, is_directory=True, size=0):
        self.name = name
        self.is_directory = is_directory
        self.size = size  # tamaño en bytes (para archivos)
        self.creation_date = datetime.now()
        
        # Representación primer hijo/hermano siguiente
        self.first_child = None  # primer contenido del directorio
        self.next_sibling = None  # siguiente elemento en el mismo directorio
        self.parent = None  # referencia al padre


class FileSystem:
    def __init__(self, root_name="C:\\"):
        self.root = FileSystemNode(root_name, is_directory=True)
        self._initialize_sample_structure()

    def _initialize_sample_structure(self):
        """Inicializa una estructura de archivos de ejemplo"""
        # Crear estructura de ejemplo
        users = self._add_child(self.root, "Users", is_directory=True)
        documents = self._add_child(users, "Documents", is_directory=True)
        pictures = self._add_child(users, "Pictures", is_directory=True)
        
        # Subcarpetas en Documents
        work = self._add_child(documents, "Work", is_directory=True)
        personal = self._add_child(documents, "Personal", is_directory=True)
        
        # Archivos en Work
        self._add_child(work, "Tarea___01.pdf", is_directory=False, size=2048000)  # 2MB
        self._add_child(work, "Algoritmos.pptx", is_directory=False, size=5120000)  # 5MB
        self._add_child(work, "cuentas.xlsx", is_directory=False, size=1024000)  # 1MB
        
        # Archivos en Personal
        self._add_child(personal, "notas.txt", is_directory=False, size=512)
        self._add_child(personal, "fotos.zip", is_directory=False, size=10485760)  # 10MB
        
        # Archivos en Pictures
        self._add_child(pictures, "viajecito.jpg", is_directory=False, size=2048000)
        self._add_child(pictures, "familia.png", is_directory=False, size=3072000)



    def _add_child(self, parent, name, is_directory=True, size=0):
        """Añade un hijo al nodo padre usando representación primer hijo/hermano"""
        new_node = FileSystemNode(name, is_directory, size)
        new_node.parent = parent
        
        if parent.first_child is None:
            parent.first_child = new_node
        else:
            # Buscar el último hermano
            sibling = parent.first_child
            while sibling.next_sibling is not None:
                sibling = sibling.next_sibling
            sibling.next_sibling = new_node
        
        return new_node

    def find_node(self, path):
        """Busca un nodo por su ruta completa"""
        if not path or path == self.root.name:
            return self.root
        
        # Normalizar la ruta
        path_parts = path.replace(self.root.name, "").strip("\\").split("\\")
        if path_parts == [""]:
            return self.root
        
        current = self.root
        
        for part in path_parts:
            if not part:  # saltar partes vacías
                continue
            
            found = False
            child = current.first_child
            
            while child is not None:
                if child.name == part:
                    current = child
                    found = True
                    break
                child = child.next_sibling
            
            if not found:
                return None
        
        return current

    def get_directory_contents(self, node):
        """Obtiene el contenido de un directorio"""
        if not node.is_directory:
            return []
        
        contents = []
        child = node.first_child
        
        while child is not None:
            contents.append(child)
            child = child.next_sibling
        
        return contents

    def calculate_directory_size(self, node):
        """Calcula el tamaño total de un directorio (recorrido postorden)"""
        if not node.is_directory:
            return node.size
        
        total_size = 0
        child = node.first_child
        
        while child is not None:
            if child.is_directory:
                total_size += self.calculate_directory_size(child)
            else:
                total_size += child.size
            child = child.next_sibling
        
        return total_size

    def get_full_path(self, node):
        """Obtiene la ruta completa de un nodo"""
        if node == self.root:
            return self.root.name
        
        path_parts = []
        current = node
        
        while current.parent is not None:
            path_parts.append(current.name)
            current = current.parent
        
        path_parts.append(self.root.name)
        path_parts.reverse()
        
        return "\\".join(path_parts)

    def search_files(self, filename, start_node=None):
        """Busca archivos por nombre en todo el sistema"""
        if start_node is None:
            start_node = self.root
        
        results = []
        self._search_recursive(start_node, filename.lower(), results)
        return results

    def _search_recursive(self, node, filename, results):
        """Búsqueda recursiva de archivos"""
        if filename in node.name.lower():
            results.append(node)
        
        child = node.first_child
        while child is not None:
            self._search_recursive(child, filename, results)
            child = child.next_sibling

    def create_directory(self, parent_path, dir_name):
        """Crea un nuevo directorio"""
        parent = self.find_node(parent_path)
        if parent and parent.is_directory:
            return self._add_child(parent, dir_name, is_directory=True)
        return None

    def create_file(self, parent_path, file_name, size=0):
        """Crea un nuevo archivo"""
        parent = self.find_node(parent_path)
        if parent and parent.is_directory:
            return self._add_child(parent, file_name, is_directory=False, size=size)
        return None


# ====================
# Tkinter + Bootstrap App
# ====================
class FileSystemApp:
    def __init__(self, root):
        self.filesystem = FileSystem()
        self.current_path = self.filesystem.root.name
        self.root = root
        self.root.title("Explorador de Sistema de Archivos")
        self.root.geometry("800x600")

        self._create_widgets()
        self._update_display()

    def _create_widgets(self):
        # Frame principal
        main_frame = tb.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)

        # Barra superior con ruta actual
        path_frame = tb.Frame(main_frame)
        path_frame.pack(fill=X, pady=(0, 10))

        tb.Label(path_frame, text="Ruta actual:", font=("Helvetica", 12)).pack(side=LEFT)
        self.path_label = tb.Label(path_frame, text=self.current_path, font=("Helvetica", 12, "bold"))
        self.path_label.pack(side=LEFT, padx=(10, 0))

        # Botones de navegación
        nav_frame = tb.Frame(main_frame)
        nav_frame.pack(fill=X, pady=(0, 10))

        self.back_button = tb.Button(nav_frame, text="← Atrás", bootstyle="info-outline", 
                                    command=self.go_back)
        self.back_button.pack(side=LEFT, padx=(0, 5))

        self.home_button = tb.Button(nav_frame, text="🏠 Inicio", bootstyle="info-outline", 
                                    command=self.go_home)
        self.home_button.pack(side=LEFT, padx=(0, 5))

        # Frame de búsqueda
        search_frame = tb.Frame(main_frame)
        search_frame.pack(fill=X, pady=(0, 10))

        tb.Label(search_frame, text="Buscar archivo:", font=("Helvetica", 10)).pack(side=LEFT)
        self.search_entry = tb.Entry(search_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=(10, 5))
        self.search_entry.bind("<KeyRelease>", self.search_files)

        self.search_button = tb.Button(search_frame, text="Buscar", bootstyle="success-outline",
                                      command=self.search_files)
        self.search_button.pack(side=LEFT)

        # Crear notebook para pestañas
        self.notebook = tb.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=YES)

        # Pestaña de explorador
        self.explorer_frame = tb.Frame(self.notebook)
        self.notebook.add(self.explorer_frame, text="Explorador")

        # TreeView para mostrar archivos
        self.tree = tb.Treeview(self.explorer_frame, columns=("size", "type", "date"), show="tree headings")
        self.tree.pack(fill=BOTH, expand=YES, side=LEFT)

        # Configurar columnas
        self.tree.heading("#0", text="Nombre")
        self.tree.heading("size", text="Tamaño")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("date", text="Fecha")

        self.tree.column("#0", width=300)
        self.tree.column("size", width=100)
        self.tree.column("type", width=100)
        self.tree.column("date", width=150)

        # Scrollbar para el TreeView
        scrollbar = tb.Scrollbar(self.explorer_frame, orient=VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind eventos
        self.tree.bind("<Double-1>", self.on_double_click)

        # Pestaña de resultados de búsqueda
        self.search_frame = tb.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Resultados de Búsqueda")

        self.search_tree = tb.Treeview(self.search_frame, columns=("path", "size", "type"), show="tree headings")
        self.search_tree.pack(fill=BOTH, expand=YES)

        self.search_tree.heading("#0", text="Nombre")
        self.search_tree.heading("path", text="Ruta Completa")
        self.search_tree.heading("size", text="Tamaño")
        self.search_tree.heading("type", text="Tipo")

        # Panel de información
        info_frame = tb.LabelFrame(main_frame, text="Información del Directorio", padding=10)
        info_frame.pack(fill=X, pady=(10, 0))

        self.info_label = tb.Label(info_frame, text="", font=("Helvetica", 10))
        self.info_label.pack()

    def _update_display(self):
        """Actualiza la visualización del explorador"""
        # Limpiar TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Actualizar etiqueta de ruta
        self.path_label.config(text=self.current_path)

        # Obtener nodo actual
        current_node = self.filesystem.find_node(self.current_path)
        if not current_node:
            return

        # Insertar los hijos en el TreeView
        for child in self.filesystem.get_directory_contents(current_node):
            size = self.filesystem.calculate_directory_size(child) if child.is_directory else child.size
            size_str = self._format_size(size)
            tipo = "Directorio" if child.is_directory else "Archivo"
            date_str = child.creation_date.strftime("%Y-%m-%d %H:%M:%S")
            self.tree.insert("", "end", text=child.name, values=(size_str, tipo, date_str))

        # Actualizar info del directorio actual
        dir_size = self.filesystem.calculate_directory_size(current_node)
        self.info_label.config(text=f"Elementos: {len(self.filesystem.get_directory_contents(current_node))} | "
                                    f"Tamaño total: {self._format_size(dir_size)}")

    def _format_size(self, size):
        """Formatea tamaño en bytes a KB, MB, GB"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    def go_back(self):
        """Navegar hacia atrás"""
        if self.current_path == self.filesystem.root.name:
            return
        current_node = self.filesystem.find_node(self.current_path)
        if current_node and current_node.parent:
            self.current_path = self.filesystem.get_full_path(current_node.parent)
            self._update_display()

    def go_home(self):
        """Ir al directorio raíz"""
        self.current_path = self.filesystem.root.name
        self._update_display()

    def on_double_click(self, event):
        """Abrir carpeta con doble clic"""
        item_id = self.tree.focus()
        if not item_id:
            return
        nombre = self.tree.item(item_id, "text")

        current_node = self.filesystem.find_node(self.current_path)
        if not current_node:
            return

        for child in self.filesystem.get_directory_contents(current_node):
            if child.name == nombre:
                if child.is_directory:
                    self.current_path = self.filesystem.get_full_path(child)
                    self._update_display()
                break

    def search_files(self, event=None):
        """Ejecuta la búsqueda"""
        query = self.search_entry.get().strip().lower()
        if not query:
            return

        # Limpiar resultados anteriores
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        # Buscar en todo el sistema
        results = self.filesystem.search_files(query)

        for node in results:
            size = self.filesystem.calculate_directory_size(node) if node.is_directory else node.size
            size_str = self._format_size(size)
            tipo = "Directorio" if node.is_directory else "Archivo"
            full_path = self.filesystem.get_full_path(node)
            self.search_tree.insert("", "end", text=node.name,
                                    values=(full_path, size_str, tipo))


# ====================
# MAIN
# ====================
if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    FileSystemApp(app)
    app.mainloop()
