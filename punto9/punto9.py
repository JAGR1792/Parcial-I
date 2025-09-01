import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ====================
# Clase Nodo AST (N-ario)
# ====================
class ASTNode:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo       # Ej: "Declaración", "Identificador", "Operación"
        self.valor = valor     # Ej: "x", "=", "+", número
        self.hijos = []        # Hijos del nodo

    def add_child(self, nodo):
        self.hijos.append(nodo)

    def __repr__(self, nivel=0):
        sangria = "  " * nivel
        rep = f"{sangria}{self.tipo}: {self.valor}\n"
        for hijo in self.hijos:
            rep += hijo.__repr__(nivel + 1)
        return rep


# ====================
# Parser simple para construir AST
# ====================
def construir_ast(codigo: str):
    """
    Construye un AST muy simple para sentencias tipo:
    var x = a + 5;
    """
    tokens = codigo.replace(";", "").split()

    if len(tokens) < 5 or tokens[0] != "var":
        return ASTNode("Error", "Sintaxis no soportada")

    # Nodo raíz: Declaración de variable
    declaracion = ASTNode("DeclaraciónDeVariable")

    # Nombre de variable
    nombre = ASTNode("Identificador", tokens[1])

    # Asignación
    asignacion = ASTNode("Asignación", "=")

    # Verificar si hay operación
    if "+" in tokens:
        idx = tokens.index("+")
        suma = ASTNode("Operación", "+")
        suma.add_child(ASTNode("Identificador", tokens[idx - 1]))
        suma.add_child(ASTNode("Número", tokens[idx + 1]))
        asignacion.add_child(suma)
    else:
        # Caso simple: asignación directa
        asignacion.add_child(ASTNode("Valor", tokens[3]))

    declaracion.add_child(nombre)
    declaracion.add_child(asignacion)

    return declaracion


# ====================
# Recorridos
# ====================
def recorrido_postorden(nodo, resultado):
    for hijo in nodo.hijos:
        recorrido_postorden(hijo, resultado)
    resultado.append(f"[{nodo.tipo}] {nodo.valor}")

def recorrido_preorden(nodo, resultado):
    resultado.append(f"[{nodo.tipo}] {nodo.valor}")
    for hijo in nodo.hijos:
        recorrido_preorden(hijo, resultado)


# ====================
# Tkinter App
# ====================
class ASTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Sintáctico (AST)")

        frame = tb.Frame(root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        label = tb.Label(frame, text="Introduce una línea de código:", font=("Helvetica", 14))
        label.pack(pady=10)

        self.entry = tb.Entry(frame, width=50, bootstyle="info")
        self.entry.pack(pady=5)

        self.textbox = tk.Text(frame, width=70, height=15, font=("Courier", 11),
                               bg="white", fg="black")
        self.textbox.pack(pady=10)

        self.generate_button = tb.Button(frame, text="Generar AST", bootstyle="success-outline",
                                         command=self.generar_ast)
        self.generate_button.pack(pady=5)

    def generar_ast(self):
        codigo = self.entry.get()
        ast = construir_ast(codigo)

        # Mostrar AST textual
        self.textbox.delete("1.0", tk.END)
        self.textbox.insert(tk.END, "=== AST Construido ===\n")
        self.textbox.insert(tk.END, ast.__repr__())

        # Recorridos
        postorden = []
        preorden = []
        recorrido_postorden(ast, postorden)
        recorrido_preorden(ast, preorden)

        self.textbox.insert(tk.END, "\n=== Recorrido Postorden (Semántico) ===\n")
        self.textbox.insert(tk.END, "\n".join(postorden))

        self.textbox.insert(tk.END, "\n\n=== Recorrido Preorden (Generación de Código) ===\n")
        self.textbox.insert(tk.END, "\n".join(preorden))


# ====================
# Main
# ====================
if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    ASTApp(app)
    app.mainloop()
 
