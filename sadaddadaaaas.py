import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

# --- CONFIGURACIÓN Y BASE DE DATOS ---
def inicializar_db():
    conn = sqlite3.connect("sistema_completo.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT, 
            articulo TEXT, 
            descripcion TEXT,
            cantidad INTEGER,
            solicitado TEXT,
            fecha_hora TEXT
        )
    """)
    conn.commit()
    conn.close()

class SistemaInventario:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventario Fe y Alegría")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f4f4f4")

        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[10, 5])

        nav = tk.Frame(self.root, bg="#da251d", height=60)
        nav.pack(fill="x")
        tk.Label(nav, text="SISTEMA DE CONTROL DE INVENTARIO", fg="white", bg="#da251d", font=("Arial", 16, "bold")).pack(pady=15)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_disponibles = tk.Frame(self.notebook, bg="#f4f4f4")
        self.tab_inventario = tk.Frame(self.notebook, bg="#f4f4f4")
        self.tab_registro = tk.Frame(self.notebook, bg="#f4f4f4")
        
        self.notebook.add(self.tab_registro, text=" ➕ AGREGAR ARTÍCULO ")
        self.notebook.add(self.tab_disponibles, text=" 📦 ARTÍCULOS DISPONIBLES ")
        self.notebook.add(self.tab_inventario, text=" 📋 HISTORIAL COMPLETO ")

        self.setup_tab_disponibles()
        self.setup_tab_inventario()
        self.setup_tab_registro()
        self.cargar_datos()

    # --- PESTAÑA 1: DISPONIBLES ---
    def setup_tab_disponibles(self):
        frame_top = tk.Frame(self.tab_disponibles, bg="#f4f4f4")
        frame_top.pack(fill="x", padx=20, pady=10)

        # En la pestaña de Disponibles
        tk.Label(frame_top, text="🔍 Buscar (Código o Nombre):", font=("Arial", 10, "bold"), bg="#f4f4f4").pack(side="left")
        self.ent_busqueda = tk.Entry(frame_top, font=("Arial", 11))
        self.ent_busqueda.pack(side="left", padx=10, fill="x", expand=True)
        # Esta línea es clave: llama a cargar_datos cada vez que escribes
        self.ent_busqueda.bind("<KeyRelease>", lambda e: self.cargar_datos())

        cols = ("CÓDIGO", "ARTÍCULO", "TOTAL DISPONIBLE")
        self.tabla_disp = ttk.Treeview(self.tab_disponibles, columns=cols, show="headings")
        for col in cols:
            self.tabla_disp.heading(col, text=col)
            self.tabla_disp.column(col, anchor="center")
        self.tabla_disp.pack(fill="both", expand=True, padx=20)

        frame_btns = tk.Frame(self.tab_disponibles, bg="#f4f4f4")
        frame_btns.pack(fill="x", pady=20)

        tk.Button(frame_btns, text="➖ SOLICITAR ARTÍCULO", command=lambda: self.ventana_movimiento("RESTAR"), 
                  bg="#ffc107", font=("Arial", 11, "bold"), width=25, pady=10).pack(side="left", padx=100)
        
        tk.Button(frame_btns, text="➕ DEVOLVER ARTÍCULO", command=lambda: self.ventana_movimiento("SUMAR"), 
                  bg="#28a745", fg="white", font=("Arial", 11, "bold"), width=25, pady=10).pack(side="right", padx=100)

    # --- VENTANA EMERGENTE PERSONALIZADA ---
    def ventana_movimiento(self, tipo):
        sel = self.tabla_disp.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un artículo de la lista.")
            return
        
        item = self.tabla_disp.item(sel)['values']
        cod, art, stock_actual = item[0], item[1], int(item[2])

        # Crear Ventana
        v = tk.Toplevel(self.root)
        v.title(f"Registrar {tipo}")
        v.geometry("400x450")
        v.configure(padx=20, pady=20)
        v.transient(self.root) # Mantener arriba
        v.grab_set()

        titulo = "SOLICITUD DE SALIDA" if tipo == "RESTAR" else "REGISTRO DE DEVOLUCIÓN"
        color = "#da251d" if tipo == "RESTAR" else "#28a745"
        
        tk.Label(v, text=titulo, font=("Arial", 12, "bold"), fg=color).pack(pady=10)
        tk.Label(v, text=f"Artículo: {art} ({cod})", font=("Arial", 10, "italic")).pack()
        
        # Campos
        tk.Label(v, text="\nCantidad:").pack(anchor="w")
        ent_c = tk.Entry(v, font=("Arial", 11)); ent_c.pack(fill="x")
        
        tk.Label(v, text="\nDescripción/Motivo:").pack(anchor="w")
        ent_d = tk.Entry(v, font=("Arial", 11)); ent_d.pack(fill="x")
        
        tk.Label(v, text="\nNombre del Responsable:").pack(anchor="w")
        ent_r = tk.Entry(v, font=("Arial", 11)); ent_r.pack(fill="x")

        def procesar():
            try:
                cantidad = int(ent_c.get().strip())
                desc = ent_d.get().strip()
                resp = ent_r.get().strip()

                if cantidad <= 0: raise ValueError
                
                # Si es resta, verificar stock y negativizar
                if tipo == "RESTAR":
                    if cantidad > stock_actual:
                        messagebox.showerror("Error", f"No hay suficiente stock. Disponible: {stock_actual}")
                        return
                    cantidad = -cantidad
                
                # Guardar
                fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                conn = sqlite3.connect("sistema_completo.db")
                conn.execute("""
                    INSERT INTO inventario (codigo, articulo, descripcion, cantidad, solicitado, fecha_hora)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (cod, art, desc, cantidad, resp, fecha))
                conn.commit()
                conn.close()
                
                self.cargar_datos()
                v.destroy()
                messagebox.showinfo("Éxito", "Movimiento registrado.")
            except:
                messagebox.showerror("Error", "Verifique que la cantidad sea un número válido.")

        tk.Button(v, text="CONFIRMAR", bg=color, fg="white", font=("Arial", 11, "bold"), command=procesar).pack(pady=30, fill="x")

    # --- PESTAÑA 2: HISTORIAL ---
    def setup_tab_inventario(self):
        columnas = ("ID", "CÓDIGO", "ARTÍCULO", "CANT", "DESCRIPCIÓN", "FECHA/HORA", "SOLICITADO")
        self.tabla_hist = ttk.Treeview(self.tab_inventario, columns=columnas, show="headings")
        for col in columnas:
            self.tabla_hist.heading(col, text=col)
            self.tabla_hist.column(col, anchor="center", width=100)
        self.tabla_hist.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(self.tab_inventario, text="🗑️ ELIMINAR REGISTRO SELECCIONADO", command=self.borrar, bg="#dc3545", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

    # --- PESTAÑA 3: REGISTRO NUEVO ---
    def setup_tab_registro(self):
        frame_reg = tk.Frame(self.tab_registro, bg="white", bd=1, relief="solid")
        frame_reg.place(relx=0.5, rely=0.4, anchor="center", width=500, height=380)

        tk.Label(frame_reg, text="AGREGAR ARTÍCULO (Ingreso Inicial)", font=("Arial", 12, "bold"), bg="white").pack(pady=20)
        self.inputs = {}
        for label in ["Código", "Artículo", "Cantidad"]:
            f = tk.Frame(frame_reg, bg="white")
            f.pack(fill="x", padx=40, pady=5)
            tk.Label(f, text=label+":", bg="white", width=12, anchor="w").pack(side="left")
            entry = tk.Entry(f, font=("Arial", 11)); entry.pack(side="right", fill="x", expand=True)
            self.inputs[label] = entry

        tk.Button(frame_reg, text="💾 GUARDAR ARTÍCULO", command=self.alta_nueva, bg="#28a745", fg="white", font=("Arial", 11, "bold"), pady=10).pack(fill="x", padx=40, pady=25)

    def alta_nueva(self):
        desc = simpledialog.askstring("Descripción", "Descripción inicial del artículo:")
        if desc:
            try:
                cod = self.inputs["Código"].get()
                art = self.inputs["Artículo"].get()
                can = int(self.inputs["Cantidad"].get())
                resp = self.inputs["Responsable"].get()
                fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                conn = sqlite3.connect("sistema_completo.db")
                conn.execute("INSERT INTO inventario (codigo, articulo, descripcion, cantidad, solicitado, fecha_hora) VALUES (?,?,?,?,?,?)",
                            (cod, art, desc, can, resp, fecha))
                conn.commit()
                conn.close()
                self.cargar_datos()
                messagebox.showinfo("Éxito", "Artículo dado de alta.")
            except: messagebox.showerror("Error", "Revisar cantidad.")

    # --- CARGA DE DATOS ---
    def cargar_datos(self):
        # Historial
        for i in self.tabla_hist.get_children(): self.tabla_hist.delete(i)
        conn = sqlite3.connect("sistema_completo.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario ORDER BY id DESC")
        for fila in cursor.fetchall(): self.tabla_hist.insert("", tk.END, values=fila)
        
        # Disponibles
        for i in self.tabla_disp.get_children(): self.tabla_disp.delete(i)
        busqueda = self.ent_busqueda.get()
        cursor.execute("""
            SELECT codigo, articulo, SUM(cantidad) 
            FROM inventario 
            WHERE codigo LIKE ? 
            GROUP BY codigo
        """, (f'%{busqueda}%',))
        for fila in cursor.fetchall(): self.tabla_disp.insert("", tk.END, values=fila)
        conn.close()

    def borrar(self):
        sel = self.tabla_hist.selection()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar este registro?"):
            id_db = self.tabla_hist.item(sel)['values'][0]
            conn = sqlite3.connect("sistema_completo.db")
            conn.execute("DELETE FROM inventario WHERE id = ?", (id_db,))
            conn.commit()
            conn.close()
            self.cargar_datos()

if __name__ == "__main__":
    inicializar_db()
    root = tk.Tk()
    SistemaInventario(root)
    root.mainloop()
