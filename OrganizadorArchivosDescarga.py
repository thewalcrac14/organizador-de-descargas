#Importación de liberias necesarias para el funcionamiento del programa

import os
import shutil
import hashlib
import threading
import subprocess
import customtkinter as ctk
from tkinter import messagebox


#Se le asigna al programa dónde está tu carpeta de Descargas y qué tipo de archivo (extensión) va en cada carpeta destino.
USER_PATH = os.path.expanduser("~")
PATH_DESCARGAS = os.path.join(USER_PATH, "Downloads")

ORGANIZACION = {
    os.path.join(USER_PATH, "Documents"): [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
    os.path.join(USER_PATH, "Pictures"):  [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"],
    os.path.join(USER_PATH, "Videos"):    [".mp4", ".mov", ".avi", ".mkv"],
    os.path.join(USER_PATH, "Music"):     [".mp3", ".wav", ".flac"],
}

#Creación UX/UI con CustomTkinter. Utilizando una ventana y implementación de consola
class OrganizadorDefinitivo(ctk.CTk):
    def __init__(self):
        super().__init__()

        #Nombre a la ventana, tamaño y tema oscuro
        self.title("Organizador de Descargas")
        self.geometry("780x740")
        self.minsize(720, 640)
        self.resizable(True, True)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue") 

        #Sistema se adapta al tamaño de la ventana para que todo se vea bien aunque la redimensiones
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #Creamos un contenedor principal donde meteremos todos nuestros textos y botones
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, padx=30, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(6, weight=1) 

        #Título principal del programa en la parte superior
        self.label_titulo = ctk.CTkLabel(self.main_container, text="🗂️ORGANIZADOR DE DESCARGAS", font=("Segoe UI", 22, "bold"), text_color="#F3F4F6")
        self.label_titulo.grid(row=0, column=0, pady=(5, 15), sticky="w")

        #Secciones para organizar por categorías
        self.label_seccion = ctk.CTkLabel(self.main_container, text="Selecciona una categoría para organizar:", font=("Segoe UI", 13, "bold"), text_color="#9CA3AF")
        self.label_seccion.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="w")

        #Botones de categorías en un cuadro gris oscuro
        self.frame_categorias = ctk.CTkFrame(self.main_container, fg_color="#1F2937", corner_radius=12)
        self.frame_categorias.grid(row=2, column=0, pady=(0, 15), sticky="ew")
        self.frame_categorias.grid_columnconfigure((0, 1), weight=1)

        #Botones de categorías. (Documentos, Imagenes, Videos, Música)
        estilo_btn_cat = {"font": ("Segoe UI", 12, "bold"), "height": 42, "corner_radius": 8, "fg_color": "#374151", "hover_color": "#4B5563"}
        
        self.btn_docs = ctk.CTkButton(self.frame_categorias, text="📄 Documentos", command=lambda: self.lanzar_hilo_procesar(os.path.join(USER_PATH, "Documents")), **estilo_btn_cat)
        self.btn_docs.grid(row=0, column=0, padx=15, pady=12, sticky="ew")
        
        self.btn_pics = ctk.CTkButton(self.frame_categorias, text="📷 Imágenes", command=lambda: self.lanzar_hilo_procesar(os.path.join(USER_PATH, "Pictures")), **estilo_btn_cat)
        self.btn_pics.grid(row=0, column=1, padx=15, pady=12, sticky="ew")
        
        self.btn_vids = ctk.CTkButton(self.frame_categorias, text="🎬 Videos", command=lambda: self.lanzar_hilo_procesar(os.path.join(USER_PATH, "Videos")), **estilo_btn_cat)
        self.btn_vids.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")
        
        self.btn_music = ctk.CTkButton(self.frame_categorias, text="🎵 Música", command=lambda: self.lanzar_hilo_procesar(os.path.join(USER_PATH, "Music")), **estilo_btn_cat)
        self.btn_music.grid(row=1, column=1, padx=15, pady=(0, 12), sticky="ew")

        #Sección para las acciones que afectan a todos los archivos a la vez
        self.label_seccion2 = ctk.CTkLabel(self.main_container, text="Acciones globales del sistema:", font=("Segoe UI", 13, "bold"), text_color="#9CA3AF")
        self.label_seccion2.grid(row=3, column=0, padx=5, pady=(0, 5), sticky="w")

        self.frame_acciones = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_acciones.grid(row=4, column=0, pady=(0, 15), sticky="ew")
        self.frame_acciones.grid_columnconfigure((0, 1), weight=1)

        #Botón verde que organiza absolutamente todo con un solo clic
        self.btn_todo = ctk.CTkButton(self.frame_acciones, text="🚀 ORGANIZAR TODOS LOS ARCHIVOS", font=("Segoe UI", 12, "bold"), height=44, corner_radius=10, fg_color="#10B981", hover_color="#059669", command=lambda: self.lanzar_hilo_procesar(None))
        self.btn_todo.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        #Botón rojo dedicado exclusivamente a borrar la basura (archivos repetidos)
        self.btn_duplicados = ctk.CTkButton(self.frame_acciones, text="🗑️BORRAR ARCHIVOS DUPLICADOS", font=("Segoe UI", 11, "bold"), height=44, corner_radius=10, fg_color="#EF4444", hover_color="#DC2626", command=self.lanzar_hilo_duplicados)
        self.btn_duplicados.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        #Consola falsa para que el programa muestre que se está haciendo paso a paso
        self.label_console = ctk.CTkLabel(self.main_container, text="CMD (Puedes escribir comandos de Windows en la barra inferior y presiona Enter):", font=("Segoe UI", 12, "italic"), text_color="#6B7280")
        self.label_console.grid(row=5, column=0, padx=5, sticky="w")

        self.txt_reporte = ctk.CTkTextbox(self.main_container, font=("Consolas", 12), fg_color="#0B0F19", text_color="#10B981", border_color="#1F2937", border_width=2, corner_radius=12)
        self.txt_reporte.grid(row=6, column=0, pady=(5, 8), sticky="nsew")

        #Barra donde puedes escribir comandos reales de Windows directamente desde nuestro programa
        self.cmd_input = ctk.CTkEntry(self.main_container, font=("Consolas", 13), placeholder_text="Escribe un comando aquí... (ej: python --version, pip list, dir)", fg_color="#0B0F19", text_color="#FFFFFF", border_color="#10B981", corner_radius=8)
        self.cmd_input.grid(row=7, column=0, pady=(0, 12), sticky="ew")
        self.cmd_input.bind("<Return>", self.ejecutar_comando_cmd)

        #Botón para cerrar el programa limpiamente
        self.frame_footer = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_footer.grid(row=8, column=0, sticky="ew")

        self.btn_salir = ctk.CTkButton(self.frame_footer, text="🚪Salir del Programa", font=("Segoe UI", 11, "bold"), height=32, width=150, corner_radius=8, fg_color="#4B5563", hover_color="#374151", command=self.quit)
        self.btn_salir.pack(side="right")
        
        #Mensaje de bienvenida que aparece al abrir el programa
        self.log(f"Microsoft Windows\n(c) Corporación Organizadora Inteligente. Todos los derechos reservados.\n\nC:\\Users\\{os.getlogin()}> Aqui puedes escribir comandos de Windows.")

    #Función para escribir mensajes en la pantallita negra
    def log(self, mensaje):
        self.txt_reporte.insert("end", f"{mensaje}\n")
        self.txt_reporte.see("end")

    #Función para hacer funcionar el CMD
    def ejecutar_comando_cmd(self, event):
        comando = self.cmd_input.get().strip()
        if not comando: return
        
        self.log(f"\nC:\\Users\\{os.getlogin()}> {comando}")
        self.cmd_input.delete(0, "end")

        def hilo_cmd():
            try:
                resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if resultado.stdout: self.log(resultado.stdout)
                if resultado.stderr: self.log(f"[ERROR CMD] {resultado.stderr}")
            except Exception as e: self.log(f"Error al lanzar el comando: {e}")
        
        threading.Thread(target=hilo_cmd, daemon=True).start()


    #Verificacion de archivos duplicados mediante la lectura de su contenido (hash)
    def calcular_hash(self, ruta):
        hash_sha = hashlib.sha256()
        try:
            with open(ruta, "rb") as f:
                for bloque in iter(lambda: f.read(4096), b""): hash_sha.update(bloque)
            return hash_sha.hexdigest()
        except: return None

    #Escaneo de los archivos duplicados en la carpeta de Descargas. Si encuentra alguno, lo borra y muestra un mensaje en la consola
    def limpiar_duplicados(self, carpeta_filtro=None):
        self.log("\n⚡[ESCANEANDO ARCHIVOS PARA DETECTAR DUPLICADOS...]")
        extensiones_validas = ORGANIZACION.get(carpeta_filtro) if carpeta_filtro else None
        hashes_vistos = {}
        borrados = 0

        for item in os.listdir(PATH_DESCARGAS):
            ruta_completa = os.path.join(PATH_DESCARGAS, item)
            if os.path.isfile(ruta_completa):
                ext = os.path.splitext(item)[1].lower()
                if extensiones_validas and ext not in extensiones_validas: continue

                file_hash = self.calcular_hash(ruta_completa)
                if not file_hash: continue

                if file_hash in hashes_vistos:
                    try:
                        os.remove(ruta_completa)
                        self.log(f"   ❌ Eliminado por redundancia: '{item}'")
                        borrados += 1
                    except: pass
                else: hashes_vistos[file_hash] = item
        return borrados

    #La aplicacion se ejecuta en "Segundo Plano" para evitar bug o crasheos
    def lanzar_hilo_procesar(self, carpeta_filtro):
        res = messagebox.askyesno("Confirmación de busqueda y limpieza", "¿Deseas buscar y eliminar archivos duplicados antes de moverlos?")
        self.cambiar_estado_botones("disabled") #Se apagan los botones temporalmente (Para evitar errores de multiples clics)
        threading.Thread(target=self.procesar, args=(carpeta_filtro, res), daemon=True).start()

    #Mensaje del botón rojo para confirmar eliminar TODOS los archivos duplicados
    def lanzar_hilo_duplicados(self):
        if messagebox.askyesno("Confirmación de limpieza completa", "¿Estás seguro de que deseas limpiar TODOS los archivos repetidos?"):
            self.cambiar_estado_botones("disabled")
            threading.Thread(target=self.solo_duplicados, daemon=True).start()

    #Funcion entre Habilitar/Deshabilitar los botones
    def cambiar_estado_botones(self, estado):
        for btn in [self.btn_docs, self.btn_pics, self.btn_vids, self.btn_music, self.btn_todo, self.btn_duplicados]:
            btn.configure(state=estado)

    #Funcionamiento del botón rojo
    def solo_duplicados(self):
        borrados = self.limpiar_duplicados(None)
        self.log(f"\n✨[OPERACIÓN TERMINADA]. Se eliminaron {borrados} duplicados totales.")
        self.cambiar_estado_botones("normal")
        messagebox.showinfo("🧹[LIMPIEZA COMPLETADA]", f"Se eliminaron {borrados} archivos.")


#Desarrollo del codigo principal que organiza los archivos

    # Agarra cada archivo, mira de qué tipo es (foto, video, etc.) y lo empuja a su carpeta correcta.
    def procesar(self, carpeta_filtro=None, borrar_duplicados=False):
        if not os.path.exists(PATH_DESCARGAS):
            self.cambiar_estado_botones("normal")
            return

        #Se limpian los archivos duplicados si el usuario dijo que "si"
        duplicados = self.limpiar_duplicados(carpeta_filtro) if borrar_duplicados else 0
        self.log("\n📂[CLASIFICANDO Y TRASLADANDO LOS ARCHIVOS...]")
        tareas = []

        #Se crea una lista de qué archivo va para cada destino
        for archivo in os.listdir(PATH_DESCARGAS):
            if os.path.isdir(os.path.join(PATH_DESCARGAS, archivo)): continue
            ext = os.path.splitext(archivo)[1].lower()

            for carpeta_destino, extensiones in ORGANIZACION.items():
                if carpeta_filtro and carpeta_destino != carpeta_filtro: continue
                if ext in extensiones:
                    tareas.append((os.path.join(PATH_DESCARGAS, archivo), carpeta_destino, archivo))
                    break

        #Si tu carpeta estaba organizada, se notifica y termina el proceso
        if not tareas:
            self.log("\n✨[NO TIENES ARCHIVOS PARA ORGANIZAR...]")
            self.cambiar_estado_botones("normal")
            return

        #Se trasladan los archivos y se crea un log en la consola de cada movimiento
        movidos = 0
        for r_orig, d_dir, arch in tareas:
            if not os.path.exists(d_dir): os.makedirs(d_dir)
            try:
                shutil.move(r_orig, os.path.join(d_dir, arch))
                self.log(f"   ➡️  Trasladando: '{arch}' hacia {os.path.basename(d_dir)}")
                movidos += 1
            except: pass

        #Se muestra el reporte final
        self.log(f"\n=========================================\n📊 REPORTE: Trasladados: {movidos} | Duplicados: {duplicados}\n=========================================")
        self.cambiar_estado_botones("normal")
        messagebox.showinfo("🚀[PROCESO COMPLETADO]", "Se han trasladado los archivos con éxito.")

#Arranca el programa si ejecutas este archivo directamente.
if __name__ == "__main__":
    app = OrganizadorDefinitivo()
    app.mainloop()
