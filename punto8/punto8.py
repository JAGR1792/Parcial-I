import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches
import numpy as np

# ====================
# Clase Trie y Nodo
# ====================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_line = False
        self.stats = {"blancas": 0, "negras": 0, "tablas": 0}
        self.opening_name = None  # nombre de apertura

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, moves: list, resultado=None, opening_name=None):
        node = self.root
        for move in moves:
            if move not in node.children:
                node.children[move] = TrieNode()
            node = node.children[move]
        node.is_end_of_line = True
        if resultado:
            node.stats[resultado] += 1
        if opening_name:
            node.opening_name = opening_name

    def find_node(self, moves: list):
        node = self.root
        for move in moves:
            if move not in node.children:
                return None
            node = node.children[move]
        return node

    def continuations(self, moves: list):
        node = self.find_node(moves)
        if not node:
            return []
        return [(move, child.stats, child.opening_name) for move, child in node.children.items()]


# ====================
# Función de dibujo mejorada con matplotlib
# ====================
def calculate_tree_positions(node, depth=0, position=0):
    """
    Calcula las posiciones de todos los nodos del árbol para evitar solapamientos.
    Retorna un diccionario con las posiciones y el ancho total del subárbol.
    """
    positions = {}
    
    if not node.children:
        # Nodo hoja
        positions[id(node)] = (position, depth)
        return positions, 1
    
    # Procesar hijos
    child_positions = {}
    total_width = 0
    current_pos = position
    
    for move, child in node.children.items():
        child_pos, child_width = calculate_tree_positions(child, depth + 1, current_pos)
        child_positions.update(child_pos)
        current_pos += child_width
        total_width += child_width
    
    # Posicionar el nodo padre en el centro de sus hijos
    if node.children:
        child_x_positions = [pos[0] for node_id, pos in child_positions.items() 
                           if any(id(child) == node_id for child in node.children.values())]
        if child_x_positions:
            center_x = (min(child_x_positions) + max(child_x_positions)) / 2
        else:
            center_x = position
    else:
        center_x = position
    
    positions[id(node)] = (center_x, depth)
    positions.update(child_positions)
    
    return positions, total_width

def plot_tree_improved(trie, title="Árbol de Aperturas", max_depth=4):
    """
    Dibuja el árbol con una distribución mejorada de nodos.
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.axis("off")
    
    # Calcular posiciones
    positions, _ = calculate_tree_positions(trie.root)
    
    # Escalas para mejorar la visualización
    x_scale = 3
    y_scale = -2
    
    # Dibujar conexiones primero
    def draw_connections(node, current_depth=0):
        if current_depth >= max_depth:
            return
            
        node_pos = positions.get(id(node))
        if not node_pos:
            return
            
        x, y = node_pos[0] * x_scale, node_pos[1] * y_scale
        
        for move, child in node.children.items():
            child_pos = positions.get(id(child))
            if child_pos and child_pos[1] <= max_depth:
                child_x, child_y = child_pos[0] * x_scale, child_pos[1] * y_scale
                
                # Línea de conexión
                ax.plot([x, child_x], [y - 0.4, child_y + 0.4], 
                       color='#2E86C1', linewidth=2, alpha=0.7)
                
                # Etiqueta del movimiento
                mid_x, mid_y = (x + child_x) / 2, (y + child_y) / 2
                ax.text(mid_x, mid_y, move, fontsize=10, fontweight='bold',
                       ha='center', va='center', 
                       bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#2E86C1", alpha=0.8))
                
                draw_connections(child, current_depth + 1)
    
    # Dibujar nodos
    def draw_nodes(node, current_depth=0):
        if current_depth >= max_depth:
            return
            
        node_pos = positions.get(id(node))
        if not node_pos:
            return
            
        x, y = node_pos[0] * x_scale, node_pos[1] * y_scale
        
        # Contenido del nodo
        if current_depth == 0:
            label = "INICIO"
            color = "#E8F6F3"
            edge_color = "#27AE60"
        else:
            label = ""
            color = "#FEF9E7"
            edge_color = "#F39C12"
        
        # Mostrar estadísticas si existen
        stats = node.stats
        if any(stats.values()):
            stats_text = f"♔:{stats['blancas']} ♛:{stats['negras']} =:{stats['tablas']}"
            label = f"{label}\n{stats_text}" if label else stats_text
        
        # Mostrar nombre de apertura
        if node.opening_name:
            label = f"{label}\n📚 {node.opening_name}" if label else f"📚 {node.opening_name}"
        
        if not label.strip():
            label = "•"
        
        # Ajustar tamaño del nodo según el contenido
        bbox_props = dict(boxstyle="round,pad=0.5", fc=color, ec=edge_color, linewidth=2)
        ax.text(x, y, label, ha='center', va='center', fontsize=9,
               bbox=bbox_props, wrap=True)
        
        # Recursión para hijos
        for move, child in node.children.items():
            draw_nodes(child, current_depth + 1)
    
    # Dibujar el árbol
    draw_connections(trie.root)
    draw_nodes(trie.root)
    
    # Ajustar límites del gráfico
    all_x = [pos[0] * x_scale for pos in positions.values()]
    all_y = [pos[1] * y_scale for pos in positions.values()]
    
    if all_x and all_y:
        margin = 2
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
    
    # Leyenda
    legend_elements = [
        mpatches.Patch(color='#E8F6F3', label='Nodo Inicial'),
        mpatches.Patch(color='#FEF9E7', label='Posiciones'),
        mpatches.Patch(color='white', label='Movimientos')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    plt.show()


# ====================
# Función para mostrar estadísticas
# ====================
def plot_opening_stats(trie, title="Estadísticas de Aperturas"):
    """
    Muestra un gráfico de barras con las estadísticas de las aperturas.
    """
    def collect_openings(node, openings_data=None):
        if openings_data is None:
            openings_data = {}
        
        if node.opening_name and any(node.stats.values()):
            name = node.opening_name
            if name in openings_data:
                for key in node.stats:
                    openings_data[name][key] += node.stats[key]
            else:
                openings_data[name] = node.stats.copy()
        
        for child in node.children.values():
            collect_openings(child, openings_data)
        
        return openings_data
    
    openings_data = collect_openings(trie.root)
    
    if not openings_data:
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'No hay datos de aperturas para mostrar', 
                ha='center', va='center', fontsize=14)
        plt.title(title)
        plt.axis('off')
        plt.show()
        return
    
    # Preparar datos para el gráfico
    names = list(openings_data.keys())
    blancas = [openings_data[name]['blancas'] for name in names]
    negras = [openings_data[name]['negras'] for name in names]
    tablas = [openings_data[name]['tablas'] for name in names]
    
    # Crear gráfico de barras apiladas
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(names))
    width = 0.6
    
    p1 = ax.bar(x, blancas, width, label='Victorias Blancas', color='#F8F9FA', edgecolor='black')
    p2 = ax.bar(x, negras, width, bottom=blancas, label='Victorias Negras', color='#343A40', edgecolor='black')
    p3 = ax.bar(x, tablas, width, bottom=np.array(blancas) + np.array(negras), 
                label='Tablas', color='#6C757D', edgecolor='black')
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Aperturas', fontsize=12)
    ax.set_ylabel('Número de Partidas', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.legend()
    
    # Añadir valores en las barras
    for i, (b, n, t) in enumerate(zip(blancas, negras, tablas)):
        total = b + n + t
        if total > 0:
            ax.text(i, total + total*0.01, str(total), ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.show()


# ====================
# Tkinter + Bootstrap App
# ====================
class ChessBookApp:
    def __init__(self, root, trie_white, trie_black):
        self.trie_white = trie_white
        self.trie_black = trie_black
        
        # Configurar la aplicación
        self.root = root
        self.root.title("📚 Libro de Aperturas de Ajedrez")
        
        # Frame principal con mejor diseño
        main_frame = tb.Frame(root, padding=30)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Título
        title_label = tb.Label(main_frame, text="♔ Libro de Aperturas de Ajedrez ♛", 
                              font=("Helvetica", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para entrada
        input_frame = tb.LabelFrame(main_frame, text="Secuencia de Jugadas", padding=20)
        input_frame.pack(fill=X, pady=10)
        
        info_label = tb.Label(input_frame, text="Introduce las jugadas separadas por espacios (ej: e4 e5 Nf3):")
        info_label.pack(anchor=W, pady=(0, 10))
        
        self.entry = tb.Entry(input_frame, width=60, bootstyle="info")
        self.entry.pack(fill=X, pady=5)
        
        # Frame para selección de color
        color_frame = tb.LabelFrame(main_frame, text="Perspectiva", padding=15)
        color_frame.pack(fill=X, pady=10)
        
        self.color_var = tk.StringVar(value="blancas")
        color_buttons_frame = tb.Frame(color_frame)
        color_buttons_frame.pack()
        
        rb1 = tb.Radiobutton(color_buttons_frame, text="♔ Blancas", 
                            variable=self.color_var, value="blancas", bootstyle="info")
        rb2 = tb.Radiobutton(color_buttons_frame, text="♛ Negras", 
                            variable=self.color_var, value="negras", bootstyle="secondary")
        rb1.pack(side=LEFT, padx=20)
        rb2.pack(side=LEFT, padx=20)
        
        # Frame para resultados
        results_frame = tb.LabelFrame(main_frame, text="Continuaciones Posibles", padding=15)
        results_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Scrollbar para el Listbox
        listbox_frame = tb.Frame(results_frame)
        listbox_frame.pack(fill=BOTH, expand=YES)
        
        scrollbar = tb.Scrollbar(listbox_frame, orient=VERTICAL)
        self.listbox = tk.Listbox(listbox_frame, width=80, height=12, font=("Consolas", 10),
                                  bg="#F8F9FA", fg="#212529", selectbackground="#007BFF",
                                  yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Frame para botones
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X, pady=15)
        
        self.search_button = tb.Button(button_frame, text="🔍 Buscar Continuaciones", 
                                      bootstyle="success", command=self.show_continuations)
        self.search_button.pack(side=LEFT, padx=10, expand=YES, fill=X)
        
        self.show_tree_button = tb.Button(button_frame, text="🌳 Mostrar Árbol", 
                                         bootstyle="info", command=self.show_tree)
        self.show_tree_button.pack(side=LEFT, padx=10, expand=YES, fill=X)
        
        self.stats_button = tb.Button(button_frame, text="📊 Estadísticas", 
                                     bootstyle="warning", command=self.show_stats)
        self.stats_button.pack(side=LEFT, padx=10, expand=YES, fill=X)
        
        # Vincular Enter a la búsqueda
        self.entry.bind('<Return>', lambda e: self.show_continuations())

    def show_continuations(self):
        sequence = self.entry.get().strip().split()
        self.listbox.delete(0, tk.END)
        
        if not sequence or sequence == ['']:
            self.listbox.insert(tk.END, "⚠️ Introduce una secuencia de jugadas válida.")
            return
        
        trie = self.trie_white if self.color_var.get() == "blancas" else self.trie_black
        continuations = trie.continuations(sequence)
        
        if continuations:
            self.listbox.insert(tk.END, f"📍 Continuaciones para: {' '.join(sequence)}")
            self.listbox.insert(tk.END, "─" * 70)
            
            for i, (move, stats, opening) in enumerate(continuations, 1):
                total = sum(stats.values())
                if total > 0:
                    blancas_pct = (stats['blancas'] / total) * 100
                    negras_pct = (stats['negras'] / total) * 100
                    tablas_pct = (stats['tablas'] / total) * 100
                    
                    apertura = f" 📚 {opening}" if opening else ""
                    stats_text = f"♔{stats['blancas']} ({blancas_pct:.1f}%) ♛{stats['negras']} ({negras_pct:.1f}%) ={stats['tablas']} ({tablas_pct:.1f}%)"
                else:
                    apertura = f" 📚 {opening}" if opening else ""
                    stats_text = "Sin estadísticas"
                
                texto = f"{i:2d}. {move:8s} → {stats_text}{apertura}"
                self.listbox.insert(tk.END, texto)
        else:
            self.listbox.insert(tk.END, "❌ No hay continuaciones registradas para esta secuencia.")
            self.listbox.insert(tk.END, "")
            self.listbox.insert(tk.END, "💡 Sugerencias:")
            self.listbox.insert(tk.END, "   • Verifica la notación de las jugadas")
            self.listbox.insert(tk.END, "   • Prueba con una secuencia más corta")
            self.listbox.insert(tk.END, "   • Cambia la perspectiva (Blancas/Negras)")

    def show_tree(self):
        color = self.color_var.get()
        trie = self.trie_white if color == "blancas" else self.trie_black
        title = f"Árbol de Aperturas - {color.capitalize()}"
        
        print(f"Mostrando {title}...")
        plot_tree_improved(trie, title)

    def show_stats(self):
        color = self.color_var.get()
        trie = self.trie_white if color == "blancas" else self.trie_black
        title = f"Estadísticas de Aperturas - {color.capitalize()}"
        
        print(f"Mostrando {title}...")
        plot_opening_stats(trie, title)


# ====================
# Main
# ====================
if __name__ == "__main__":
    trie_white = Trie()
    trie_black = Trie()
    
    # Aperturas con estadísticas más realistas
    openings_data = [
    
    
    # Defensa Siciliana y variantes
    (trie_white, ["e4", "c5"], {"blancas": 45, "negras": 40, "tablas": 15}, "Defensa Siciliana"),
    (trie_white, ["e4", "c5", "Nf3"], {"blancas": 47, "negras": 38, "tablas": 15}, "Siciliana Abierta"),
    (trie_white, ["e4", "c5", "Nf3", "d6"], {"blancas": 46, "negras": 39, "tablas": 15}, "Variante Najdorf"),
    (trie_white, ["e4", "c5", "Nf3", "d6", "d4"], {"blancas": 48, "negras": 37, "tablas": 15}, "Siciliana Najdorf"),
    (trie_white, ["e4", "c5", "Nf3", "d6", "d4", "cxd4"], {"blancas": 49, "negras": 36, "tablas": 15}, "Siciliana Najdorf Principal"),
    (trie_white, ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4"], {"blancas": 50, "negras": 35, "tablas": 15}, "Siciliana Najdorf Desarrollada"),
    (trie_white, ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6"], {"blancas": 51, "negras": 34, "tablas": 15}, "Najdorf con Cf6"),
    (trie_white, ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3"], {"blancas": 52, "negras": 33, "tablas": 15}, "Najdorf Línea Principal"),
    (trie_white, ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6"], {"blancas": 53, "negras": 32, "tablas": 15}, "Najdorf Clásica"),
    
    (trie_white, ["e4", "c5", "Nf3", "Nc6"], {"blancas": 44, "negras": 41, "tablas": 15}, "Siciliana Acelerada"),
    (trie_white, ["e4", "c5", "Nf3", "Nc6", "d4"], {"blancas": 45, "negras": 40, "tablas": 15}, "Siciliana Acelerada Principal"),
    (trie_white, ["e4", "c5", "Nf3", "Nc6", "d4", "cxd4"], {"blancas": 46, "negras": 39, "tablas": 15}, "Siciliana Acelerada Desarrollada"),
    (trie_white, ["e4", "c5", "Nf3", "Nc6", "d4", "cxd4", "Nxd4"], {"blancas": 47, "negras": 38, "tablas": 15}, "Siciliana Acelerada Sistema"),
    
    (trie_white, ["e4", "c5", "Nf3", "g6"], {"blancas": 43, "negras": 42, "tablas": 15}, "Dragón Siciliano"),
    (trie_white, ["e4", "c5", "Nf3", "g6", "d4"], {"blancas": 44, "negras": 41, "tablas": 15}, "Dragón Principal"),
    (trie_white, ["e4", "c5", "Nf3", "g6", "d4", "cxd4"], {"blancas": 45, "negras": 40, "tablas": 15}, "Dragón Abierto"),
    (trie_white, ["e4", "c5", "Nf3", "g6", "d4", "cxd4", "Nxd4"], {"blancas": 46, "negras": 39, "tablas": 15}, "Dragón Desarrollado"),
    (trie_white, ["e4", "c5", "Nf3", "g6", "d4", "cxd4", "Nxd4", "Bg7"], {"blancas": 47, "negras": 38, "tablas": 15}, "Dragón con Alfil"),
    
    (trie_white, ["e4", "c5", "Nc3"], {"blancas": 41, "negras": 44, "tablas": 15}, "Siciliana Cerrada"),
    (trie_white, ["e4", "c5", "Nc3", "Nc6"], {"blancas": 42, "negras": 43, "tablas": 15}, "Siciliana Cerrada Principal"),
    (trie_white, ["e4", "c5", "Nc3", "Nc6", "g3"], {"blancas": 43, "negras": 42, "tablas": 15}, "Siciliana Cerrada Fianchetto"),
    
    # Defensa Francesa y variantes
    (trie_white, ["e4", "e6"], {"blancas": 43, "negras": 42, "tablas": 15}, "Defensa Francesa"),
    (trie_white, ["e4", "e6", "d4"], {"blancas": 44, "negras": 41, "tablas": 15}, "Francesa Principal"),
    (trie_white, ["e4", "e6", "d4", "d5"], {"blancas": 45, "negras": 40, "tablas": 15}, "Francesa Clásica"),
    (trie_white, ["e4", "e6", "d4", "d5", "Nc3"], {"blancas": 46, "negras": 39, "tablas": 15}, "Variante Winawer"),
    (trie_white, ["e4", "e6", "d4", "d5", "Nc3", "Bb4"], {"blancas": 47, "negras": 38, "tablas": 15}, "Winawer Principal"),
    (trie_white, ["e4", "e6", "d4", "d5", "Nc3", "Bb4", "e5"], {"blancas": 48, "negras": 37, "tablas": 15}, "Winawer Avance"),
    (trie_white, ["e4", "e6", "d4", "d5", "Nc3", "Bb4", "e5", "c5"], {"blancas": 49, "negras": 36, "tablas": 15}, "Winawer Línea Principal"),
    
    (trie_white, ["e4", "e6", "d4", "d5", "exd5"], {"blancas": 42, "negras": 43, "tablas": 15}, "Francesa Intercambio"),
    (trie_white, ["e4", "e6", "d4", "d5", "exd5", "exd5"], {"blancas": 43, "negras": 42, "tablas": 15}, "Francesa Intercambio Principal"),
    
    (trie_white, ["e4", "e6", "d4", "d5", "Nd2"], {"blancas": 44, "negras": 41, "tablas": 15}, "Variante Tarrasch"),
    (trie_white, ["e4", "e6", "d4", "d5", "Nd2", "Nf6"], {"blancas": 45, "negras": 40, "tablas": 15}, "Tarrasch Principal"),
    (trie_white, ["e4", "e6", "d4", "d5", "Nd2", "Nf6", "e5"], {"blancas": 46, "negras": 39, "tablas": 15}, "Tarrasch Avance"),
    
    # Defensa Caro-Kann y variantes
    (trie_white, ["e4", "c6"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Caro-Kann"),
    (trie_white, ["e4", "c6", "d4"], {"blancas": 47, "negras": 39, "tablas": 14}, "Caro-Kann Principal"),
    (trie_white, ["e4", "c6", "d4", "d5"], {"blancas": 48, "negras": 38, "tablas": 14}, "Caro-Kann Clásica"),
    (trie_white, ["e4", "c6", "d4", "d5", "Nc3"], {"blancas": 49, "negras": 37, "tablas": 14}, "Variante Principal"),
    (trie_white, ["e4", "c6", "d4", "d5", "Nc3", "dxe4"], {"blancas": 50, "negras": 36, "tablas": 14}, "Caro-Kann Principal Intercambio"),
    (trie_white, ["e4", "c6", "d4", "d5", "Nc3", "dxe4", "Nxe4"], {"blancas": 51, "negras": 35, "tablas": 14}, "Caro-Kann Línea Principal"),
    (trie_white, ["e4", "c6", "d4", "d5", "Nc3", "dxe4", "Nxe4", "Bf5"], {"blancas": 52, "negras": 34, "tablas": 14}, "Caro-Kann Clásica Moderna"),
    
    (trie_white, ["e4", "c6", "d4", "d5", "exd5"], {"blancas": 45, "negras": 41, "tablas": 14}, "Caro-Kann Intercambio"),
    (trie_white, ["e4", "c6", "d4", "d5", "exd5", "cxd5"], {"blancas": 46, "negras": 40, "tablas": 14}, "Caro-Kann Intercambio Principal"),
    
    (trie_white, ["e4", "c6", "d4", "d5", "f3"], {"blancas": 44, "negras": 42, "tablas": 14}, "Ataque Fantasma"),
    (trie_white, ["e4", "c6", "Nc3"], {"blancas": 43, "negras": 43, "tablas": 14}, "Caro-Kann Dos Caballos"),
    
    # Apertura Italiana y variantes
    (trie_white, ["e4", "e5"], {"blancas": 48, "negras": 37, "tablas": 15}, "Rey y Peón"),
    (trie_white, ["e4", "e5", "Nf3"], {"blancas": 49, "negras": 36, "tablas": 15}, "Apertura del Caballo del Rey"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6"], {"blancas": 50, "negras": 35, "tablas": 15}, "Defensa Petrov"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bc4"], {"blancas": 51, "negras": 34, "tablas": 15}, "Apertura Italiana"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5"], {"blancas": 52, "negras": 33, "tablas": 15}, "Italiana Clásica"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "c3"], {"blancas": 53, "negras": 32, "tablas": 15}, "Italiana con c3"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "d3"], {"blancas": 52, "negras": 33, "tablas": 15}, "Italiana con d3"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "0-0"], {"blancas": 54, "negras": 31, "tablas": 15}, "Italiana Enroque"),
    
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bc4", "f5"], {"blancas": 49, "negras": 36, "tablas": 15}, "Defensa Rousseau"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bc4", "Be7"], {"blancas": 50, "negras": 35, "tablas": 15}, "Defensa Húngara"),
    
    # Ruy López (Apertura Española) y variantes
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5"], {"blancas": 52, "negras": 35, "tablas": 13}, "Ruy López"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"], {"blancas": 53, "negras": 34, "tablas": 13}, "Defensa Morphy"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4"], {"blancas": 54, "negras": 33, "tablas": 13}, "Ruy López Principal"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6"], {"blancas": 55, "negras": 32, "tablas": 13}, "Defensa Cerrada"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "0-0"], {"blancas": 56, "negras": 31, "tablas": 13}, "Ruy López Cerrada"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "0-0", "Be7"], {"blancas": 57, "negras": 30, "tablas": 13}, "Ruy López Cerrada Principal"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "0-0", "Be7", "Re1"], {"blancas": 58, "negras": 29, "tablas": 13}, "Ruy López Cerrada Moderna"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "0-0", "Be7", "Re1", "b5"], {"blancas": 59, "negras": 28, "tablas": 13}, "Variante Breyer"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "0-0", "Be7", "Re1", "b5", "Bb3"], {"blancas": 60, "negras": 27, "tablas": 13}, "Breyer Principal"),
    
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "d6"], {"blancas": 50, "negras": 37, "tablas": 13}, "Defensa Steinitz"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "f5"], {"blancas": 48, "negras": 39, "tablas": 13}, "Defensa Schliemann"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Bxc6"], {"blancas": 49, "negras": 38, "tablas": 13}, "Ruy López Intercambio"),
    
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "Bc5"], {"blancas": 51, "negras": 36, "tablas": 13}, "Defensa Cordel"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "f5"], {"blancas": 47, "negras": 40, "tablas": 13}, "Defensa Janisch"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "Bb5", "Nd4"], {"blancas": 48, "negras": 39, "tablas": 13}, "Defensa Bird"),
    
    # Defensa Petrov (Rusa)
    (trie_white, ["e4", "e5", "Nf3", "Nf6"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Petrov"),
    (trie_white, ["e4", "e5", "Nf3", "Nf6", "Nxe5"], {"blancas": 47, "negras": 39, "tablas": 14}, "Petrov Principal"),
    (trie_white, ["e4", "e5", "Nf3", "Nf6", "Nxe5", "d6"], {"blancas": 48, "negras": 38, "tablas": 14}, "Petrov Clásica"),
    (trie_white, ["e4", "e5", "Nf3", "Nf6", "Nxe5", "d6", "Nf3"], {"blancas": 49, "negras": 37, "tablas": 14}, "Petrov Moderna"),
    (trie_white, ["e4", "e5", "Nf3", "Nf6", "d3"], {"blancas": 45, "negras": 41, "tablas": 14}, "Petrov con d3"),
    
    # Gambito de Rey y variantes
    (trie_white, ["e4", "e5", "f4"], {"blancas": 45, "negras": 42, "tablas": 13}, "Gambito de Rey"),
    (trie_white, ["e4", "e5", "f4", "exf4"], {"blancas": 46, "negras": 41, "tablas": 13}, "Gambito de Rey Aceptado"),
    (trie_white, ["e4", "e5", "f4", "exf4", "Nf3"], {"blancas": 47, "negras": 40, "tablas": 13}, "Gambito de Rey Caballo"),
    (trie_white, ["e4", "e5", "f4", "exf4", "Bc4"], {"blancas": 46, "negras": 41, "tablas": 13}, "Gambito de Rey Alfil"),
    (trie_white, ["e4", "e5", "f4", "Bc5"], {"blancas": 44, "negras": 43, "tablas": 13}, "Gambito de Rey Declinado"),
    (trie_white, ["e4", "e5", "f4", "d5"], {"blancas": 43, "negras": 44, "tablas": 13}, "Contragambito Falkbeer"),
    
    # Otras defensas tras e4
    (trie_white, ["e4", "d6"], {"blancas": 47, "negras": 39, "tablas": 14}, "Defensa Pirc"),
    (trie_white, ["e4", "d6", "d4"], {"blancas": 48, "negras": 38, "tablas": 14}, "Pirc Principal"),
    (trie_white, ["e4", "d6", "d4", "Nf6"], {"blancas": 49, "negras": 37, "tablas": 14}, "Pirc Clásica"),
    (trie_white, ["e4", "d6", "d4", "Nf6", "Nc3"], {"blancas": 50, "negras": 36, "tablas": 14}, "Pirc con Cc3"),
    (trie_white, ["e4", "d6", "d4", "Nf6", "Nc3", "g6"], {"blancas": 51, "negras": 35, "tablas": 14}, "Pirc Fianchetto"),
    
    (trie_white, ["e4", "g6"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Moderna"),
    (trie_white, ["e4", "g6", "d4"], {"blancas": 47, "negras": 39, "tablas": 14}, "Moderna Principal"),
    (trie_white, ["e4", "g6", "d4", "Bg7"], {"blancas": 48, "negras": 38, "tablas": 14}, "Moderna con Alfil"),
    
    (trie_white, ["e4", "Nc6"], {"blancas": 45, "negras": 41, "tablas": 14}, "Defensa Nimzowitsch"),
    (trie_white, ["e4", "Nc6", "d4"], {"blancas": 46, "negras": 40, "tablas": 14}, "Nimzowitsch Principal"),
    
    (trie_white, ["e4", "a6"], {"blancas": 50, "negras": 36, "tablas": 14}, "Defensa Saint George"),
    (trie_white, ["e4", "b6"], {"blancas": 49, "negras": 37, "tablas": 14}, "Defensa Owen"),
    (trie_white, ["e4", "f5"], {"blancas": 52, "negras": 34, "tablas": 14}, "Defensa Barnes"),
    
    # ===== APERTURAS DE PEÓN DE DAMA (1.d4) =====
    
    # Gambito de Dama y variantes
    (trie_white, ["d4", "d5"], {"blancas": 48, "negras": 38, "tablas": 14}, "Peón Dama vs Peón Dama"),
    (trie_white, ["d4", "d5", "c4"], {"blancas": 49, "negras": 37, "tablas": 14}, "Gambito de Dama"),
    (trie_white, ["d4", "d5", "c4", "e6"], {"blancas": 50, "negras": 36, "tablas": 14}, "Gambito de Dama Declinado"),
    (trie_white, ["d4", "d5", "c4", "e6", "Nc3"], {"blancas": 51, "negras": 35, "tablas": 14}, "GDD Principal"),
    (trie_white, ["d4", "d5", "c4", "e6", "Nc3", "Nf6"], {"blancas": 52, "negras": 34, "tablas": 14}, "GDD Ortodoxo"),
    (trie_white, ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5"], {"blancas": 53, "negras": 33, "tablas": 14}, "GDD con Alfil"),
    (trie_white, ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7"], {"blancas": 54, "negras": 32, "tablas": 14}, "GDD Línea Principal"),
    (trie_white, ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7", "e3"], {"blancas": 55, "negras": 31, "tablas": 14}, "GDD Ortodoxo Clásico"),
    (trie_white, ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7", "e3", "0-0"], {"blancas": 56, "negras": 30, "tablas": 14}, "GDD Ortodoxo Principal"),
    
    (trie_white, ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Nf3"], {"blancas": 50, "negras": 36, "tablas": 14}, "GDD con Cf3"),
    (trie_white, ["d4", "d5", "c4", "e6", "Nf3"], {"blancas": 49, "negras": 37, "tablas": 14}, "Sistema Réti-Gambito"),
    
    (trie_white, ["d4", "d5", "c4", "dxc4"], {"blancas": 47, "negras": 39, "tablas": 14}, "Gambito de Dama Aceptado"),
    (trie_white, ["d4", "d5", "c4", "dxc4", "Nf3"], {"blancas": 48, "negras": 38, "tablas": 14}, "GDA Principal"),
    (trie_white, ["d4", "d5", "c4", "dxc4", "Nf3", "Nf6"], {"blancas": 49, "negras": 37, "tablas": 14}, "GDA con Cf6"),
    (trie_white, ["d4", "d5", "c4", "dxc4", "Nf3", "Nf6", "e3"], {"blancas": 50, "negras": 36, "tablas": 14}, "GDA Clásico"),
    (trie_white, ["d4", "d5", "c4", "dxc4", "e4"], {"blancas": 46, "negras": 40, "tablas": 14}, "GDA con e4"),
    
    (trie_white, ["d4", "d5", "c4", "c6"], {"blancas": 48, "negras": 38, "tablas": 14}, "Defensa Eslava"),
    (trie_white, ["d4", "d5", "c4", "c6", "Nf3"], {"blancas": 49, "negras": 37, "tablas": 14}, "Eslava Principal"),
    (trie_white, ["d4", "d5", "c4", "c6", "Nf3", "Nf6"], {"blancas": 50, "negras": 36, "tablas": 14}, "Eslava Clásica"),
    (trie_white, ["d4", "d5", "c4", "c6", "Nf3", "Nf6", "Nc3"], {"blancas": 51, "negras": 35, "tablas": 14}, "Eslava con Cc3"),
    (trie_white, ["d4", "d5", "c4", "c6", "Nf3", "Nf6", "Nc3", "dxc4"], {"blancas": 50, "negras": 36, "tablas": 14}, "Eslava Aceptada"),
    
    (trie_white, ["d4", "d5", "c4", "Nc6"], {"blancas": 45, "negras": 41, "tablas": 14}, "Defensa Chigorin"),
    (trie_white, ["d4", "d5", "c4", "Bf5"], {"blancas": 47, "negras": 39, "tablas": 14}, "Defensa Báltica"),
    (trie_white, ["d4", "d5", "c4", "f5"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Staunton"),
    
    # Defensas Indias
    (trie_white, ["d4", "Nf6"], {"blancas": 47, "negras": 39, "tablas": 14}, "Defensas Indias"),
    (trie_white, ["d4", "Nf6", "c4"], {"blancas": 48, "negras": 38, "tablas": 14}, "Sistema Inglés-Indio"),
    (trie_white, ["d4", "Nf6", "c4", "g6"], {"blancas": 47, "negras": 39, "tablas": 14}, "Defensa India de Rey"),
    (trie_white, ["d4", "Nf6", "c4", "g6", "Nc3"], {"blancas": 48, "negras": 38, "tablas": 14}, "India de Rey Principal"),
    (trie_white, ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7"], {"blancas": 49, "negras": 37, "tablas": 14}, "India de Rey con Alfil"),
    (trie_white, ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4"], {"blancas": 50, "negras": 36, "tablas": 14}, "Ataque de los Cuatro Peones"),
    (trie_white, ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4", "d6"], {"blancas": 51, "negras": 35, "tablas": 14}, "India de Rey Clásica"),
    (trie_white, ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4", "d6", "f3"], {"blancas": 52, "negras": 34, "tablas": 14}, "Ataque Sämisch"),
    (trie_white, ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4", "d6", "Nf3"], {"blancas": 50, "negras": 36, "tablas": 14}, "India de Rey Moderna"),
    (trie_white, ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4", "d6", "Be2"], {"blancas": 49, "negras": 37, "tablas": 14}, "Sistema Averbakh"),
    
    (trie_white, ["d4", "Nf6", "c4", "e6"], {"blancas": 49, "negras": 37, "tablas": 14}, "Defensa Nimzo-India"),
    (trie_white, ["d4", "Nf6", "c4", "e6", "Nc3"], {"blancas": 50, "negras": 36, "tablas": 14}, "Nimzo-India Principal"),
    (trie_white, ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4"], {"blancas": 49, "negras": 37, "tablas": 14}, "Nimzo-India Clásica"),
    (trie_white, ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4", "e3"], {"blancas": 50, "negras": 36, "tablas": 14}, "Variante Rubinstein"),
    (trie_white, ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4", "Qc2"], {"blancas": 48, "negras": 38, "tablas": 14}, "Variante Capablanca"),
    (trie_white, ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4", "a3"], {"blancas": 47, "negras": 39, "tablas": 14}, "Variante Sämisch"),
    (trie_white, ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4", "f3"], {"blancas": 46, "negras": 40, "tablas": 14}, "Variante Kmoch"),
    
    (trie_white, ["d4", "Nf6", "c4", "c5"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Benoni"),
    (trie_white, ["d4", "Nf6", "c4", "c5", "d5"], {"blancas": 47, "negras": 39, "tablas": 14}, "Benoni Moderna"),
    (trie_white, ["d4", "Nf6", "c4", "c5", "d5", "e6"], {"blancas": 48, "negras": 38, "tablas": 14}, "Benoni Principal"),
    (trie_white, ["d4", "Nf6", "c4", "c5", "d5", "e6", "Nc3"], {"blancas": 49, "negras": 37, "tablas": 14}, "Benoni Clásica"),
    (trie_white, ["d4", "Nf6", "c4", "c5", "d5", "e6", "Nc3", "exd5"], {"blancas": 50, "negras": 36, "tablas": 14}, "Benoni Intercambio"),
    (trie_white, ["d4", "Nf6", "c4", "c5", "d5", "e6", "Nc3", "exd5", "cxd5"], {"blancas": 51, "negras": 35, "tablas": 14}, "Benoni Línea Principal"),
    
    (trie_white, ["d4", "Nf6", "c4", "d6"], {"blancas": 48, "negras": 38, "tablas": 14}, "Defensa India Antigua"),
    (trie_white, ["d4", "Nf6", "c4", "d6", "Nc3"], {"blancas": 49, "negras": 37, "tablas": 14}, "India Antigua Principal"),
    (trie_white, ["d4", "Nf6", "c4", "d6", "Nc3", "e5"], {"blancas": 48, "negras": 38, "tablas": 14}, "India Antigua con e5"),
    
    (trie_white, ["d4", "Nf6", "c4", "b6"], {"blancas": 47, "negras": 39, "tablas": 14}, "Defensa India de Dama"),
    (trie_white, ["d4", "Nf6", "c4", "b6", "Nc3"], {"blancas": 48, "negras": 38, "tablas": 14}, "India de Dama Principal"),
    (trie_white, ["d4", "Nf6", "c4", "b6", "Nc3", "Bb7"], {"blancas": 49, "negras": 37, "tablas": 14}, "India de Dama con Alfil"),
    (trie_white, ["d4", "Nf6", "c4", "b6", "g3"], {"blancas": 46, "negras": 40, "tablas": 14}, "India de Dama Fianchetto"),
    
    # Defensa Holandesa
    (trie_white, ["d4", "f5"], {"blancas": 45, "negras": 41, "tablas": 14}, "Defensa Holandesa"),
    (trie_white, ["d4", "f5", "g3"], {"blancas": 46, "negras": 40, "tablas": 14}, "Holandesa con g3"),
    (trie_white, ["d4", "f5", "g3", "Nf6"], {"blancas": 47, "negras": 39, "tablas": 14}, "Holandesa Principal"),
    (trie_white, ["d4", "f5", "g3", "Nf6", "Bg2"], {"blancas": 48, "negras": 38, "tablas": 14}, "Holandesa con Alfil"),
    (trie_white, ["d4", "f5", "c4"], {"blancas": 44, "negras": 42, "tablas": 14}, "Holandesa con c4"),
    (trie_white, ["d4", "f5", "c4", "Nf6"], {"blancas": 45, "negras": 41, "tablas": 14}, "Holandesa Stonewall"),
    (trie_white, ["d4", "f5", "c4", "Nf6", "g3"], {"blancas": 46, "negras": 40, "tablas": 14}, "Holandesa Moderna"),
    (trie_white, ["d4", "f5", "Nf3"], {"blancas": 43, "negras": 43, "tablas": 14}, "Holandesa con Cf3"),
    
    # Otras aperturas tras d4
    (trie_white, ["d4", "e6"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Franco-India"),
    (trie_white, ["d4", "e6", "c4"], {"blancas": 47, "negras": 39, "tablas": 14}, "Franco-India Principal"),
    (trie_white, ["d4", "e6", "e4"], {"blancas": 45, "negras": 41, "tablas": 14}, "Ataque Blackmar-Diemer"),
    
    (trie_white, ["d4", "c5"], {"blancas": 44, "negras": 42, "tablas": 14}, "Defensa Benoni Antigua"),
    (trie_white, ["d4", "c5", "d5"], {"blancas": 45, "negras": 41, "tablas": 14}, "Benoni Avance"),
    (trie_white, ["d4", "c5", "Nf3"], {"blancas": 43, "negras": 43, "tablas": 14}, "Benoni con Cf3"),
    
    (trie_white, ["d4", "g6"], {"blancas": 45, "negras": 41, "tablas": 14}, "Defensa India Moderna"),
    (trie_white, ["d4", "g6", "c4"], {"blancas": 46, "negras": 40, "tablas": 14}, "India Moderna Principal"),
    (trie_white, ["d4", "g6", "e4"], {"blancas": 44, "negras": 42, "tablas": 14}, "India Moderna con e4"),
    
    # ===== APERTURAS DE FLANCO =====
    
    # Apertura Inglesa
    (trie_white, ["c4"], {"blancas": 47, "negras": 39, "tablas": 14}, "Apertura Inglesa"),
    (trie_white, ["c4", "e5"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Siciliana Inversa"),
    (trie_white, ["c4", "e5", "Nc3"], {"blancas": 47, "negras": 39, "tablas": 14}, "Inglesa con Cc3"),
    (trie_white, ["c4", "e5", "Nc3", "Nf6"], {"blancas": 48, "negras": 38, "tablas": 14}, "Inglesa Principal"),
    (trie_white, ["c4", "e5", "Nc3", "Nc6"], {"blancas": 47, "negras": 39, "tablas": 14}, "Inglesa Simétrica"),
    (trie_white, ["c4", "e5", "g3"], {"blancas": 45, "negras": 41, "tablas": 14}, "Inglesa Fianchetto"),
    (trie_white, ["c4", "e5", "Nf3"], {"blancas": 46, "negras": 40, "tablas": 14}, "Inglesa con Cf3"),
    
    (trie_white, ["c4", "Nf6"], {"blancas": 48, "negras": 38, "tablas": 14}, "Defensa Anglo-India"),
    (trie_white, ["c4", "Nf6", "Nc3"], {"blancas": 49, "negras": 37, "tablas": 14}, "Anglo-India Principal"),
    (trie_white, ["c4", "Nf6", "g3"], {"blancas": 47, "negras": 39, "tablas": 14}, "Anglo-India Fianchetto"),
    (trie_white, ["c4", "Nf6", "Nf3"], {"blancas": 48, "negras": 38, "tablas": 14}, "Sistema Réti por Transposición"),
    
    (trie_white, ["c4", "c5"], {"blancas": 45, "negras": 41, "tablas": 14}, "Variante Simétrica"),
    (trie_white, ["c4", "c5", "Nc3"], {"blancas": 46, "negras": 40, "tablas": 14}, "Simétrica Principal"),
    (trie_white, ["c4", "c5", "g3"], {"blancas": 44, "negras": 42, "tablas": 14}, "Simétrica Fianchetto"),
    (trie_white, ["c4", "c5", "Nf3"], {"blancas": 45, "negras": 41, "tablas": 14}, "Simétrica con Cf3"),
    
    (trie_white, ["c4", "d5"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Anglo-Escandinava"),
    (trie_white, ["c4", "d5", "cxd5"], {"blancas": 47, "negras": 39, "tablas": 14}, "Anglo-Escandinava Intercambio"),
    (trie_white, ["c4", "d5", "Nf3"], {"blancas": 45, "negras": 41, "tablas": 14}, "Anglo-Escandinava con Cf3"),
    
    (trie_white, ["c4", "g6"], {"blancas": 44, "negras": 42, "tablas": 14}, "Defensa Moderna contra Inglesa"),
    (trie_white, ["c4", "f5"], {"blancas": 43, "negras": 43, "tablas": 14}, "Defensa Holandesa contra Inglesa"),
    
    # Sistema Réti
    (trie_white, ["Nf3"], {"blancas": 46, "negras": 40, "tablas": 14}, "Apertura Réti"),
    (trie_white, ["Nf3", "d5"], {"blancas": 47, "negras": 39, "tablas": 14}, "Réti contra d5"),
    (trie_white, ["Nf3", "d5", "g3"], {"blancas": 48, "negras": 38, "tablas": 14}, "Réti Fianchetto"),
    (trie_white, ["Nf3", "d5", "c4"], {"blancas": 49, "negras": 37, "tablas": 14}, "Réti con c4"),
    (trie_white, ["Nf3", "d5", "c4", "d4"], {"blancas": 47, "negras": 39, "tablas": 14}, "Réti Avance"),
    (trie_white, ["Nf3", "d5", "c4", "dxc4"], {"blancas": 48, "negras": 38, "tablas": 14}, "Réti Aceptado"),
    
    (trie_white, ["Nf3", "Nf6"], {"blancas": 45, "negras": 41, "tablas": 14}, "Réti Simétrico"),
    (trie_white, ["Nf3", "Nf6", "g3"], {"blancas": 46, "negras": 40, "tablas": 14}, "Sistema Réti"),
    (trie_white, ["Nf3", "Nf6", "g3", "g6"], {"blancas": 47, "negras": 39, "tablas": 14}, "Doble Fianchetto"),
    (trie_white, ["Nf3", "Nf6", "c4"], {"blancas": 48, "negras": 38, "tablas": 14}, "Réti-Inglesa"),
    (trie_white, ["Nf3", "Nf6", "d4"], {"blancas": 49, "negras": 37, "tablas": 14}, "Transposición a d4"),
    
    (trie_white, ["Nf3", "c5"], {"blancas": 44, "negras": 42, "tablas": 14}, "Réti contra Siciliana"),
    (trie_white, ["Nf3", "e6"], {"blancas": 45, "negras": 41, "tablas": 14}, "Réti contra Francesa"),
    (trie_white, ["Nf3", "f5"], {"blancas": 43, "negras": 43, "tablas": 14}, "Réti contra Holandesa"),
    
    # Apertura Bird
    (trie_white, ["f4"], {"blancas": 42, "negras": 44, "tablas": 14}, "Apertura Bird"),
    (trie_white, ["f4", "d5"], {"blancas": 43, "negras": 43, "tablas": 14}, "Bird contra d5"),
    (trie_white, ["f4", "d5", "Nf3"], {"blancas": 44, "negras": 42, "tablas": 14}, "Bird con Cf3"),
    (trie_white, ["f4", "d5", "e3"], {"blancas": 42, "negras": 44, "tablas": 14}, "Bird con e3"),
    (trie_white, ["f4", "Nf6"], {"blancas": 41, "negras": 45, "tablas": 14}, "Bird contra Cf6"),
    (trie_white, ["f4", "e5"], {"blancas": 40, "negras": 46, "tablas": 14}, "Gambito From"),
    (trie_white, ["f4", "c5"], {"blancas": 41, "negras": 45, "tablas": 14}, "Bird Siciliana"),
    
    # Apertura Larsen
    (trie_white, ["b3"], {"blancas": 43, "negras": 43, "tablas": 14}, "Apertura Larsen"),
    (trie_white, ["b3", "e5"], {"blancas": 42, "negras": 44, "tablas": 14}, "Larsen contra e5"),
    (trie_white, ["b3", "d5"], {"blancas": 44, "negras": 42, "tablas": 14}, "Larsen contra d5"),
    (trie_white, ["b3", "Nf6"], {"blancas": 43, "negras": 43, "tablas": 14}, "Larsen contra Cf6"),
    
    # Otras aperturas de flanco
    (trie_white, ["g3"], {"blancas": 44, "negras": 42, "tablas": 14}, "Apertura Benko"),
    (trie_white, ["g3", "d5"], {"blancas": 45, "negras": 41, "tablas": 14}, "Benko contra d5"),
    (trie_white, ["g3", "e5"], {"blancas": 43, "negras": 43, "tablas": 14}, "Benko contra e5"),
    
    (trie_white, ["Nc3"], {"blancas": 42, "negras": 44, "tablas": 14}, "Apertura Dunst"),
    (trie_white, ["Nc3", "d5"], {"blancas": 43, "negras": 43, "tablas": 14}, "Dunst contra d5"),
    (trie_white, ["Nc3", "e5"], {"blancas": 41, "negras": 45, "tablas": 14}, "Dunst contra e5"),
    
    # ===== APERTURAS IRREGULARES =====
    
    (trie_white, ["e3"], {"blancas": 41, "negras": 45, "tablas": 14}, "Apertura Van't Kruijs"),
    (trie_white, ["d3"], {"blancas": 40, "negras": 46, "tablas": 14}, "Apertura Mieses"),
    (trie_white, ["a3"], {"blancas": 39, "negras": 47, "tablas": 14}, "Apertura Anderssen"),
    (trie_white, ["h3"], {"blancas": 38, "negras": 48, "tablas": 14}, "Apertura Clemenz"),
    (trie_white, ["a4"], {"blancas": 37, "negras": 49, "tablas": 14}, "Apertura Ware"),
    (trie_white, ["b4"], {"blancas": 40, "negras": 46, "tablas": 14}, "Apertura Sokolsky"),
    (trie_white, ["g4"], {"blancas": 35, "negras": 51, "tablas": 14}, "Apertura Grob"),
    (trie_white, ["f3"], {"blancas": 34, "negras": 52, "tablas": 14}, "Apertura Gedult"),
    (trie_white, ["h4"], {"blancas": 33, "negras": 53, "tablas": 14}, "Apertura Desprez"),
    (trie_white, ["c3"], {"blancas": 39, "negras": 47, "tablas": 14}, "Apertura Saragossa"),
    
    # ===== APERTURAS PARA NEGRAS (Respuestas principales) =====
    
    # Respuestas a 1.e4
    (trie_black, ["e4", "e5"], {"blancas": 37, "negras": 48, "tablas": 15}, "Doble Rey (Negras)"),
    (trie_black, ["e4", "e5", "Nf3"], {"blancas": 36, "negras": 49, "tablas": 15}, "Defensa contra Cf3"),
    (trie_black, ["e4", "e5", "Nf3", "Nc6"], {"blancas": 35, "negras": 50, "tablas": 15}, "Defensa del Caballo de Dama"),
    (trie_black, ["e4", "e5", "Nf3", "Nc6", "Bb5"], {"blancas": 34, "negras": 51, "tablas": 15}, "Contra Ruy López"),
    (trie_black, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"], {"blancas": 33, "negras": 52, "tablas": 15}, "Defensa Morphy (Negras)"),
    (trie_black, ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4"], {"blancas": 32, "negras": 53, "tablas": 15}, "Morphy Principal (Negras)"),
    
    (trie_black, ["e4", "e5", "Nf3", "Nf6"], {"blancas": 40, "negras": 45, "tablas": 15}, "Defensa Petrov (Negras)"),
    (trie_black, ["e4", "e5", "Nf3", "Nf6", "Nxe5"], {"blancas": 39, "negras": 46, "tablas": 15}, "Petrov Principal (Negras)"),
    (trie_black, ["e4", "e5", "Nf3", "Nf6", "Nxe5", "d6"], {"blancas": 38, "negras": 47, "tablas": 15}, "Petrov Clásica (Negras)"),
    
    (trie_black, ["e4", "c5"], {"blancas": 40, "negras": 45, "tablas": 15}, "Siciliana (Negras)"),
    (trie_black, ["e4", "c5", "Nf3"], {"blancas": 39, "negras": 46, "tablas": 15}, "Siciliana Abierta (Negras)"),
    (trie_black, ["e4", "c5", "Nf3", "d6"], {"blancas": 38, "negras": 47, "tablas": 15}, "Siciliana Najdorf (Negras)"),
    (trie_black, ["e4", "c5", "Nf3", "d6", "d4"], {"blancas": 37, "negras": 48, "tablas": 15}, "Najdorf Principal (Negras)"),
    (trie_black, ["e4", "c5", "Nf3", "d6", "d4", "cxd4"], {"blancas": 36, "negras": 49, "tablas": 15}, "Najdorf Captura (Negras)"),
    
    (trie_black, ["e4", "c5", "Nf3", "Nc6"], {"blancas": 41, "negras": 44, "tablas": 15}, "Siciliana Acelerada (Negras)"),
    (trie_black, ["e4", "c5", "Nf3", "g6"], {"blancas": 42, "negras": 43, "tablas": 15}, "Dragón (Negras)"),
    (trie_black, ["e4", "c5", "Nf3", "e6"], {"blancas": 40, "negras": 45, "tablas": 15}, "Siciliana Paulsen (Negras)"),
    
    (trie_black, ["e4", "e6"], {"blancas": 42, "negras": 43, "tablas": 15}, "Francesa (Negras)"),
    (trie_black, ["e4", "e6", "d4"], {"blancas": 41, "negras": 44, "tablas": 15}, "Francesa Principal (Negras)"),
    (trie_black, ["e4", "e6", "d4", "d5"], {"blancas": 40, "negras": 45, "tablas": 15}, "Francesa Clásica (Negras)"),
    (trie_black, ["e4", "e6", "d4", "d5", "Nc3"], {"blancas": 39, "negras": 46, "tablas": 15}, "Winawer (Negras)"),
    (trie_black, ["e4", "e6", "d4", "d5", "Nc3", "Bb4"], {"blancas": 38, "negras": 47, "tablas": 15}, "Winawer Principal (Negras)"),
    
    (trie_black, ["e4", "c6"], {"blancas": 40, "negras": 46, "tablas": 14}, "Caro-Kann (Negras)"),
    (trie_black, ["e4", "c6", "d4"], {"blancas": 39, "negras": 47, "tablas": 14}, "Caro-Kann Principal (Negras)"),
    (trie_black, ["e4", "c6", "d4", "d5"], {"blancas": 38, "negras": 48, "tablas": 14}, "Caro-Kann Clásica (Negras)"),
    (trie_black, ["e4", "c6", "d4", "d5", "Nc3"], {"blancas": 37, "negras": 49, "tablas": 14}, "Caro-Kann Moderna (Negras)"),
    
    (trie_black, ["e4", "d6"], {"blancas": 39, "negras": 47, "tablas": 14}, "Pirc (Negras)"),
    (trie_black, ["e4", "d6", "d4"], {"blancas": 38, "negras": 48, "tablas": 14}, "Pirc Principal (Negras)"),
    (trie_black, ["e4", "d6", "d4", "Nf6"], {"blancas": 37, "negras": 49, "tablas": 14}, "Pirc Clásica (Negras)"),
    
    (trie_black, ["e4", "g6"], {"blancas": 40, "negras": 46, "tablas": 14}, "Moderna (Negras)"),
    (trie_black, ["e4", "g6", "d4"], {"blancas": 39, "negras": 47, "tablas": 14}, "Moderna Principal (Negras)"),
    
    # Respuestas a 1.d4
    (trie_black, ["d4", "d5"], {"blancas": 38, "negras": 48, "tablas": 14}, "Peón Dama (Negras)"),
    (trie_black, ["d4", "d5", "c4"], {"blancas": 37, "negras": 49, "tablas": 14}, "Contra Gambito Dama"),
    (trie_black, ["d4", "d5", "c4", "e6"], {"blancas": 36, "negras": 50, "tablas": 14}, "GDD (Negras)"),
    (trie_black, ["d4", "d5", "c4", "e6", "Nc3"], {"blancas": 35, "negras": 51, "tablas": 14}, "GDD Principal (Negras)"),
    (trie_black, ["d4", "d5", "c4", "e6", "Nc3", "Nf6"], {"blancas": 34, "negras": 52, "tablas": 14}, "GDD Ortodoxo (Negras)"),
    
    (trie_black, ["d4", "d5", "c4", "dxc4"], {"blancas": 39, "negras": 47, "tablas": 14}, "GDA (Negras)"),
    (trie_black, ["d4", "d5", "c4", "dxc4", "Nf3"], {"blancas": 38, "negras": 48, "tablas": 14}, "GDA Principal (Negras)"),
    
    (trie_black, ["d4", "d5", "c4", "c6"], {"blancas": 38, "negras": 48, "tablas": 14}, "Eslava (Negras)"),
    (trie_black, ["d4", "d5", "c4", "c6", "Nf3"], {"blancas": 37, "negras": 49, "tablas": 14}, "Eslava Principal (Negras)"),
    (trie_black, ["d4", "d5", "c4", "c6", "Nf3", "Nf6"], {"blancas": 36, "negras": 50, "tablas": 14}, "Eslava Clásica (Negras)"),
    
    (trie_black, ["d4", "Nf6"], {"blancas": 39, "negras": 47, "tablas": 14}, "Defensas Indias (Negras)"),
    (trie_black, ["d4", "Nf6", "c4"], {"blancas": 38, "negras": 48, "tablas": 14}, "Sistema Inglés-Indio (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "g6"], {"blancas": 39, "negras": 47, "tablas": 14}, "India de Rey (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "g6", "Nc3"], {"blancas": 38, "negras": 48, "tablas": 14}, "India de Rey Principal (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7"], {"blancas": 37, "negras": 49, "tablas": 14}, "India de Rey con Alfil (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4"], {"blancas": 36, "negras": 50, "tablas": 14}, "Contra Cuatro Peones (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4", "d6"], {"blancas": 35, "negras": 51, "tablas": 14}, "India de Rey Clásica (Negras)"),
    
    (trie_black, ["d4", "Nf6", "c4", "e6"], {"blancas": 37, "negras": 49, "tablas": 14}, "Nimzo-India (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "e6", "Nc3"], {"blancas": 36, "negras": 50, "tablas": 14}, "Nimzo-India Principal (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4"], {"blancas": 37, "negras": 49, "tablas": 14}, "Nimzo-India Clásica (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4", "e3"], {"blancas": 36, "negras": 50, "tablas": 14}, "Rubinstein (Negras)"),
    
    (trie_black, ["d4", "Nf6", "c4", "c5"], {"blancas": 40, "negras": 46, "tablas": 14}, "Benoni (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "c5", "d5"], {"blancas": 39, "negras": 47, "tablas": 14}, "Benoni Moderna (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "c5", "d5", "e6"], {"blancas": 38, "negras": 48, "tablas": 14}, "Benoni Principal (Negras)"),
    
    (trie_black, ["d4", "Nf6", "c4", "b6"], {"blancas": 39, "negras": 47, "tablas": 14}, "India de Dama (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "b6", "Nc3"], {"blancas": 38, "negras": 48, "tablas": 14}, "India de Dama Principal (Negras)"),
    (trie_black, ["d4", "Nf6", "c4", "b6", "Nc3", "Bb7"], {"blancas": 37, "negras": 49, "tablas": 14}, "India de Dama con Alfil (Negras)"),
    
    (trie_black, ["d4", "f5"], {"blancas": 41, "negras": 45, "tablas": 14}, "Holandesa (Negras)"),
    (trie_black, ["d4", "f5", "g3"], {"blancas": 40, "negras": 46, "tablas": 14}, "Holandesa con g3 (Negras)"),
    (trie_black, ["d4", "f5", "c4"], {"blancas": 42, "negras": 44, "tablas": 14}, "Holandesa con c4 (Negras)"),
    (trie_black, ["d4", "f5", "Nf3"], {"blancas": 43, "negras": 43, "tablas": 14}, "Holandesa con Cf3 (Negras)"),
    
    # Respuestas a 1.c4 (Apertura Inglesa)
    (trie_black, ["c4", "e5"], {"blancas": 40, "negras": 46, "tablas": 14}, "Siciliana Inversa (Negras)"),
    (trie_black, ["c4", "e5", "Nc3"], {"blancas": 39, "negras": 47, "tablas": 14}, "Contra Inglesa con Cc3"),
    (trie_black, ["c4", "e5", "g3"], {"blancas": 41, "negras": 45, "tablas": 14}, "Contra Inglesa Fianchetto"),
    
    (trie_black, ["c4", "Nf6"], {"blancas": 38, "negras": 48, "tablas": 14}, "Anglo-India (Negras)"),
    (trie_black, ["c4", "Nf6", "Nc3"], {"blancas": 37, "negras": 49, "tablas": 14}, "Anglo-India Principal (Negras)"),
    (trie_black, ["c4", "Nf6", "g3"], {"blancas": 39, "negras": 47, "tablas": 14}, "Anglo-India Fianchetto (Negras)"),
    
    (trie_black, ["c4", "c5"], {"blancas": 41, "negras": 45, "tablas": 14}, "Simétrica (Negras)"),
    (trie_black, ["c4", "c5", "Nc3"], {"blancas": 40, "negras": 46, "tablas": 14}, "Simétrica Principal (Negras)"),
    
    (trie_black, ["c4", "d5"], {"blancas": 40, "negras": 46, "tablas": 14}, "Anglo-Escandinava (Negras)"),
    (trie_black, ["c4", "d5", "cxd5"], {"blancas": 39, "negras": 47, "tablas": 14}, "Anglo-Escandinava Intercambio (Negras)"),
    
    (trie_black, ["c4", "g6"], {"blancas": 42, "negras": 44, "tablas": 14}, "Moderna contra Inglesa (Negras)"),
    (trie_black, ["c4", "f5"], {"blancas": 43, "negras": 43, "tablas": 14}, "Holandesa contra Inglesa (Negras)"),
    
    # Respuestas a 1.Cf3 (Sistema Réti)
    (trie_black, ["Nf3", "d5"], {"blancas": 39, "negras": 47, "tablas": 14}, "Contra Réti con d5"),
    (trie_black, ["Nf3", "d5", "g3"], {"blancas": 38, "negras": 48, "tablas": 14}, "Contra Réti Fianchetto"),
    (trie_black, ["Nf3", "d5", "c4"], {"blancas": 37, "negras": 49, "tablas": 14}, "Contra Réti con c4"),
    
    (trie_black, ["Nf3", "Nf6"], {"blancas": 41, "negras": 45, "tablas": 14}, "Réti Simétrico (Negras)"),
    (trie_black, ["Nf3", "Nf6", "g3"], {"blancas": 40, "negras": 46, "tablas": 14}, "Sistema Réti (Negras)"),
    (trie_black, ["Nf3", "Nf6", "c4"], {"blancas": 38, "negras": 48, "tablas": 14}, "Réti-Inglesa (Negras)"),
    
    (trie_black, ["Nf3", "c5"], {"blancas": 42, "negras": 44, "tablas": 14}, "Siciliana contra Réti"),
    (trie_black, ["Nf3", "e6"], {"blancas": 41, "negras": 45, "tablas": 14}, "Francesa contra Réti"),
    (trie_black, ["Nf3", "f5"], {"blancas": 43, "negras": 43, "tablas": 14}, "Holandesa contra Réti"),
    
    # ===== LÍNEAS TÁCTICAS Y GAMBITOS ADICIONALES =====
    
    # Gambitos con e4
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "f4"], {"blancas": 44, "negras": 42, "tablas": 14}, "Gambito Vienes"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "f4", "exf4"], {"blancas": 45, "negras": 41, "tablas": 14}, "Vienes Aceptado"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "d4"], {"blancas": 43, "negras": 43, "tablas": 14}, "Gambito Escocés"),
    (trie_white, ["e4", "e5", "Nf3", "Nc6", "d4", "exd4"], {"blancas": 44, "negras": 42, "tablas": 14}, "Escocés Aceptado"),
    
    (trie_white, ["e4", "e5", "Bc4"], {"blancas": 42, "negras": 44, "tablas": 14}, "Apertura del Alfil de Rey"),
    (trie_white, ["e4", "e5", "Bc4", "Nc6"], {"blancas": 43, "negras": 43, "tablas": 14}, "Alfil de Rey Principal"),
    (trie_white, ["e4", "e5", "Bc4", "f5"], {"blancas": 41, "negras": 45, "tablas": 14}, "Gambito Calabrés"),
    
    (trie_white, ["e4", "e5", "Nf3", "f5"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Damiano"),
    (trie_white, ["e4", "e5", "Nf3", "Qf6"], {"blancas": 48, "negras": 38, "tablas": 14}, "Defensa Napoleón"),
    (trie_white, ["e4", "e5", "Nf3", "d6"], {"blancas": 45, "negras": 41, "tablas": 14}, "Defensa Philidor"),
    (trie_white, ["e4", "e5", "Nf3", "d6", "d4"], {"blancas": 46, "negras": 40, "tablas": 14}, "Philidor Principal"),
    
    # Gambitos con d4
    (trie_white, ["d4", "d5", "e4"], {"blancas": 45, "negras": 41, "tablas": 14}, "Gambito Blackmar-Diemer"),
    (trie_white, ["d4", "d5", "e4", "dxe4"], {"blancas": 46, "negras": 40, "tablas": 14}, "BDG Aceptado"),
    (trie_white, ["d4", "d5", "e4", "dxe4", "Nc3"], {"blancas": 47, "negras": 39, "tablas": 14}, "BDG Principal"),
    (trie_white, ["d4", "d5", "e4", "dxe4", "f3"], {"blancas": 44, "negras": 42, "tablas": 14}, "BDG Lemberg"),
    
    (trie_white, ["d4", "f5", "e4"], {"blancas": 42, "negras": 44, "tablas": 14}, "Gambito Staunton"),
    (trie_white, ["d4", "f5", "e4", "fxe4"], {"blancas": 43, "negras": 43, "tablas": 14}, "Staunton Aceptado"),
    
    (trie_white, ["d4", "Nc6"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Nimzowitsch"),
    (trie_white, ["d4", "Nc6", "d5"], {"blancas": 47, "negras": 39, "tablas": 14}, "Nimzowitsch Avance"),
    (trie_white, ["d4", "Nc6", "c4"], {"blancas": 45, "negras": 41, "tablas": 14}, "Nimzowitsch con c4"),
    
    # Aperturas poco comunes pero teóricamente sólidas
    (trie_white, ["e4", "d5"], {"blancas": 48, "negras": 38, "tablas": 14}, "Defensa Escandinava"),
    (trie_white, ["e4", "d5", "exd5"], {"blancas": 49, "negras": 37, "tablas": 14}, "Escandinava Principal"),
    (trie_white, ["e4", "d5", "exd5", "Qxd5"], {"blancas": 50, "negras": 36, "tablas": 14}, "Escandinava con Dama"),
    (trie_white, ["e4", "d5", "exd5", "Nf6"], {"blancas": 47, "negras": 39, "tablas": 14}, "Gambito Marshall Escandinavo"),
    
    (trie_white, ["e4", "Nf6"], {"blancas": 46, "negras": 40, "tablas": 14}, "Defensa Alekhine"),
    (trie_white, ["e4", "Nf6", "e5"], {"blancas": 47, "negras": 39, "tablas": 14}, "Alekhine Principal"),
    (trie_white, ["e4", "Nf6", "e5", "Nd5"], {"blancas": 48, "negras": 38, "tablas": 14}, "Alekhine Clásica"),
    (trie_white, ["e4", "Nf6", "e5", "Nd5", "d4"], {"blancas": 49, "negras": 37, "tablas": 14}, "Alekhine con d4"),
    (trie_white, ["e4", "Nf6", "e5", "Nd5", "c4"], {"blancas": 48, "negras": 38, "tablas": 14}, "Variante Cuatro Peones Alekhine"),
    
    (trie_white, ["e4", "b6"], {"blancas": 49, "negras": 37, "tablas": 14}, "Defensa Owen"),
    (trie_white, ["e4", "b6", "d4"], {"blancas": 50, "negras": 36, "tablas": 14}, "Owen Principal"),
    (trie_white, ["e4", "b6", "d4", "Bb7"], {"blancas": 51, "negras": 35, "tablas": 14}, "Owen con Alfil"),
    
    (trie_white, ["e4", "a6"], {"blancas": 50, "negras": 36, "tablas": 14}, "Defensa Saint George"),
    (trie_white, ["e4", "a6", "d4"], {"blancas": 51, "negras": 35, "tablas": 14}, "Saint George Principal"),
    
    # Sistemas de desarrollo para ambos bandos
    (trie_white, ["Nf3", "Nf6", "g3", "d5", "Bg2"], {"blancas": 46, "negras": 40, "tablas": 14}, "Sistema Catalán por Transposición"),
    (trie_white, ["d4", "Nf6", "Nf3", "g6", "g3"], {"blancas": 45, "negras": 41, "tablas": 14}, "Sistema de Desarrollo Natural"),
    (trie_white, ["e4", "e6", "d3", "d5", "Nd2"], {"blancas": 43, "negras": 43, "tablas": 14}, "Ataque del Rey Indio"),
    (trie_white, ["d4", "d5", "Nf3", "Nf6", "e3"], {"blancas": 47, "negras": 39, "tablas": 14}, "Sistema Colle"),
    (trie_white, ["d4", "d5", "Nf3", "Nf6", "e3", "e6", "Bd3"], {"blancas": 48, "negras": 38, "tablas": 14}, "Colle-Zukertort"),
    
    # Aperturas hipermodernas adicionales
    (trie_white, ["g3", "d5", "Bg2", "Nf6"], {"blancas": 44, "negras": 42, "tablas": 14}, "Benko Hipermoderno"),
    (trie_white, ["b3", "e5", "Bb2", "Nc6"], {"blancas": 42, "negras": 44, "tablas": 14}, "Larsen Desarrollado"),
    (trie_white, ["f4", "d5", "Nf3", "Nf6", "e3"], {"blancas": 41, "negras": 45, "tablas": 14}, "Bird con Sistema"),
    
    # Transposiciones importantes
    (trie_white, ["c4", "e5", "Nc3", "Nf6", "Nf3"], {"blancas": 47, "negras": 39, "tablas": 14}, "Inglesa-Réti"),
    (trie_white, ["Nf3", "d5", "d4", "Nf6", "c4"], {"blancas": 49, "negras": 37, "tablas": 14}, "Réti-Dama"),
    (trie_white, ["g3", "Nf6", "Bg2", "d5", "Nf3"], {"blancas": 45, "negras": 41, "tablas": 14}, "Benko-Catalán"),
    
    # Variantes especializadas del Gambito de Rey
    (trie_white, ["e4", "e5", "f4", "exf4", "Nf3", "g5"], {"blancas": 45, "negras": 41, "tablas": 14}, "Defensa Kieseritzky"),
    (trie_white, ["e4", "e5", "f4", "exf4", "Nf3", "g5", "h4"], {"blancas": 46, "negras": 40, "tablas": 14}, "Ataque Allgaier"),
    (trie_white, ["e4", "e5", "f4", "exf4", "Bc4", "Qh4+"], {"blancas": 44, "negras": 42, "tablas": 14}, "Defensa Cunningham"),
    
    # Líneas adicionales de la Defensa Siciliana
    (trie_white, ["e4", "c5", "d4", "cxd4", "c3"], {"blancas": 44, "negras": 42, "tablas": 14}, "Gambito Morra"),
    (trie_white, ["e4", "c5", "d4", "cxd4", "c3", "dxc3"], {"blancas": 45, "negras": 41, "tablas": 14}, "Morra Aceptado"),
    (trie_white, ["e4", "c5", "f4"], {"blancas": 42, "negras": 44, "tablas": 14}, "Ataque Grand Prix"),
    (trie_white, ["e4", "c5", "f4", "d6"], {"blancas": 43, "negras": 43, "tablas": 14}, "Grand Prix Principal"),
    (trie_white, ["e4", "c5", "Nf3", "d6", "Bb5+"], {"blancas": 45, "negras": 41, "tablas": 14}, "Ataque Richter-Rauzer"),
    
    # Contraataques y defensas activas para negras
    (trie_black, ["e4", "e5", "Nf3", "Nc6", "Bc4", "f5"], {"blancas": 36, "negras": 49, "tablas": 15}, "Rousseau Gambit (Negras)"),
    (trie_black, ["d4", "e6", "e4", "d5"], {"blancas": 41, "negras": 45, "tablas": 14}, "Franco-India Francesa"),
    (trie_black, ["d4", "c5", "d5", "e6"], {"blancas": 42, "negras": 44, "tablas": 14}, "Benoni Benko (Negras)"),
    (trie_black, ["d4", "c5", "d5", "b5"], {"blancas": 40, "negras": 46, "tablas": 14}, "Gambito Benko (Negras)"),
    (trie_black, ["d4", "c5", "d5", "b5", "cxb5"], {"blancas": 41, "negras": 45, "tablas": 14}, "Benko Aceptado (Negras)"),
    (trie_black, ["d4", "c5", "d5", "b5", "cxb5", "a6"], {"blancas": 40, "negras": 46, "tablas": 14}, "Benko Principal (Negras)"),
]
    
    # Insertar datos en los tries
    for trie, moves, stats, opening in openings_data:
        for resultado, count in stats.items():
            for _ in range(count):
                trie.insert(moves, resultado, opening)
    
    # Crear y ejecutar la aplicación
    app = tb.Window(themename="flatly")
    app.geometry("900x700")
    ChessBookApp(app, trie_white, trie_black)
    app.mainloop()