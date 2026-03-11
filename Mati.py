import tkinter as tk
from tkinter import scrolledtext
import subprocess
import platform

class PinkAdmin:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Hardware - Pink Edition")
        self.root.geometry("700x550")
        self.root.configure(bg="#FFF0F5") # Fondo Rosa Pastel

        # Colores
        self.pink_dark = "#FF69B4"
        self.pink_soft = "#FFB6C1"
        self.white = "#FFFFFF"

        self.setup_ui()

    def run_ps(self, cmd):
        """Ejecuta comandos de PowerShell para obtener datos reales"""
        try:
            # Usamos powershell por ser más preciso que wmic
            process = subprocess.Popen(["powershell", "-Command", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            return stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def setup_ui(self):
        # Título
        tk.Label(self.root, text="DISPOSITIVOS Y COMPONENTES", bg="#FFF0F5", 
                 fg=self.pink_dark, font=("Segoe UI", 16, "bold"), pady=20).pack()

        # Botones
        btn_frame = tk.Frame(self.root, bg="#FFF0F5")
        btn_frame.pack(pady=10)

        self.btn_style = {"bg": self.pink_soft, "fg": "white", "font": ("Segoe UI", 10, "bold"), 
                          "relief": "flat", "padx": 20, "pady": 8, "cursor": "hand2"}

        tk.Button(btn_frame, text="ESCANEAR RAM", command=self.get_ram, **self.btn_style).pack(side="left", padx=5)
        tk.Button(btn_frame, text="ESCANEAR DISCOS", command=self.get_disks, **self.btn_style).pack(side="left", padx=5)
        tk.Button(btn_frame, text="ESCANEAR CPU", command=self.get_cpu, **self.btn_style).pack(side="left", padx=5)

        # Área de resultados
        self.display = scrolledtext.ScrolledText(self.root, width=80, height=20, 
                                                font=("Consolas", 10), bg="white", 
                                                fg="#444", padx=10, pady=10, borderwidth=0)
        self.display.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.display.insert(tk.END, "Haz clic en un botón para escanear el hardware de esta PC...")

    def update_display(self, title, content):
        self.display.config(state="normal")
        self.display.delete("1.0", tk.END)
        self.display.insert(tk.END, f"=== {title} ===\n\n")
        self.display.insert(tk.END, content)
        self.display.config(state="disabled")

    def get_ram(self):
        # Obtiene la RAM total en GB usando PowerShell
        cmd = "(Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB"
        res = self.run_ps(cmd)
        if res:
            try:
                gb = round(float(res.replace(',', '.')), 2)
                self.update_display("MEMORIA RAM", f"Total instalado en el sistema: {gb} GB")
            except:
                self.update_display("MEMORIA RAM", f"Raw Data: {res}")
        else:
            self.update_display("MEMORIA RAM", "No se detectaron módulos o acceso denegado.")

    def get_disks(self):
        # Obtiene discos, tamaño y espacio libre
        cmd = "Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, @{n='SizeGB';e={[math]::Round($_.Size/1GB,2)}}, @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB,2)}} | Out-String"
        res = self.run_ps(cmd)
        self.update_display("ALMACENAMIENTO", res if res else "No se encontraron discos.")

    def get_cpu(self):
        # Obtiene nombre del procesador
        cmd = "(Get-CimInstance Win32_Processor).Name"
        res = self.run_ps(cmd)
        self.update_display("PROCESADOR", res if res else "No se pudo leer la CPU.")

if __name__ == "__main__":
    root = tk.Tk()
    # Evitar que la ventana sea muy pequeña al inicio
    root.minsize(600, 400)
    app = PinkAdmin(root)
    root.mainloop()
