import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# ====================
# Clase Nodo y Árbol N-ario
# ====================
class EmployeeNode:
    def __init__(self, name):
        self.name = name
        self.children = []   # subordinados directos
        self.parent = None   # referencia al jefe

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


class OrgChart:
    def __init__(self, ceo_name="CEO"):
        self.root = EmployeeNode(ceo_name)

    def find_employee(self, node, name):
        if node.name.lower() == name.lower():
            return node
        for child in node.children:
            found = self.find_employee(child, name)
            if found:
                return found
        return None

    def add_employee(self, boss_name, employee_name):
        boss = self.find_employee(self.root, boss_name)
        if boss:
            boss.add_child(EmployeeNode(employee_name))

    def get_subordinates(self, name):
        employee = self.find_employee(self.root, name)
        result = []
        if employee:
            self._collect_subordinates(employee, result)
        return result

    def _collect_subordinates(self, node, result):
        for child in node.children:
            result.append(child.name)
            self._collect_subordinates(child, result)

    def get_chain_of_command(self, name):
        employee = self.find_employee(self.root, name)
        chain = []
        while employee and employee.parent:
            chain.append(employee.parent.name)
            employee = employee.parent
        return chain


# ====================
# Tkinter + Bootstrap App
# ====================
class OrgChartApp:
    def __init__(self, root, chart):
        self.chart = chart
        self.root = root
        self.root.title("Organigrama Empresarial")

        frame = tb.Frame(root, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        label = tb.Label(frame, text="Consulta jerárquica:", font=("Helvetica", 14))
        label.pack(pady=10)

        # Caja de entrada
        self.entry = tb.Entry(frame, width=40, bootstyle="info")
        self.entry.pack(pady=5)

        # Botones de consulta
        btn1 = tb.Button(frame, text="Subordinados", bootstyle="success-outline",
                         command=self.show_subordinates)
        btn1.pack(pady=5)

        btn2 = tb.Button(frame, text="Cadena de mando", bootstyle="warning-outline",
                         command=self.show_chain)
        btn2.pack(pady=5)

        btn3 = tb.Button(frame, text="Mostrar Árbol", bootstyle="primary-outline",
                         command=self.show_tree)
        btn3.pack(pady=5)

        # Área de resultados
        self.text = tk.Text(frame, width=50, height=8, font=("Helvetica", 12))
        self.text.pack(pady=10)

        # Canvas para organigrama
        self.canvas = tk.Canvas(frame, width=1000, height=600, bg="white")
        self.canvas.pack(pady=10)

    # ====== Funciones de consulta ======
    def show_subordinates(self):
        name = self.entry.get().strip()
        subs = self.chart.get_subordinates(name)
        self.text.delete("1.0", tk.END)
        if subs:
            self.text.insert(tk.END, f"Subordinados de {name}:\n" + "\n".join(subs))
        else:
            self.text.insert(tk.END, f"No se encontraron subordinados de {name}.")

    def show_chain(self):
        name = self.entry.get().strip()
        chain = self.chart.get_chain_of_command(name)
        self.text.delete("1.0", tk.END)
        if chain:
            self.text.insert(tk.END, f"Cadena de mando de {name}:\n" + " → ".join(chain))
        else:
            self.text.insert(tk.END, f"{name} es el CEO o no tiene superiores.")

    # ====== Dibujar organigrama ======
    def show_tree(self):
        self.canvas.delete("all")
        self._draw_node(self.chart.root, 500, 50, 400)

    def _draw_node(self, node, x, y, x_offset):
        box_width, box_height = 120, 40

        # Dibujar rectángulo (caja del empleado)
        self.canvas.create_rectangle(x - box_width/2, y - box_height/2,
                                     x + box_width/2, y + box_height/2,
                                     fill="skyblue", outline="black")
        self.canvas.create_text(x, y, text=node.name, font=("Helvetica", 10, "bold"))

        # Dibujar hijos
        if node.children:
            step = x_offset / max(len(node.children), 1)
            new_x = x - x_offset/2 + step/2
            for child in node.children:
                child_x, child_y = new_x, y + 100

                # Línea: de abajo del padre al centro arriba del hijo
                self.canvas.create_line(x, y + box_height/2,
                                        child_x, child_y - box_height/2,
                                        width=2)

                # Llamada recursiva
                self._draw_node(child, child_x, child_y, x_offset/2)
                new_x += step


# ====================
# Main
# ====================
if __name__ == "__main__":
    org = OrgChart("CEO")
    org.add_employee("CEO", "Vicepresidente 1")
    org.add_employee("CEO", "Vicepresidente 2")
    org.add_employee("Vicepresidente 1", "Director A")
    org.add_employee("Vicepresidente 1", "Director B")
    org.add_employee("Director A", "Jefe de Área 1")
    org.add_employee("Director A", "Jefe de Área 2")
    org.add_employee("Vicepresidente 2", "Director C")

    app = tb.Window(themename="flatly")
    OrgChartApp(app, org)
    app.mainloop()
