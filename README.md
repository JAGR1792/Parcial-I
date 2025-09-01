# 📚 Parcial I – Estructuras de Datos  

Este repositorio contiene la implementación de **10 casos prácticos** utilizando **árboles N-arios** y **Tries**, organizados en módulos independientes y accesibles mediante una interfaz gráfica construida con **Tkinter** y **ttkbootstrap**.  

La aplicación permite ejecutar cada caso desde un menú principal, facilitando la exploración de los distintos usos de estas estructuras de datos.  

---

## ⚙️ Requisitos  

Este proyecto utiliza **Python 3.11+** y las siguientes librerías:  

- `tk`  
- `ttkbootstrap>=1.10.1`  
- `matplotlib>=3.9.0`  
- `numpy>=1.26.0`  

📥 Instalación rápida:  

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución  

Ejecuta el menú principal con:  

```bash
python main.py
```  

Se abrirá una **ventana gráfica** donde podrás elegir entre los **10 puntos implementados**.  

---

## 📂 Estructura del Proyecto  

```
Parcial-I/
│── main.py                 # Menú principal (Tkinter + ttkbootstrap)
│── requirements.txt        # Dependencias
│
├── punto1/consultas.txt
├── punto1/punto1.py        # Caso 1: Sistema de archivos jerárquico
├── punto2/diccionario.txt
├── punto2/punto2.py        # Caso 2: Diccionario multilingüe
├── punto3/punto3.py        # Caso 3: Autocompletado de buscador
├── punto4/punto4.py        # Caso 4: Enrutador de red
├── punto5/punto5.py        # Caso 5: Secuencias de ADN
├── punto6/punto6.py        # Caso 6: Censura de chats
├── punto7/punto7.py        # Caso 7: Organigrama empresarial
├── punto8/punto8.py        # Caso 8: Base de datos de ajedrez
├── punto9/punto9.py        # Caso 9: Árbol de sintaxis abstracta
├── punto10/punto10.py      # Caso 10: Sopas de letras
│
└── Ejemplo del pdf/Esqueleto.py
```

---

## 🧩 Casos de Uso Implementados  

### 🌳 Árbol N-ario  
- **Sistema de archivos jerárquico** – Representación de carpetas y archivos.  
- **Organigrama empresarial** – Jerarquía de empleados y subordinados.  
- **Árbol de sintaxis abstracta (AST)** – Representación de código fuente para compiladores.  

### 🔠 Trie  
- **Diccionario multilingüe** – Traducciones rápidas palabra por palabra.  
- **Autocompletado de buscador** – Sugerencias en tiempo real.  
- **Enrutador de red** – Selección de rutas por prefijos binarios de IP.  
- **Secuencias de ADN** – Búsqueda de patrones genéticos (K-mers).  
- **Censura de chats** – Filtro de palabras prohibidas en tiempo real.  
- **Base de datos de ajedrez** – Sugerencias de jugadas de apertura.  
- **Sopas de letras** – Búsqueda de palabras en una cuadrícula.  

---

## 📝 Conclusiones  

- **Trie** → Ideal para **búsquedas rápidas** en textos, secuencias y autocompletado **O(L)**.  
- **Árbol N-ario** → Perfecto para **jerarquías** (archivos, organigramas, compiladores).  

👉 Ambos tienen aplicaciones reales en **buscadores, redes, biomedicina, juegos y sistemas operativos**.  

---
