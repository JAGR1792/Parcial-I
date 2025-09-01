import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ====================
# Trie
# ====================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

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


# ====================
# Algoritmo de búsqueda en sopa de letras
# ====================
def buscar_palabras(grid, palabras):
    filas, cols = len(grid), len(grid[0])
    trie = Trie()
    for palabra in palabras:
        trie.insert(palabra)

    direcciones = [(-1,0), (1,0), (0,-1), (0,1),
                   (-1,-1), (-1,1), (1,-1), (1,1)]

    encontradas = set()

    for i in range(filas):
        for j in range(cols):
            for dx, dy in direcciones:
                x, y = i, j
                palabra_actual = ""
                nodo = trie.root
                while 0 <= x < filas and 0 <= y < cols:
                    letra = grid[x][y]
                    if letra not in nodo.children:
                        break
                    nodo = nodo.children[letra]
                    palabra_actual += letra
                    if nodo.is_end_of_word:
                        encontradas.add(palabra_actual)
                    x += dx
                    y += dy
    return encontradas


# ====================
# Tkinter App
# ====================
class SopaDeLetrasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sopa de Letras con Trie")

        frame = tb.Frame(root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        label1 = tb.Label(frame, text="Palabras a buscar (separadas por coma):", font=("Helvetica", 12))
        label1.pack(pady=5)

        self.entry_words = tb.Entry(frame, width=50, bootstyle="info")
        self.entry_words.insert(0, "CASA,MAR,SOL,AVE")
        self.entry_words.pack(pady=5)

        label2 = tb.Label(frame, text="Cuadrícula de la sopa (usar espacios):", font=("Helvetica", 12))
        label2.pack(pady=5)

        # Caja para escribir la sopa
        self.text_grid = tk.Text(frame, width=40, height=8, font=("Courier", 12),
                                 bg="white", fg="black")
        self.text_grid.pack(pady=5)

        # Ejemplo de sopa
        ejemplo = """
        M A R X C V B N M S 
        X V B N M A S D F G
        H J K L Ñ Z Q W E R
        T Y U I O P A S D F
        G H J K L Z X O V B
        N M Q W E R T L U I
        O P A S D F G H J K
        L Z X C V B N M Q W
        E R T Y U I O P A S
        D F G H J K L E V A""" # EVA = AVE
        self.text_grid.insert("1.0", ejemplo)

        self.btn_search = tb.Button(frame, text="Buscar Palabras", bootstyle="success-outline",
                                    command=self.buscar)
        self.btn_search.pack(pady=10)

        self.listbox = tk.Listbox(frame, width=40, height=8, font=("Helvetica", 12),
                                  bg="white", fg="#333", selectbackground="#cce5ff")
        self.listbox.pack(pady=10)

    def buscar(self):
        # Obtener lista de palabras
        palabras = [p.strip().upper() for p in self.entry_words.get().split(",")]

        # Obtener cuadrícula
        texto = self.text_grid.get("1.0", tk.END).strip().split("\n")
        grid = [fila.split() for fila in texto]

        # Ejecutar búsqueda
        encontradas = buscar_palabras(grid, palabras)

        # Mostrar resultados
        self.listbox.delete(0, tk.END)
        if encontradas:
            for palabra in encontradas:
                self.listbox.insert(tk.END, palabra)
        else:
            self.listbox.insert(tk.END, "No se encontró ninguna palabra.")

if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    SopaDeLetrasApp(app)
    app.mainloop()
