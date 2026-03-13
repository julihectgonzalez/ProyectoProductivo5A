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

        self.tab_registro = tk.Frame(self.notebook, bg="#f4f4f4")
        self.tab_disponibles = tk.Frame(self.notebook, bg="#f4f4f4")
        self.tab_danados_frame = tk.Frame(self.notebook, bg="#f4f4f4")
        self.tab_inventario = tk.Frame(self.notebook, bg="#f4f4f4")
        
        self.notebook.add(self.tab_registro, text=" ➕ AGREGAR ARTÍCULO ")
        self.notebook.add(self.tab_disponibles, text=" 📦 ARTÍCULOS DISPONIBLES ")
        self.notebook.add(self.tab_danados_frame, text=" ❌ ARTÍCULOS DAÑADOS ")
        self.notebook.add(self.tab_inventario, text=" 📋 HISTORIAL COMPLETO ")

        self.setup_tab_registro()
        self.setup_tab_disponibles()
        self.setup_tab_danados()
        self.setup_tab_inventario()
        self.cargar_datos()

    def obtener_siguiente_codigo(self):
        """Busca el código más alto y devuelve el siguiente número"""
        try:
            conn = sqlite3.connect("sistema_completo.db")
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(CAST(codigo AS INTEGER)) FROM inventario")
            max_cod = cursor.fetchone()[0]
            conn.close()
            return str(max_cod + 1) if max_cod is not None else "1"
        except:
            return "1"

    def setup_tab_danados(self):
        cols = ("CÓDIGO", "ARTÍCULO", "CANT. TOTAL DAÑADA")
        self.tabla_danados = ttk.Treeview(self.tab_danados_frame, columns=cols, show="headings")
        for col in cols:
            self.tabla_danados.heading(col, text=col)
            self.tabla_danados.column(col, anchor="center")
        self.tabla_danados.pack(fill="both", expand=True, padx=20, pady=20)

    def setup_tab_disponibles(self):
        frame_top = tk.Frame(self.tab_disponibles, bg="#f4f4f4")
        frame_top.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_top, text="🔍 Buscar:", font=("Arial", 10, "bold"), bg="#f4f4f4").pack(side="left")
        self.ent_busqueda = tk.Entry(frame_top, font=("Arial", 11))
        self.ent_busqueda.pack(side="left", padx=10, fill="x", expand=True)
        self.ent_busqueda.bind("<KeyRelease>", lambda e: self.cargar_datos())

        cols = ("CÓDIGO", "ARTÍCULO", "STOCK ACTUAL")
        self.tabla_disp = ttk.Treeview(self.tab_disponibles, columns=cols, show="headings")
        for col in cols:
            self.tabla_disp.heading(col, text=col)
            self.tabla_disp.column(col, anchor="center")
        self.tabla_disp.pack(fill="both", expand=True, padx=20)

        frame_btns = tk.Frame(self.tab_disponibles, bg="#f4f4f4")
        frame_btns.pack(fill="x", pady=20)

        tk.Button(frame_btns, text="➖ SOLICITAR", command=lambda: self.ventana_movimiento("RESTAR"), 
                  bg="#ffc107", font=("Arial", 10, "bold"), width=15).pack(side="left", padx=20)
        
        tk.Button(frame_btns, text="➕ DEVOLVER", command=lambda: self.ventana_movimiento("SUMAR"), 
                  bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=15).pack(side="left", padx=20)
        
        tk.Button(frame_btns, text="⚠️ DAÑADO", command=lambda: self.ventana_movimiento("DAÑADO"), 
                  bg="#dc3545", fg="white", font=("Arial", 10, "bold"), width=15).pack(side="left", padx=20)

    def ventana_movimiento(self, tipo):
        sel = self.tabla_disp.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un artículo de la lista.")
            return
        
        item = self.tabla_disp.item(sel)['values']
        cod, art, stock_actual = str(item[0]), item[1], int(item[2])

        v = tk.Toplevel(self.root)
        v.title(f"Registrar {tipo}")
        v.geometry("400x450")
        v.transient(self.root)
        v.grab_set()

        color = "#dc3545" if tipo == "DAÑADO" else ("#ffc107" if tipo == "RESTAR" else "#28a745")
        titulo = "REPORTAR DAÑO" if tipo == "DAÑADO" else ("SOLICITAR ARTÍCULO" if tipo == "RESTAR" else "DEVOLUCIÓN")
        
        tk.Label(v, text=titulo, font=("Arial", 12, "bold"), fg=color).pack(pady=10)
        tk.Label(v, text=f"Artículo: {art}\nStock Disponible: {stock_actual}", font=("Arial", 10)).pack()
        
        tk.Label(v, text="\nCantidad:").pack(anchor="w", padx=40)
        ent_c = tk.Entry(v, font=("Arial", 11)); ent_c.pack(fill="x", padx=40)
        
        tk.Label(v, text="\nObservación:").pack(anchor="w", padx=40)
        ent_d = tk.Entry(v, font=("Arial", 11)); ent_d.pack(fill="x", padx=40)
        
        tk.Label(v, text="\nResponsable:").pack(anchor="w", padx=40)
        ent_r = tk.Entry(v, font=("Arial", 11)); ent_r.pack(fill="x", padx=40)

        def procesar():
            try:
                cant_input = int(ent_c.get().strip())
                desc = ent_d.get().strip()
                resp = ent_r.get().strip()

                if cant_input <= 0: raise ValueError
                
                if tipo in ["RESTAR", "DAÑADO"] and cant_input > stock_actual:
                    messagebox.showerror("Error", "No hay suficiente stock.")
                    return

                conn = sqlite3.connect("sistema_completo.db")
                prefix = "SOLICITUD: " if tipo == "RESTAR" else ("DAÑADO: " if tipo == "DAÑADO" else "DEVOLUCIÓN: ")
                final_cant = -cant_input if tipo in ["RESTAR", "DAÑADO"] else cant_input

                conn.execute("""
                    INSERT INTO inventario (codigo, articulo, descripcion, cantidad, solicitado, fecha_hora) 
                    VALUES (?,?,?,?,?,?)
                """, (cod, art, prefix + desc, final_cant, resp, datetime.now().strftime("%d/%m/%Y %H:%M")))
                
                conn.commit()
                conn.close()
                self.cargar_datos()
                v.destroy()
                messagebox.showinfo("Éxito", "Movimiento registrado.")
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida.")

        tk.Button(v, text="CONFIRMAR", bg=color, fg="white" if color!="#ffc107" else "black", 
                  font=("Arial", 11, "bold"), command=procesar).pack(pady=30, fill="x", padx=40)

    def cargar_datos(self):
        conn = sqlite3.connect("sistema_completo.db")
        cursor = conn.cursor()

        # 1. Historial
        for i in self.tabla_hist.get_children(): self.tabla_hist.delete(i)
        cursor.execute("SELECT * FROM inventario ORDER BY id DESC")
        for fila in cursor.fetchall(): self.tabla_hist.insert("", tk.END, values=fila)
        
        # 2. Disponibles
        for i in self.tabla_disp.get_children(): self.tabla_disp.delete(i)
        busq = f'%{self.ent_busqueda.get()}%'
        cursor.execute("""
            SELECT codigo, MAX(articulo), SUM(cantidad) 
            FROM inventario 
            WHERE codigo LIKE ? OR articulo LIKE ?
            GROUP BY codigo
            HAVING SUM(cantidad) != 0
        """, (busq, busq))
        
        for fila in cursor.fetchall():
            self.tabla_disp.insert("", tk.END, values=fila)

        # 3. Dañados
        for i in self.tabla_danados.get_children(): self.tabla_danados.delete(i)
        cursor.execute("""
            SELECT codigo, MAX(articulo), SUM(ABS(cantidad)) 
            FROM inventario 
            WHERE descripcion LIKE 'DAÑADO:%' 
            GROUP BY codigo
        """)
        for fila in cursor.fetchall():
            self.tabla_danados.insert("", tk.END, values=fila)
        
        conn.close()

    def setup_tab_inventario(self):
        columnas = ("ID", "CÓDIGO", "ARTÍCULO", "DESCRIPCIÓN", "CANTIDAD", "RESPONSABLE", "FECHA/HORA")
        self.tabla_hist = ttk.Treeview(self.tab_inventario, columns=columnas, show="headings")
        for col in columnas:
            self.tabla_hist.heading(col, text=col)
            self.tabla_hist.column(col, anchor="center", width=100)
        self.tabla_hist.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(self.tab_inventario, text="🗑️ ELIMINAR REGISTRO", command=self.borrar, 
                  bg="#dc3545", fg="white", font=("Arial", 10, "bold")).pack(pady=5)

    def setup_tab_registro(self):
        frame_reg = tk.Frame(self.tab_registro, bg="white", bd=1, relief="solid")
        frame_reg.place(relx=0.5, rely=0.4, anchor="center", width=500, height=380)

        tk.Label(frame_reg, text="INGRESO INICIAL DE ARTÍCULO", font=("Arial", 12, "bold"), bg="white").pack(pady=20)
        self.inputs = {}
        
        # Campos de entrada
        for label in ["Código", "Artículo", "Cantidad"]:
            f = tk.Frame(frame_reg, bg="white")
            f.pack(fill="x", padx=40, pady=5)
            tk.Label(f, text=label+":", bg="white", width=12, anchor="w").pack(side="left")
            
            # Si es código, lo hacemos de solo lectura
            if label == "Código":
                entry = tk.Entry(f, font=("Arial", 11), bg="#eeeeee")
                entry.insert(0, self.obtener_siguiente_codigo())
                entry.config(state='readonly')
            else:
                entry = tk.Entry(f, font=("Arial", 11))
            
            entry.pack(side="right", fill="x", expand=True)
            self.inputs[label] = entry

        tk.Button(frame_reg, text="💾 GUARDAR ARTÍCULO", command=self.alta_nueva, bg="#28a745", fg="white", font=("Arial", 11, "bold")).pack(fill="x", padx=40, pady=25)

    def alta_nueva(self):
        try:
            # Para leer el entry readonly hay que usar get() igual
            cod = self.inputs["Código"].get()
            art = self.inputs["Artículo"].get().strip()
            can = int(self.inputs["Cantidad"].get().strip())
            
            if not art: raise ValueError
            
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            conn = sqlite3.connect("sistema_completo.db")
            conn.execute("INSERT INTO inventario (codigo, articulo, descripcion, cantidad, solicitado, fecha_hora) VALUES (?,?,?,?,?,?)",
                        (cod, art, "INGRESO INICIAL", can, "ADMIN", fecha))
            conn.commit()
            conn.close()
            
            self.cargar_datos()
            messagebox.showinfo("Éxito", f"Artículo {cod} añadido.")
            
            # Limpiar campos y actualizar el siguiente código
            self.inputs["Artículo"].delete(0, tk.END)
            self.inputs["Cantidad"].delete(0, tk.END)
            
            # Actualizar el código automático para el siguiente registro
            self.inputs["Código"].config(state='normal')
            self.inputs["Código"].delete(0, tk.END)
            self.inputs["Código"].insert(0, self.obtener_siguiente_codigo())
            self.inputs["Código"].config(state='readonly')
            
        except ValueError:
            messagebox.showerror("Error", "Verifique que el artículo tenga nombre y la cantidad sea un número.")

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

class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("1100x750")
        self.root.configure(bg="white")
        
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self.main_frame, text="SISTEMA FE Y ALEGRÍA", font=("Arial", 25, "bold"), fg="#da251d", bg="white").pack(pady=20)
        
        self.ent_user = tk.Entry(self.main_frame, font=("Arial", 12), justify="center")
        self.ent_user.insert(0, "admin")
        self.ent_user.pack(pady=5)
        
        self.ent_pass = tk.Entry(self.main_frame, font=("Arial", 12), show="*", justify="center")
        self.ent_pass.insert(0, "1234")
        self.ent_pass.pack(pady=5)
        
        tk.Button(self.main_frame, text="INICIAR SESIÓN", bg="#da251d", fg="white", font=("Arial", 11, "bold"), command=self.validar, width=20).pack(pady=30)

    def validar(self):
        if self.ent_user.get() == "admin" and self.ent_pass.get() == "1234":
            for w in self.root.winfo_children(): w.destroy()
            SistemaInventario(self.root)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

if __name__ == "__main__":
    inicializar_db()
    root = tk.Tk()
    Login(root)
    root.mainloop()
