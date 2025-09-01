import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import ipaddress

# ====================
# Clases para el Trie de IP
# ====================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.route_info = None


class IPTrie:
    def __init__(self):
        self.root = TrieNode()

    def insertar_prefijo(self, ip_binaria: str, longitud: int, interfaz: str):
        node = self.root
        for bit in ip_binaria[:longitud]:
            if bit not in node.children:
                node.children[bit] = TrieNode()
            node = node.children[bit]
        node.route_info = interfaz

    def buscar_ruta(self, ip_binaria: str) -> str:
        node = self.root
        mejor_coincidencia = None
        for bit in ip_binaria:
            if bit in node.children:
                node = node.children[bit]
                if node.route_info is not None:
                    mejor_coincidencia = node.route_info
            else:
                break
        return mejor_coincidencia

    def obtener_todas_rutas(self):
        """Devuelve una lista de todas las rutas almacenadas en el trie"""
        rutas = []
        self._obtener_rutas_recursivo(self.root, "", rutas)
        return rutas
    
    def _obtener_rutas_recursivo(self, node, prefijo, rutas):
        if node.route_info is not None:
            rutas.append((prefijo, node.route_info))
        
        for bit, child in node.children.items():
            self._obtener_rutas_recursivo(child, prefijo + bit, rutas)


# ====================
# Funciones auxiliares
# ====================
def ip_a_binario(ip: str) -> str:
    return bin(int(ipaddress.IPv4Address(ip)))[2:].zfill(32)


# ====================
# Tkinter App
# ====================
class RouterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enrutador con Trie de Prefijos IP")
        self.root.geometry("700x550")

        self.trie = IPTrie()
        self._crear_widgets()

    def _crear_widgets(self):
        frame = tb.Frame(self.root, padding=10)
        frame.pack(fill=BOTH, expand=YES)

        # --- Insertar prefijos ---
        tb.Label(frame, text="Agregar Prefijo (ej: 192.168.1.0/24):").pack(anchor=W, pady=(0,5))
        self.prefijo_entry = tb.Entry(frame, width=30)
        self.prefijo_entry.pack(anchor=W, pady=(0,10))

        tb.Label(frame, text="Interfaz (ej: Interfaz 1):").pack(anchor=W, pady=(0,5))
        self.interfaz_entry = tb.Entry(frame, width=30)
        self.interfaz_entry.pack(anchor=W, pady=(0,10))

        self.insertar_btn = tb.Button(frame, text="Agregar Prefijo", bootstyle="success-outline", command=self.agregar_prefijo)
        self.insertar_btn.pack(anchor=W, pady=(0,10))

        # --- Botón cargar ejemplo (CORREGIDO) ---
        self.ejemplo_btn = tb.Button(frame, text="Cargar Ejemplo", bootstyle="secondary-outline", command=self.cargar_ejemplo)
        self.ejemplo_btn.pack(anchor=W, pady=(0,10))

        # --- Botón mostrar rutas ---
        self.mostrar_btn = tb.Button(frame, text="Mostrar Todas las Rutas", bootstyle="info-outline", command=self.mostrar_rutas)
        self.mostrar_btn.pack(anchor=W, pady=(0,20))

        # --- Buscar IP destino ---
        tb.Label(frame, text="IP de Destino:").pack(anchor=W, pady=(0,5))
        self.destino_entry = tb.Entry(frame, width=30)
        self.destino_entry.pack(anchor=W, pady=(0,10))

        self.buscar_btn = tb.Button(frame, text="Buscar Ruta", bootstyle="primary-outline", command=self.buscar_ruta)
        self.buscar_btn.pack(anchor=W, pady=(0,20))

        # --- Resultado ---
        self.resultado_label = tb.Label(frame, text="", font=("Helvetica", 12, "bold"))
        self.resultado_label.pack(anchor=W, pady=(10,0))

        # --- Area de texto para mostrar rutas ---
        self.rutas_text = tb.Text(frame, height=8, width=70)
        self.rutas_text.pack(fill=BOTH, expand=YES, pady=(10,0))

    def agregar_prefijo(self):
        texto = self.prefijo_entry.get().strip()
        interfaz = self.interfaz_entry.get().strip()
        
        if not texto or not interfaz:
            self.resultado_label.config(text="ERROR: Prefijo o interfaz vacíos")
            return
            
        try:
            red = ipaddress.IPv4Network(texto, strict=False)
            ip_bin = ip_a_binario(str(red.network_address))
            self.trie.insertar_prefijo(ip_bin, red.prefixlen, interfaz)
            self.resultado_label.config(text=f"ÉXITO: Prefijo {texto} agregado a {interfaz}")
            
            # Limpiar los campos de entrada
            self.prefijo_entry.delete(0, tk.END)
            self.interfaz_entry.delete(0, tk.END)
            
        except Exception as e:
            self.resultado_label.config(text=f"ERROR: {e}")

    def cargar_ejemplo(self):
        """Carga rutas de ejemplo en el Trie"""
        ejemplos = [
            ("192.168.1.0/24", "Interfaz LAN-1"),
            ("192.168.2.0/24", "Interfaz LAN-2"),
            ("192.168.0.0/16", "Interfaz Regional"),
            ("10.0.0.0/8", "Interfaz Interna"),
            ("172.16.0.0/12", "Interfaz Privada"),
            ("0.0.0.0/0", "Gateway por Defecto"),
        ]
        
        contador = 0
        for prefijo, interfaz in ejemplos:
            try:
                red = ipaddress.IPv4Network(prefijo, strict=False)
                ip_bin = ip_a_binario(str(red.network_address))
                self.trie.insertar_prefijo(ip_bin, red.prefixlen, interfaz)
                contador += 1
            except Exception as e:
                print(f"Error cargando {prefijo}: {e}")
                
        self.resultado_label.config(text=f"ÉXITO: {contador} rutas de ejemplo cargadas")
        self.mostrar_rutas()

    def mostrar_rutas(self):
        """Muestra todas las rutas almacenadas en el trie"""
        rutas = self.trie.obtener_todas_rutas()
        self.rutas_text.delete(1.0, tk.END)
        
        if not rutas:
            self.rutas_text.insert(tk.END, "No hay rutas almacenadas en el trie.\n")
            return
            
        self.rutas_text.insert(tk.END, "=== TABLA DE RUTAS ===\n\n")
        for i, (binario, interfaz) in enumerate(rutas, 1):
            # Convertir binario de vuelta a notación CIDR para mostrar
            longitud = len(binario)
            if longitud <= 32:
                # Rellenar con ceros para completar 32 bits
                ip_completa = binario.ljust(32, '0')
                # Convertir a decimal
                ip_decimal = int(ip_completa, 2)
                ip_str = str(ipaddress.IPv4Address(ip_decimal))
                self.rutas_text.insert(tk.END, f"{i:2d}. {ip_str}/{longitud} -> {interfaz}\n")
        
        self.rutas_text.insert(tk.END, f"\nTotal: {len(rutas)} rutas almacenadas")

    def buscar_ruta(self):
        destino = self.destino_entry.get().strip()
        if not destino:
            self.resultado_label.config(text="ERROR: IP de destino vacía")
            return
            
        try:
            # Validar que sea una IP válida
            ipaddress.IPv4Address(destino)
            
            ip_bin = ip_a_binario(destino)
            interfaz = self.trie.buscar_ruta(ip_bin)
            
            if interfaz:
                self.resultado_label.config(text=f"RUTA ENCONTRADA: {destino} -> {interfaz}")
            else:
                self.resultado_label.config(text=f"SIN RUTA: No se encontró ruta para {destino}")
                
        except Exception as e:
            self.resultado_label.config(text=f"ERROR: IP inválida - {e}")


# ====================
# MAIN
# ====================
if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    RouterApp(app)
    app.mainloop()