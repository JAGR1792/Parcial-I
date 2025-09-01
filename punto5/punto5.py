import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import random


# ====================
# Clase Trie y Nodo para ADN
# ====================
class DNATrieNode:
    def __init__(self):
        self.children = {}  # Solo A, C, G, T
        self.is_end_of_sequence = False
        self.positions = []  # posiciones donde aparece esta secuencia
        self.sequence_info = []  # información adicional de la secuencia


class DNATrie:
    def __init__(self):
        self.root = DNATrieNode()
        self.genome_length = 0

    def insert_sequence(self, sequence: str, position: int = 0, info: str = ""):
        """Inserta una secuencia de ADN en el Trie"""
        sequence = sequence.upper().strip()
        
        # Validar que solo contenga nucleótidos válidos
        if not all(c in 'ACGT' for c in sequence):
            return False
            
        node = self.root
        for nucleotide in sequence:
            if nucleotide not in node.children:
                node.children[nucleotide] = DNATrieNode()
            node = node.children[nucleotide]
        
        node.is_end_of_sequence = True
        node.positions.append(position)
        if info:
            node.sequence_info.append(info)
        return True

    def insert_kmers(self, genome: str, k: int = 6):
        """Indexa el genoma insertando todos los k-mers"""
        genome = genome.upper().strip()
        if not all(c in 'ACGT' for c in genome):
            return False
            
        self.genome_length = len(genome)
        
        for i in range(len(genome) - k + 1):
            kmer = genome[i:i+k]
            self.insert_sequence(kmer, i, f"k-mer en posición {i}")
        return True

    def search_sequence(self, sequence: str):
        """Busca una secuencia específica y retorna sus posiciones"""
        sequence = sequence.upper().strip()
        node = self.root
        
        for nucleotide in sequence:
            if nucleotide not in node.children:
                return []
            node = node.children[nucleotide]
        
        if node.is_end_of_sequence:
            return node.positions
        return []

    def find_patterns(self, prefix: str):
        """Encuentra todos los patrones que empiecen con el prefijo dado"""
        prefix = prefix.upper().strip()
        node = self.root
        
        for nucleotide in prefix:
            if nucleotide not in node.children:
                return []
            node = node.children[nucleotide]

        patterns = []
        self._collect_patterns(node, prefix, patterns)
        return patterns

    def _collect_patterns(self, node, current_sequence, patterns):
        """Recolecta recursivamente todos los patrones desde un nodo"""
        if node.is_end_of_sequence:
            patterns.append({
                'sequence': current_sequence,
                'positions': node.positions,
                'count': len(node.positions)
            })
        
        for nucleotide, child_node in node.children.items():
            self._collect_patterns(child_node, current_sequence + nucleotide, patterns)


# ====================
# Aplicación GUI para análisis de ADN
# ====================
class DNAAnalyzerApp:
    def __init__(self, root, dna_trie):
        self.dna_trie = dna_trie
        self.root = root
        self.root.title("Analizador de Secuencias de ADN con Trie")
        self.root.geometry("900x800")

        # Datos de ejemplo precargados
        self.sample_genomes = {
            "Fragmento E. coli (lacZ)": {
                "sequence": "ATGGCGAATTCGGATCCATGACCGAGTACAAGCCCACGGTGCGCCTCGCCACCCGCGACGACGTCCCCAGGGCCGTACGCACCCTCGCCGCCGCGTTCGCCGACTACCCCGCCACGCGCCACACCGTCGATCCGGACCGCCTCATGAAGATCCTCAACGTGAACGGCAGCGGCCTGAACGACCTGCTGGACCGCGTCGTCGCCGACTTCGCCGACGACAGCGCCTACGTCAACGGCGTCGTGAGCCTGAAGGACGGCAGCCCGAACCCGGACAGCGGCGTGACCGACGTCACCAACGGCAACTACGTCGGCAACACCGACGGCAACTACGTCAGCGTCACCGGCAACTACGTCAACGACACCGACGGCGGCCGCATGGATATCCTGGCCGACGTCGCCGACGACAGCGCCGACGACGCCGACGACGCCGACGTC",
                "description": "Fragmento del gen lacZ de E. coli con sitios de restricción EcoRI y BamHI"
            },
            "Secuencia Viral (HIV-1)": {
                "sequence": "ATGGGTGCGAGAGCGTCGGTATTAAGCGGGGAGAATTAGATCGATGGGAGAAAATTCGGTTACGGCCAGGGGGAAAGAAAAAATATCGATTAAAACATATAGTATGGGCAAGCAGGGAGCTGGACAGATTTGCACTTAACCCTGGCCTGTTAGAAACATCAGAAGGCTGTAGACAAATACTAGGACAGCTACAACCATCCCTTCAGACAGGATCAGAGGAACTTAAATCATTATATAATACAATAGCAACCCTCTATTGTGTACATCAAAGGATAGACATAAAAGACACCAAGGAAGCCTTAGACAAGATAGAGGAAGAGCAAAACAAAAGTAAGAAAAAGGCACAGCAAGCAGCAGCTGACACAGGACACAGCAATCAGGTCAGCCAAAATTACCCTATAGTGCAGAACCTCCAGGGGCAAATGGTACATCAGGCCATATCACCTAGAACTTTAAATGCATGGGTAAAAGTAGTAGAAGAGAAGGCTTTCAGCCCA",
                "description": "Fragmento del gen gag del VIH-1 (región estructural)"
            },
            "Promotor Humano (p53)": {
                "sequence": "CGGCGCGCCCGCGCGCCCGCGCGCCCGCGCGCCCGCGCGCCCGCGCGCCCGCGCGCCCGCGCGCCCGCGCGCCCGCGCGCCCGCGCGCCATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTATGGAAACTACTTCCTGAAAACAACGTTCTGTCCCCCTTGCCGTCCCAAGCAATGGATGATTTGATGCTGTCCCCGGACGATATTGAACAATGGTTCACTGAAGACCCAGGTCCAGATGAAGCTCCCAGAATGCCAGAGGCTGCTCCCCCCGTGGCCCCTGCACCAGCAGCTCCTACACCGGCGGCCCCTGCACCAGCCCCCTCCTGGCCCCTGTCATCTTCTGTCCCTTCCCAGAAAACCTACCAGGGCAGCTACGGTTTCCGTCTGGGCTTCTTGCATTCTGGGACAGCCAAGTCTGTGACTTGCACGTACTCCCCTGCCCTCAACAAGATGTTTTGCCAACTGGCCAAGACCTGCCCTGTGCAGCTGTGGGTTGATTCCACACCCCCGCCCGGCACCCGCGTCCGCGCCATGGCC",
                "description": "Región promotora del gen supresor de tumores p53 humano"
            },
            "Genoma Mitocondrial": {
                "sequence": "GATCACAGGTCTATCACCCTATTAACCACTCACGGGAGCTCTCCATGCATTTGGTATTTTCGTCTGGGGGGTGTGCACGCGATAGCATTGCGAGACGCTGGAGCCGGAGCACCCTATGTCGCAGTATCTGTCTTTGATTCCTGCCTCATTCTATTATTTATCGCACCTACGTTCAATATTACAGGCGAACATACCTACTAAAGTGTGTTAATTAATTAATGCTTGTAGGACATAATAATAACAATTGAATGTCTGCACAGCCACTTTCCACACAGACATCATAACAAAAAATTTCCACCAAACCCCCCCCTCCCCCCGCTTCTGGCCACAGCACTTAAACACATCTCTGCCAAACCCCAAAAACAAAGAACCCTAACACCAGCCTAACCAGATTTCAAATTTTATCTTTTGGCGGTATGCACTTTTAACAGTCACCCCCCAACTAACACATTATTTTCCCCTCCCACTCCCATACTACTAATCTCATCAATACAACCCCCGCCCATCCTACCCAGCACACACACACCGCTGCTAACCCCATACCCCGAACCAACCAAACCCCAAAGACACCCCCCACAG",
                "description": "Fragmento del genoma mitocondrial humano (región control)"
            }
        }

        # Frame principal
        main_frame = tb.Frame(root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # Título
        title = tb.Label(main_frame, text="🧬 Analizador de Secuencias de ADN", 
                        font=("Helvetica", 16, "bold"))
        title.pack(pady=10)

        # Frame para cargar genoma
        genome_frame = tb.LabelFrame(main_frame, text="Genoma de Referencia", padding=10)
        genome_frame.pack(fill=X, pady=5)

        # Área de texto para el genoma
        self.genome_text = tk.Text(genome_frame, height=4, width=80, 
                                 font=("Courier", 10), wrap=tk.WORD)
        self.genome_text.pack(pady=5)

        # Botones para genoma
        genome_buttons_frame1 = tb.Frame(genome_frame)
        genome_buttons_frame1.pack(pady=5)

        tb.Button(genome_buttons_frame1, text="Generar Aleatorio", 
                 bootstyle="info", command=self.generate_random_genome).pack(side=LEFT, padx=3)
        
        tb.Button(genome_buttons_frame1, text="Indexar Genoma (k=6)", 
                 bootstyle="success", command=self.index_genome).pack(side=LEFT, padx=3)

        # Dropdown para ejemplos precargados
        sample_frame = tb.Frame(genome_frame)
        sample_frame.pack(pady=5, fill=X)

        tb.Label(sample_frame, text="Ejemplos precargados:").pack(side=LEFT, padx=5)
        self.sample_var = tk.StringVar(value="Seleccionar ejemplo...")
        self.sample_combo = tb.Combobox(sample_frame, textvariable=self.sample_var, 
                                       values=list(self.sample_genomes.keys()), 
                                       state="readonly", width=40)
        self.sample_combo.pack(side=LEFT, padx=5)
        
        tb.Button(sample_frame, text="Cargar Ejemplo", 
                 bootstyle="warning", command=self.load_sample_genome).pack(side=LEFT, padx=3)

        # Frame para búsqueda con ejemplos
        search_frame = tb.LabelFrame(main_frame, text="Búsqueda de Secuencias", padding=10)
        search_frame.pack(fill=X, pady=10)

        # Ejemplos de búsquedas comunes
        examples_frame = tb.Frame(search_frame)
        examples_frame.pack(fill=X, pady=(0, 5))
        
        tb.Label(examples_frame, text="Búsquedas comunes:", font=("Helvetica", 10, "bold")).pack(anchor=W)
        
        examples_buttons_frame = tb.Frame(examples_frame)
        examples_buttons_frame.pack(fill=X, pady=2)
        
        # Botones de ejemplo
        example_searches = [
            ("ATG", "Codón inicio", "info"),
            ("GAATTC", "Sitio EcoRI", "success"),
            ("GGATCC", "Sitio BamHI", "warning"),
            ("TATA", "Caja TATA", "danger"),
            ("CGCG", "CpG islands", "secondary")
        ]
        
        for search, desc, style in example_searches:
            btn = tb.Button(examples_buttons_frame, text=f"{search} ({desc})", 
                           bootstyle=f"{style}-outline", 
                           command=lambda s=search: self.set_search_example(s))
            btn.pack(side=LEFT, padx=2, pady=2)

        # Entrada para secuencia de búsqueda
        tb.Label(search_frame, text="Secuencia a buscar (solo A, C, G, T):").pack(anchor=W, pady=(10,0))
        self.search_entry = tb.Entry(search_frame, width=50, bootstyle="primary")
        self.search_entry.pack(pady=5, fill=X)
        self.search_entry.bind("<KeyRelease>", self.update_suggestions)

        # Botones de búsqueda
        search_buttons = tb.Frame(search_frame)
        search_buttons.pack(pady=5)

        tb.Button(search_buttons, text="Búsqueda Exacta", 
                 bootstyle="primary-outline", command=self.exact_search).pack(side=LEFT, padx=5)
        
        tb.Button(search_buttons, text="Buscar Patrones", 
                 bootstyle="warning-outline", command=self.pattern_search).pack(side=LEFT, padx=5)

        # Listbox para sugerencias
        tb.Label(search_frame, text="Patrones encontrados:").pack(anchor=W, pady=(10,0))
        self.suggestions_listbox = tk.Listbox(search_frame, width=80, height=6, 
                                            font=("Courier", 10), bg="white", 
                                            fg="#333", selectbackground="#cce5ff")
        self.suggestions_listbox.pack(pady=5, fill=X)

        # Frame para resultados
        results_frame = tb.LabelFrame(main_frame, text="Resultados del Análisis", padding=10)
        results_frame.pack(fill=BOTH, expand=YES, pady=5)

        self.results_text = tk.Text(results_frame, height=10, width=80, 
                                  font=("Courier", 10), wrap=tk.WORD,
                                  bg="#f8f9fa", fg="#333")
        self.results_text.pack(fill=BOTH, expand=YES)

        # Scrollbar para resultados
        scrollbar = tb.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.results_text.config(yscrollcommand=scrollbar.set)

        # Frame para estadísticas
        stats_frame = tb.Frame(main_frame)
        stats_frame.pack(fill=X, pady=5)

        self.stats_label = tb.Label(stats_frame, text="Genoma no cargado", 
                                   font=("Helvetica", 10), bootstyle="info")
        self.stats_label.pack()

        # Inicializar con datos de ejemplo para demostración
        self.load_demo_data()

    def load_demo_data(self):
        """Carga datos de demostración al iniciar"""
        demo_genome = self.sample_genomes["Fragmento E. coli (lacZ)"]
        self.genome_text.insert(1.0, demo_genome["sequence"])
        
        # Auto-indexar para demostración
        self.dna_trie.insert_kmers(demo_genome["sequence"], k=6)
        self.stats_label.config(text=f"Demo cargado: {len(demo_genome['sequence'])} nucleótidos, k-mers de 6")
        
        self.results_text.insert(tk.END, "🎯 DEMO PRECARGADO - Fragmento lacZ de E. coli\n")
        self.results_text.insert(tk.END, "="*50 + "\n")
        self.results_text.insert(tk.END, f"📋 {demo_genome['description']}\n")
        self.results_text.insert(tk.END, f"🧬 Longitud: {len(demo_genome['sequence'])} nucleótidos\n")
        self.results_text.insert(tk.END, f"🔍 K-mers indexados: {len(demo_genome['sequence'])-5}\n\n")
        
        self.results_text.insert(tk.END, "💡 PRUEBAS SUGERIDAS:\n")
        self.results_text.insert(tk.END, "• ATG - Buscar codones de inicio\n")
        self.results_text.insert(tk.END, "• GAATTC - Sitio de restricción EcoRI\n")
        self.results_text.insert(tk.END, "• GGATCC - Sitio de restricción BamHI\n")
        self.results_text.insert(tk.END, "• GCG - Buscar patrones ricos en GC\n")
        self.results_text.insert(tk.END, "• CGC - Dinucleótidos CpG\n\n")
        self.results_text.insert(tk.END, "🚀 ¡Listo para usar! Prueba las búsquedas de ejemplo.\n\n")

    def set_search_example(self, sequence):
        """Establece un ejemplo de búsqueda en el campo de entrada"""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, sequence)
        # Actualizar sugerencias automáticamente
        self.update_suggestions()

    def load_sample_genome(self):
        """Carga un genoma de ejemplo seleccionado"""
        selected = self.sample_var.get()
        if selected in self.sample_genomes:
            sample = self.sample_genomes[selected]
            
            # Limpiar y cargar nuevo genoma
            self.genome_text.delete(1.0, tk.END)
            self.genome_text.insert(1.0, sample["sequence"])
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"✅ EJEMPLO CARGADO: {selected}\n")
            self.results_text.insert(tk.END, "="*60 + "\n")
            self.results_text.insert(tk.END, f"📋 Descripción: {sample['description']}\n")
            self.results_text.insert(tk.END, f"🧬 Longitud: {len(sample['sequence'])} nucleótidos\n\n")
            self.results_text.insert(tk.END, "➡️ Presiona 'Indexar Genoma' para empezar a buscar.\n\n")
            
            # Mostrar contenido del genoma formateado
            self.results_text.insert(tk.END, "🔬 CONTENIDO DE LA SECUENCIA:\n")
            sequence = sample["sequence"]
            for i in range(0, len(sequence), 60):
                line_num = f"{i+1:>4}: "
                line = sequence[i:i+60]
                self.results_text.insert(tk.END, line_num + line + "\n")
            
            self.results_text.insert(tk.END, "\n" + "="*60 + "\n\n")

    def generate_random_genome(self):
        """Genera un genoma aleatorio para pruebas"""
        nucleotides = ['A', 'C', 'G', 'T']
        length = random.randint(300, 600)
        genome = ''.join(random.choice(nucleotides) for _ in range(length))
        
        # Insertar algunos patrones conocidos para pruebas
        patterns = [
            ("ATGCGT", "Secuencia sintética"),
            ("GAATTC", "Sitio EcoRI"),
            ("GGATCC", "Sitio BamHI"), 
            ("TTAGGC", "Secuencia telómero"),
            ("CCCGGG", "Sitio SmaI"),
            ("AAGCTT", "Sitio HindIII")
        ]
        
        inserted_patterns = []
        for pattern, desc in patterns:
            if random.random() > 0.3:  # 70% probabilidad de insertar cada patrón
                pos = random.randint(50, length-50)
                genome = genome[:pos] + pattern + genome[pos+len(pattern):]
                inserted_patterns.append(f"{pattern} ({desc})")
        
        self.genome_text.delete(1.0, tk.END)
        self.genome_text.insert(1.0, genome)
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🎲 GENOMA ALEATORIO GENERADO\n")
        self.results_text.insert(tk.END, "="*40 + "\n")
        self.results_text.insert(tk.END, f"🧬 Longitud: {len(genome)} nucleótidos\n")
        self.results_text.insert(tk.END, f"🎯 Patrones insertados: {len(inserted_patterns)}\n\n")
        
        if inserted_patterns:
            self.results_text.insert(tk.END, "🔍 PATRONES GARANTIZADOS:\n")
            for pattern in inserted_patterns:
                self.results_text.insert(tk.END, f"  • {pattern}\n")
        
        self.results_text.insert(tk.END, f"\n➡️ Presiona 'Indexar Genoma' para continuar.\n\n")

    def index_genome(self):
        """Indexa el genoma usando k-mers"""
        genome = self.genome_text.get(1.0, tk.END).strip()
        
        if not genome:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "❌ Error: No hay genoma para indexar\n")
            return

        # Limpiar el Trie anterior
        self.dna_trie = DNATrie()
        
        if self.dna_trie.insert_kmers(genome, k=6):
            self.stats_label.config(text=f"Genoma indexado: {len(genome)} nucleótidos, k-mers de 6")
            
            # Análisis básico del genoma
            a_count = genome.count('A')
            c_count = genome.count('C')
            g_count = genome.count('G')
            t_count = genome.count('T')
            gc_content = (c_count + g_count) / len(genome) * 100
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"✅ GENOMA INDEXADO EXITOSAMENTE\n")
            self.results_text.insert(tk.END, "="*45 + "\n")
            self.results_text.insert(tk.END, f"🧬 Longitud total: {len(genome)} nucleótidos\n")
            self.results_text.insert(tk.END, f"🔍 K-mers generados: {len(genome)-5}\n")
            self.results_text.insert(tk.END, f"📊 Contenido GC: {gc_content:.1f}%\n\n")
            
            self.results_text.insert(tk.END, f"📈 COMPOSICIÓN DE NUCLEÓTIDOS:\n")
            self.results_text.insert(tk.END, f"  A: {a_count:4d} ({a_count/len(genome)*100:.1f}%)\n")
            self.results_text.insert(tk.END, f"  C: {c_count:4d} ({c_count/len(genome)*100:.1f}%)\n")
            self.results_text.insert(tk.END, f"  G: {g_count:4d} ({g_count/len(genome)*100:.1f}%)\n")
            self.results_text.insert(tk.END, f"  T: {t_count:4d} ({t_count/len(genome)*100:.1f}%)\n\n")
            
            # Buscar algunos patrones comunes automáticamente
            common_patterns = ["ATG", "GAATTC", "GGATCC", "TATA", "CGCG"]
            self.results_text.insert(tk.END, f"🔍 ANÁLISIS RÁPIDO DE PATRONES COMUNES:\n")
            for pattern in common_patterns:
                positions = self.dna_trie.search_sequence(pattern)
                count = len(positions)
                if count > 0:
                    self.results_text.insert(tk.END, f"  {pattern}: {count} ocurrencias\n")
                else:
                    self.results_text.insert(tk.END, f"  {pattern}: No encontrado\n")
            
            self.results_text.insert(tk.END, f"\n🚀 ¡Listo para búsquedas! Usa los botones de ejemplo arriba.\n\n")
        else:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "❌ Error: El genoma contiene caracteres inválidos\n")
            self.results_text.insert(tk.END, "   Solo se permiten nucleótidos: A, C, G, T\n")

    def update_suggestions(self, event=None):
        """Actualiza las sugerencias mientras se escribe"""
        prefix = self.search_entry.get().upper()
        self.suggestions_listbox.delete(0, tk.END)

        if len(prefix) >= 2:  # Solo mostrar sugerencias para prefijos de al menos 2 caracteres
            patterns = self.dna_trie.find_patterns(prefix)[:10]  # Limitar a 10 sugerencias
            for pattern in patterns:
                display = f"{pattern['sequence']} (aparece {pattern['count']} veces)"
                self.suggestions_listbox.insert(tk.END, display)

    def exact_search(self):
        """Realiza búsqueda exacta de una secuencia"""
        sequence = self.search_entry.get().upper().strip()
        
        if not sequence:
            return

        if not all(c in 'ACGT' for c in sequence):
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "❌ Error: La secuencia solo debe contener A, C, G, T\n")
            return

        positions = self.dna_trie.search_sequence(sequence)
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🔍 BÚSQUEDA EXACTA: {sequence}\n")
        self.results_text.insert(tk.END, "="*50 + "\n\n")
        
        if positions:
            self.results_text.insert(tk.END, f"✅ Secuencia encontrada en {len(positions)} posiciones:\n")
            for i, pos in enumerate(positions[:20]):  # Mostrar máximo 20 posiciones
                self.results_text.insert(tk.END, f"  Posición {pos}\n")
            if len(positions) > 20:
                self.results_text.insert(tk.END, f"  ... y {len(positions)-20} posiciones más\n")
        else:
            self.results_text.insert(tk.END, "❌ Secuencia no encontrada en el genoma indexado\n")

    def pattern_search(self):
        """Busca todos los patrones que empiecen con la secuencia dada"""
        prefix = self.search_entry.get().upper().strip()
        
        if not prefix:
            return

        if not all(c in 'ACGT' for c in prefix):
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "❌ Error: La secuencia solo debe contener A, C, G, T\n")
            return

        patterns = self.dna_trie.find_patterns(prefix)
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🔍 BÚSQUEDA DE PATRONES: {prefix}*\n")
        self.results_text.insert(tk.END, "="*50 + "\n\n")
        
        if patterns:
            total_occurrences = sum(p['count'] for p in patterns)
            self.results_text.insert(tk.END, f"✅ Encontrados {len(patterns)} patrones únicos ")
            self.results_text.insert(tk.END, f"con {total_occurrences} ocurrencias totales:\n\n")
            
            # Ordenar por frecuencia
            patterns.sort(key=lambda x: x['count'], reverse=True)
            
            for pattern in patterns[:30]:  # Mostrar máximo 30 patrones
                self.results_text.insert(tk.END, f"  {pattern['sequence']} → {pattern['count']} veces\n")
            
            if len(patterns) > 30:
                self.results_text.insert(tk.END, f"  ... y {len(patterns)-30} patrones más\n")
        else:
            self.results_text.insert(tk.END, f"❌ No se encontraron patrones que empiecen con '{prefix}'\n")


# ====================
# Main
# ====================
if __name__ == "__main__":
    # Crear Trie para ADN
    dna_trie = DNATrie()
    
    # Crear ventana principal
    app = tb.Window(themename="flatly")
    DNAAnalyzerApp(app, dna_trie)
    app.mainloop()