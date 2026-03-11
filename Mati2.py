import tkinter as tk
import customtkinter as ctk
import psutil
import platform
import socket
import subprocess

# Configuración de apariencia
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

class AppSistemas(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Información del Sistema - Monitor Rosa")
        self.geometry("700x500")
        self.configure(fg_color="#FCE4EC") # Rosa muy claro de fondo

        # Configuración de colores rosa
        self.color_primario = "#F06292" # Rosa fuerte
        self.color_secundario = "#F8BBD0" # Rosa suave
        self.color_texto = "#880E4F" # Guinda/Rosa oscuro

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Barra lateral de navegación
        self.navigation_frame = ctk.CTkFrame(self, fg_color=self.color_primario, corner_radius=0)
        self.navigation_frame.grid(row=0, column:0, sticky="nsew")
        
        self.label_titulo = ctk.CTkLabel(self.navigation_frame, text="SISTEMA", 
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        text_color="white")
        self.label_titulo.pack(pady=20, padx=10)

        self.btn_pc = ctk.CTkButton(self.navigation_frame, text="Componentes PC", 
                                   fg_color="transparent", text_color="white",
                                   hover_color=self.color_texto, anchor="w",
                                   command=self.mostrar_pc)
        self.btn_pc.pack(fill="x", padx=5, pady=5)

        self.btn_red = ctk.CTkButton(self.navigation_frame, text="Red y Conexión", 
                                    fg_color="transparent", text_color="white",
                                    hover_color=self.color_texto, anchor="w",
                                    command=self.mostrar_red)
        self.btn_red.pack(fill="x", padx=5, pady=5)

        # Contenedor principal de texto
        self.home_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15, border_color=self.color_primario, border_width=2)
        self.home_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.textbox = ctk.CTkTextbox(self.home_frame, font=("Consolas", 12), text_color=self.color_texto, fg_color="white")
        self.textbox.pack(expand=True, fill="both", padx=10, pady=10)

        self.mostrar_pc()

    def limpiar_texto(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", tk.END)

    def mostrar_pc(self):
        self.limpiar_texto()
        info = [
            "--- COMPONENTES DEL SISTEMA ---",
            f"Sistema Operativo: {platform.system()} {platform.release()}",
            f"Procesador: {platform.processor()}",
            f"Arquitectura: {platform.machine()}",
            f"Memoria RAM Total: {round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            f"Uso de CPU actual: {psutil.cpu_percent()}%",
            "\n--- DISCOS DUROS ---"
        ]
        
        for particion in psutil.disk_partitions():
            try:
                uso = psutil.disk_usage(particion.mountpoint)
                info.append(f"Disco {particion.device}: {round(uso.total / (1024**3), 2)} GB")
            except PermissionError:
                continue

        self.textbox.insert("0.0", "\n".join(info))
        self.textbox.configure(state="disabled")

    def mostrar_red(self):
        self.limpiar_texto()
        
        hostname = socket.gethostname()
        ip_local = socket.gethostbyname(hostname)
        
        info = [
            "--- INFORMACIÓN DE RED ---",
            f"Nombre del Equipo: {hostname}",
            f"Dirección IP Local: {ip_local}",
            "\n--- INTERFACES DE RED ---"
        ]
        
        addrs = psutil.net_if_addrs()
        for interface, snics in addrs.items():
            info.append(f"Interfaz: {interface}")
            for snic in snics:
                if snic.family == socket.AF_INET:
                    info.append(f"  IP: {snic.address}")

        self.textbox.insert("0.0", "\n".join(info))
        self.textbox.configure(state="disabled")

if __name__ == "__main__":
    app = AppSistemas()
    app.mainloop()
