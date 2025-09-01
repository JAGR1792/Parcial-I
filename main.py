import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import subprocess
import sys
import os

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal - Proyecto Puntos 1 a 10")

        frame = tb.Frame(root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        label = tb.Label(frame, text="Selecciona un punto para ejecutar:", font=("Helvetica", 16, "bold"))
        label.pack(pady=10)

        # Crear botones del 1 al 10
        for i in range(1, 11):
            btn = tb.Button(frame, text=f"Punto {i}", bootstyle="primary-outline",
                            command=lambda n=i: self.ejecutar_punto(n))
            btn.pack(pady=5, fill=X)

        # Botón salir
        btn_salir = tb.Button(frame, text="Salir", bootstyle="danger-outline", command=self.root.quit)
        btn_salir.pack(pady=10, fill=X)

    def ejecutar_punto(self, numero):
        """Ejecuta el archivo puntoX/puntoX.py en un proceso separado"""
        carpeta = f"punto{numero}"
        archivo = f"punto{numero}.py"
        ruta = os.path.join(carpeta, archivo)

        if os.path.exists(ruta):
            # Usamos el mismo intérprete de Python
            subprocess.Popen([sys.executable, ruta])
        else:
            tk.messagebox.showerror("Error", f"No se encontró {ruta}")


# ====================
# Main
# ====================
if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    MainMenu(app)
    app.mainloop()
