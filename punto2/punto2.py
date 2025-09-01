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


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        """Inserta una palabra en el Trie"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word: str) -> bool:
        """Verifica si una palabra existe en el Trie"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    
    def _buscar_palabras_desde_nodo(self, node, prefix, suggestions):
        """Recorrido DFS para recolectar palabras completas desde un nodo"""
        if node.is_end_of_word:
            suggestions.append(prefix)
        for char, child in node.children.items():
            self._buscar_palabras_desde_nodo(child, prefix + char, suggestions)

    def sugerir_correcciones(self, palabra: str):
        """
        Genera sugerencias para una palabra incorrecta usando heurísticas simples:
        - Eliminar un carácter
        - Sustituir un carácter por otro
        - Añadir un carácter en cada posición
        """
        sugerencias = set()
        alfabeto = "abcdefghijklmnopqrstuvwxyzáéíóúñ"

        # 1. Eliminar un carácter
        for i in range(len(palabra)):
            nueva = palabra[:i] + palabra[i+1:]
            if self.search(nueva):
                sugerencias.add(nueva)

        # 2. Sustituir un carácter
        for i in range(len(palabra)):
            for c in alfabeto:
                nueva = palabra[:i] + c + palabra[i+1:]
                if self.search(nueva):
                    sugerencias.add(nueva)

        # 3. Insertar un carácter
        for i in range(len(palabra) + 1):
            for c in alfabeto:
                nueva = palabra[:i] + c + palabra[i:]
                if self.search(nueva):
                    sugerencias.add(nueva)

        return list(sugerencias)


# ====================
# Tkinter + Bootstrap App
# ====================
class SpellCheckerApp:
    def __init__(self, root, trie):
        self.trie = trie
        self.root = root
        self.root.title("Verificador Ortográfico (Trie)")

        frame = tb.Frame(root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        label = tb.Label(frame, text="Escribe una palabra:", font=("Helvetica", 14))
        label.pack(pady=10)

        self.entry = tb.Entry(frame, width=40, bootstyle="info")
        self.entry.pack(pady=5)

        self.check_button = tb.Button(frame, text="Verificar", bootstyle="success-outline",
                                      command=self.verificar_palabra)
        self.check_button.pack(pady=5)

        self.result_label = tb.Label(frame, text="", font=("Helvetica", 12))
        self.result_label.pack(pady=10)

        self.suggestions_box = tk.Listbox(frame, width=40, height=6, font=("Helvetica", 12),
                                          bg="white", fg="#333", selectbackground="#cce5ff")
        self.suggestions_box.pack(pady=10)

    # --------------------
    # FUNCIONES NUEVAS EN ESPAÑOL
    # --------------------
    def verificar_palabra(self):
        """Verifica si la palabra escrita está en el diccionario"""
        palabra = self.entry.get().lower().strip()
        self.suggestions_box.delete(0, tk.END)

        if not palabra:
            self.result_label.config(text="⚠ Escribe una palabra.", foreground="orange")
            return

        if self.trie.search(palabra):
            self.result_label.config(text=f" '{palabra}' es correcta.", foreground="green")
        else:
            self.result_label.config(text=f" '{palabra}' no está en el diccionario.", foreground="red")
            sugerencias = self.trie.sugerir_correcciones(palabra)
            for s in sugerencias:
                self.suggestions_box.insert(tk.END, s)


# ====================
# Main
# ====================
if __name__ == "__main__":
    trie = Trie()

    # Cargar un diccionario básico desde archivo
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DICCIONARIO_PATH = os.path.join(BASE_DIR, "diccionario.txt")

    try:
        with open(DICCIONARIO_PATH, "r", encoding="utf-8") as f:
            for linea in f:
                palabra = linea.strip().lower()
                if palabra:
                    trie.insert(palabra)
        print(f"✔ Diccionario cargado desde {DICCIONARIO_PATH}")
    except FileNotFoundError:
        print(" No esta cargando el diccionario JORGE HAZ ALGO")

        # Palabras de ejemplo
        for w in ["árbol", "perro", "gato", "casa", "programa", "inteligencia", "artificial"]:
            trie.insert(w)

    app = tb.Window(themename="flatly")
    SpellCheckerApp(app, trie)
    app.mainloop()
