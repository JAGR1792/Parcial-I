import os
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ====================
# Clase Trie y Nodo
# ====================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.frequency = 0  # contador de frecuencia

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.frequency += 1

    def _find_words_from_node(self, node, prefix, suggestions):
        if node.is_end_of_word:
            suggestions.append((prefix, node.frequency))
        for char, child in node.children.items():
            self._find_words_from_node(child, prefix + char, suggestions)

    def suggest(self, prefix: str):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        suggestions = []
        self._find_words_from_node(node, prefix, suggestions)
        # ordenar por frecuencia (más populares primero)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [w for w, _ in suggestions]



class AutocompleteApp:
    def __init__(self, root, trie):
        self.trie = trie
        self.root = root
        self.root.title("Motor de Búsqueda (Trie)")

        # Frame principal
        frame = tb.Frame(root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        # Etiqueta
        label = tb.Label(frame, text="Escribe tu consulta:", font=("Helvetica", 14))
        label.pack(pady=10)

        # Caja de texto
        self.entry = tb.Entry(frame, width=50, bootstyle="info")
        self.entry.pack(pady=5)
        self.entry.bind("<KeyRelease>", self.update_suggestions)

        # Listbox de sugerencias (tkinter puro)
        self.listbox = tk.Listbox(frame, width=50, height=6, font=("Helvetica", 12),
                                  bg="white", fg="#333", selectbackground="#cce5ff")
        self.listbox.pack(pady=10)

        # Botón buscar
        self.search_button = tb.Button(frame, text="Buscar",
                                       bootstyle="success-outline",
                                       command=self.confirm_search)
        self.search_button.pack(pady=5)

    def update_suggestions(self, event=None):
        prefix = self.entry.get()
        self.listbox.delete(0, tk.END)

        if prefix:
            suggestions = self.trie.suggest(prefix)
            for word in suggestions:
                self.listbox.insert(tk.END, word)

    def confirm_search(self):
        query = self.entry.get()
        if query:
            self.trie.insert(query)
            self.entry.delete(0, tk.END)
            self.listbox.delete(0, tk.END)


# ====================
# Main
# ====================
if __name__ == "__main__":
    trie = Trie()

    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONSULTAS_PATH = os.path.join(BASE_DIR, "consultas.txt")

    # 1. Cargar historial inicial desde consultas.txt (construcción offline)
    try:
        with open(CONSULTAS_PATH, "r", encoding="utf-8") as f:
            for linea in f:
                consulta = linea.strip()
                if consulta:
                    trie.insert(consulta)
        print(f"✔ Consultas cargadas desde {CONSULTAS_PATH}")
    except FileNotFoundError:
        print(f"⚠ No se encontró 'consultas.txt' en {BASE_DIR}. Se usará un diccionario vacío.")

    # 2. Iniciar la app
    app = tb.Window(themename="flatly")  # prueba otros: "cyborg", "superhero", "darkly"
    AutocompleteApp(app, trie)
    app.mainloop()
