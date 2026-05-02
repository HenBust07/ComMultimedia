import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import CalcPSNR
import CompresionDCT
import cv2
import math

# ── Paleta (misma que main_gui) ──
COLOR_BG      = "#0D1B2A"
COLOR_PANEL   = "#112233"
COLOR_ACCENT  = "#00C9A7"
COLOR_ACCENT2 = "#378ADD"
COLOR_TEXT    = "#E8F4FD"
COLOR_MUTED   = "#7A9BB5"
COLOR_BTN     = "#1A3A5C"
COLOR_RED     = "#E24B4A"

ANCHO_IMG = 370
ALTO_IMG  = 320

def abrir(imagen_original):
    ventana = tk.Tk()
    ventana.title("Compresión DCT — Evaluación")
    ventana.geometry("1280x720")
    ventana.resizable(False, False)
    ventana.configure(bg=COLOR_BG)

    # ══════════════════════════════════════════
    #  HEADER con canvas decorativo
    # ══════════════════════════════════════════
    header = tk.Canvas(ventana, width=1280, height=70,
                       bg=COLOR_PANEL, highlightthickness=0)
    header.place(x=0, y=0)

    # Línea inferior del header
    header.create_line(0, 69, 1280, 69, fill=COLOR_ACCENT, width=2)

    # Ondas decorativas pequeñas en el header
    for i in range(0, 1280, 3):
        y = 35 + 8 * math.sin(i * 0.05)
        header.create_oval(i, y, i+2, y+2, fill=COLOR_ACCENT2, outline="")

    # Título centrado
    header.create_text(640, 35,
                       text="Compresión de Imágenes mediante la DCT",
                       font=("Courier", 17, "bold"),
                       fill=COLOR_ACCENT)

    # ══════════════════════════════════════════
    #  Convertir imagen a gris y recortar
    # ══════════════════════════════════════════
    gris_full = cv2.cvtColor(imagen_original, cv2.COLOR_BGR2GRAY)
    alto_rec  = (gris_full.shape[0] // 8) * 8
    ancho_rec = (gris_full.shape[1] // 8) * 8
    gris = gris_full[:alto_rec, :ancho_rec]

    def cv2_a_tk(img_cv2, ancho=ANCHO_IMG, alto=ALTO_IMG):
        if len(img_cv2.shape) == 2:
            img_pil = Image.fromarray(img_cv2)
        else:
            img_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
        img_pil = img_pil.resize((ancho, alto))
        return ImageTk.PhotoImage(img_pil)

    # ══════════════════════════════════════════
    #  Función para crear tarjeta de imagen
    # ══════════════════════════════════════════
    def crear_tarjeta(parent, x, y, titulo, tag):
        """Crea un panel con borde, etiqueta superior y espacio para imagen."""
        # Marco exterior
        marco = tk.Frame(parent, bg=COLOR_ACCENT, padx=2, pady=2)
        marco.place(x=x, y=y)

        # Interior
        interior = tk.Frame(marco, bg=COLOR_PANEL)
        interior.pack()

        # Etiqueta superior dentro del panel
        encabezado = tk.Frame(interior, bg=COLOR_BTN, height=28)
        encabezado.pack(fill="x")

        # Punto de color decorativo
        punto_color = COLOR_ACCENT if tag != "COMPRIMIDA" else COLOR_ACCENT2
        tk.Label(encabezado, text="●", font=("Courier", 10),
                 bg=COLOR_BTN, fg=punto_color).pack(side="left", padx=8)

        tk.Label(encabezado,
                 text=titulo,
                 font=("Courier", 10, "bold"),
                 bg=COLOR_BTN, fg=COLOR_TEXT).pack(side="left")

        # Label para la imagen
        img_label = tk.Label(interior, bg=COLOR_PANEL,
                             width=ANCHO_IMG, height=ALTO_IMG)
        img_label.pack()

        return img_label

    # ══════════════════════════════════════════
    #  Tres tarjetas de imagen
    # ══════════════════════════════════════════
    img1 = crear_tarjeta(ventana, x=20,  y=80,  titulo="ORIGINAL",       tag="ORIGINAL")
    img2 = crear_tarjeta(ventana, x=415, y=80,  titulo="MONOCROMÁTICA",  tag="MONO")
    img3 = crear_tarjeta(ventana, x=810, y=80,  titulo="COMPRIMIDA",     tag="COMPRIMIDA")

    # Cargar imágenes iniciales
    foto_original = cv2_a_tk(imagen_original)
    img1.config(image=foto_original)
    img1.image = foto_original

    foto_gris = cv2_a_tk(gris)
    img2.config(image=foto_gris)
    img2.image = foto_gris

    # Placeholder para comprimida
    placeholder = np.full((ALTO_IMG, ANCHO_IMG), 25, dtype=np.uint8)
    # Cuadrícula decorativa en el placeholder
    for i in range(0, ALTO_IMG, 20):
        placeholder[i, :] = 40
    for j in range(0, ANCHO_IMG, 20):
        placeholder[:, j] = 40
    foto_placeholder = cv2_a_tk(placeholder)
    img3.config(image=foto_placeholder)
    img3.image = foto_placeholder

    # ══════════════════════════════════════════
    #  Panel de control inferior
    # ══════════════════════════════════════════
    panel_ctrl = tk.Canvas(ventana, width=1280, height=160,
                           bg=COLOR_PANEL, highlightthickness=0)
    panel_ctrl.place(x=0, y=555)
    panel_ctrl.create_line(0, 0, 1280, 0, fill=COLOR_ACCENT, width=2)

    # ── Sección izquierda: coeficientes ──
    tk.Label(ventana,
             text="Coeficientes DCT (1 – 64)",
             font=("Courier", 11), bg=COLOR_PANEL, fg=COLOR_MUTED
             ).place(x=40, y=572)

    frame_entry = tk.Frame(ventana, bg=COLOR_BTN,
                           highlightbackground=COLOR_ACCENT,
                           highlightthickness=1)
    frame_entry.place(x=40, y=598)

    entrada_coef = tk.Entry(frame_entry, width=10,
                            font=("Courier", 14, "bold"),
                            bg=COLOR_BTN, fg=COLOR_ACCENT,
                            insertbackground=COLOR_ACCENT,
                            relief="flat", bd=6)
    entrada_coef.pack()

    # ── Sección central: botón comprimir ──
    def hover_btn(e, btn, entrando):
        btn.config(bg=COLOR_ACCENT if entrando else COLOR_BTN,
                   fg=COLOR_BG    if entrando else COLOR_TEXT)

    btn_comprimir = tk.Button(ventana,
                              text="▶  COMPRIMIR",
                              font=("Courier", 13, "bold"),
                              bg=COLOR_BTN, fg=COLOR_TEXT,
                              activebackground=COLOR_ACCENT,
                              relief="flat", cursor="hand2",
                              width=18, pady=12,
                              command=lambda: comprimir())
    btn_comprimir.place(x=480, y=590)
    btn_comprimir.bind("<Enter>", lambda e: hover_btn(e, btn_comprimir, True))
    btn_comprimir.bind("<Leave>", lambda e: hover_btn(e, btn_comprimir, False))

    # ── Sección derecha: PSNR ──
    tk.Label(ventana,
             text="PSNR obtenido",
             font=("Courier", 11), bg=COLOR_PANEL, fg=COLOR_MUTED
             ).place(x=900, y=572)

    frame_psnr = tk.Frame(ventana, bg=COLOR_BTN,
                          highlightbackground=COLOR_ACCENT2,
                          highlightthickness=1)
    frame_psnr.place(x=900, y=598)

    entrada_psnr = tk.Entry(frame_psnr, width=18,
                            font=("Courier", 14, "bold"),
                            bg=COLOR_BTN, fg=COLOR_ACCENT2,
                            insertbackground=COLOR_ACCENT2,
                            relief="flat", bd=6,
                            state="readonly")
    entrada_psnr.pack()

    # ── Barra de estado ──
    status_var = tk.StringVar(value="  Listo — ingresa el número de coeficientes y presiona COMPRIMIR")
    status_bar = tk.Label(ventana, textvariable=status_var,
                          font=("Courier", 10), bg=COLOR_BG,
                          fg=COLOR_MUTED, anchor="w")
    status_bar.place(x=0, y=695, width=1000)

    # ── Botón regresar al menú ──
    def regresar():
        import subprocess, sys, os
        ruta_main = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_gui.py")
        ventana.destroy()
        subprocess.Popen([sys.executable, ruta_main])

    def hover_regresar(e, entrando):
        btn_regresar.config(bg=COLOR_BTN    if entrando else COLOR_PANEL,
                            fg=COLOR_ACCENT if entrando else COLOR_MUTED)

    btn_regresar = tk.Button(ventana, text="◀  menú",
                             font=("Courier", 11),
                             bg=COLOR_PANEL, fg=COLOR_MUTED,
                             relief="flat", cursor="hand2",
                             width=10, pady=6,
                             command=regresar)
    btn_regresar.place(x=1020, y=690)
    btn_regresar.bind("<Enter>", lambda e: hover_regresar(e, True))
    btn_regresar.bind("<Leave>", lambda e: hover_regresar(e, False))

    # ── Botón salir ──
    def hover_salir(e, entrando):
        btn_salir.config(bg=COLOR_RED    if entrando else "#2a1a1a",
                         fg=COLOR_TEXT   if entrando else COLOR_RED)

    btn_salir = tk.Button(ventana, text="salir",
                          font=("Courier", 11),
                          bg="#2a1a1a", fg=COLOR_RED,
                          relief="flat", cursor="hand2",
                          width=10, pady=6,
                          command=ventana.destroy)
    btn_salir.place(x=1160, y=690)
    btn_salir.bind("<Enter>", lambda e: hover_salir(e, True))
    btn_salir.bind("<Leave>", lambda e: hover_salir(e, False))

    # ══════════════════════════════════════════
    #  Lógica de compresión (sin cambios)
    # ══════════════════════════════════════════
    def comprimir():
        coef = entrada_coef.get().strip()
        if not coef.isdigit() or not (1 <= int(coef) <= 64):
            messagebox.showerror("Error de entrada",
                                 "Ingresa un número entero entre 1 y 64")
            return

        status_var.set(f"  Comprimiendo con {coef} coeficientes...")
        ventana.update()

        img_comprimida = CompresionDCT.comprimir_imagen(gris, int(coef))

        foto_comprimida = cv2_a_tk(img_comprimida)
        img3.config(image=foto_comprimida)
        img3.image = foto_comprimida

        psnr = CalcPSNR.calcular_psnr(gris, img_comprimida)

        entrada_psnr.config(state="normal")
        entrada_psnr.delete(0, tk.END)
        entrada_psnr.insert(0, psnr)
        entrada_psnr.config(state="readonly")

        status_var.set(f"  ✓  Compresión completada — {coef} coeficientes  |  PSNR: {psnr}")

    ventana.mainloop()
