import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ====================
# Trie para palabras prohibidas
# ====================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class WordFilterTrie:
    def __init__(self):
        self.root = TrieNode()

    def insertar_palabra(self, palabra: str):
        node = self.root
        for char in palabra.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def censurar_mensaje(self, mensaje: str) -> str:
        """Reemplaza palabras prohibidas en el mensaje con asteriscos"""
        resultado = list(mensaje)
        mensaje_lower = mensaje.lower()

        for i in range(len(mensaje_lower)):
            node = self.root
            j = i
            while j < len(mensaje_lower) and mensaje_lower[j] in node.children:
                node = node.children[mensaje_lower[j]]
                if node.is_end_of_word:
                    # Censurar desde i hasta j
                    for k in range(i, j + 1):
                        resultado[k] = "*"
                j += 1

        return "".join(resultado)


# ====================
# Tkinter App
# ====================
class ChatFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Censura de Palabras en Chat")
        self.root.geometry("600x400")

        self.trie = WordFilterTrie()
        self._crear_widgets()
        self.cargar_ejemplo()  # Cargar palabras prohibidas automáticamente

    def _crear_widgets(self):
        frame = tb.Frame(self.root, padding=10)
        frame.pack(fill=BOTH, expand=YES)

       
       

        # Entrada de mensaje
        tb.Label(frame, text="Escribe tu mensaje:", font=("Helvetica", 11)).pack(anchor=W)
        self.entry = tb.Entry(frame, width=60)
        self.entry.pack(anchor=W, pady=(5, 15))

        # Botón enviar
        self.send_btn = tb.Button(frame, text="Enviar", bootstyle="success-outline",
                                  command=self.enviar_mensaje)
        self.send_btn.pack(anchor=W, pady=(0, 15))

        # Salida del mensaje censurado
        tb.Label(frame, text="Mensaje procesado:", font=("Helvetica", 11, "bold")).pack(anchor=W)
        self.output_label = tb.Label(frame, text="", font=("Helvetica", 12), wraplength=500, justify=LEFT)
        self.output_label.pack(anchor=W, pady=(5, 15))

    def cargar_ejemplo(self):
        """Carga una lista negra de ejemplo"""
        palabras_prohibidas = [
            "prohibido", "ofensivo", "malo", "tonto", "estupido",
            "grosero", "insulto", "feo", "basura", "violencia",
            "odio", "asqueroso", "tonto", "ignorante", "vulgar",
            "mentiroso", "abusivo", "inutil", "idiota", "imbecil",
            "cretino", "necio", "tarado", "estupida", "maldito",
            "pendejo", "gilipollas", "cabron", "maricon",
            "zorra", "mierda", "carajo", "joder", "chingar",
            "coño", "boludo", "pelotudo", "pendeja", "idiotas",
            "imbeciles", "cretinos", "necios", "tarados", "estupidas",
            "malditos", "pendejos", "gilipollas", "cabrones",
            "maricones", "zorras", "mierdas", "carajos", "jodiendo",
            "chingando", "coños", "boludos", "pelotudos", "pendejas"  # me quede sin palabras, y la IA no me ayuda :(, cosas de ser family friendly :[
        ]
        for palabra in palabras_prohibidas:
            self.trie.insertar_palabra(palabra)
        self.output_label.config(text=" Palabras prohibidas cargadas")

    def enviar_mensaje(self):
        mensaje = self.entry.get()
        if not mensaje:
            self.output_label.config(text=" Escribe un mensaje primero")
            return
        censurado = self.trie.censurar_mensaje(mensaje)
        self.output_label.config(text=censurado)


# ====================
# MAIN
# ====================
if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    ChatFilterApp(app)
    app.mainloop()
