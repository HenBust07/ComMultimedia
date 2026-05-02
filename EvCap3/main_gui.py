import tkinter as tk
import signal
import sys
import cv2
import math
from tkinter import filedialog
import VentanaPrincipal

# ── Paleta de colores ──
COLOR_BG       = "#0D1B2A"   # azul marino oscuro
COLOR_PANEL    = "#112233"   # panel lateral
COLOR_ACCENT   = "#00C9A7"   # verde teal
COLOR_ACCENT2  = "#378ADD"   # azul claro
COLOR_TEXT     = "#E8F4FD"   # blanco azulado
COLOR_MUTED    = "#7A9BB5"   # gris azulado
COLOR_BTN      = "#1A3A5C"   # botón base
COLOR_BTN_HOV  = "#00C9A7"   # botón hover
COLOR_RED      = "#E24B4A"   # salir

ventana = tk.Tk()
ventana.title("Compresión de Imágenes — DCT")
ventana.geometry("620x480")
ventana.resizable(False, False)
ventana.configure(bg=COLOR_BG)

camara_activa = False

# ══════════════════════════════════════════════
#  Canvas con animación de señales / ondas
# ══════════════════════════════════════════════
canvas = tk.Canvas(ventana, width=620, height=200,
                   bg=COLOR_BG, highlightthickness=0)
canvas.place(x=0, y=0)

# Cuadrícula de fondo
for x in range(0, 621, 30):
    canvas.create_line(x, 0, x, 200, fill="#162840", width=1)
for y in range(0, 201, 20):
    canvas.create_line(0, y, 620, y, fill="#162840", width=1)

# Antena central SVG-style (dibujada con líneas)
def dibujar_antena(cx, cy):
    # Torre
    canvas.create_line(cx, cy, cx, cy+55, fill=COLOR_MUTED, width=3)
    canvas.create_line(cx-25, cy+55, cx+25, cy+55, fill=COLOR_MUTED, width=3)
    canvas.create_line(cx-12, cy+55, cx-12, cy+70, fill=COLOR_MUTED, width=2)
    canvas.create_line(cx+12, cy+55, cx+12, cy+70, fill=COLOR_MUTED, width=2)
    canvas.create_line(cx-18, cy+70, cx+18, cy+70, fill=COLOR_MUTED, width=3)
    # Punta
    canvas.create_oval(cx-4, cy-6, cx+4, cy+2, fill=COLOR_ACCENT, outline="")

dibujar_antena(310, 60)

# Ondas de radio animadas
ondas = []
for r in [35, 60, 85, 110]:
    arco = canvas.create_arc(310-r, 60-r, 310+r, 60+r,
                              start=30, extent=120,
                              style="arc", outline=COLOR_ACCENT2,
                              width=2)
    ondas.append((arco, r))

# Señal sinusoidal izquierda
puntos_sin = []
for i in range(200):
    x = i * 1.3
    y = 155 + 18 * math.sin(i * 0.12)
    puntos_sin.append((x, y))

for i in range(len(puntos_sin) - 1):
    alpha = i / len(puntos_sin)
    color = COLOR_ACCENT if i % 2 == 0 else COLOR_ACCENT2
    canvas.create_line(puntos_sin[i][0], puntos_sin[i][1],
                       puntos_sin[i+1][0], puntos_sin[i+1][1],
                       fill=color, width=2)

# Señal sinusoidal derecha (desfasada)
for i in range(len(puntos_sin) - 1):
    x1 = 620 - puntos_sin[i][0]
    x2 = 620 - puntos_sin[i+1][0]
    color = COLOR_ACCENT if i % 2 == 0 else COLOR_ACCENT2
    canvas.create_line(x1, puntos_sin[i][1],
                       x2, puntos_sin[i+1][1],
                       fill=color, width=2)

# Puntos de datos dispersos (estilo constelación IQ)
import random
random.seed(42)
for _ in range(18):
    px = random.randint(20, 590)
    py = random.randint(135, 195)
    canvas.create_oval(px-2, py-2, px+2, py+2, fill=COLOR_ACCENT, outline="")

# Línea separadora decorativa
canvas.create_line(0, 198, 620, 198, fill=COLOR_ACCENT, width=2)

# ── Animación de pulso en la antena ──
pulso_radios = [0]
pulso_items  = [None]

def animar_pulso():
    r = pulso_radios[0]
    if pulso_items[0]:
        canvas.delete(pulso_items[0])
    if r < 130:
        alpha_hex = format(max(0, int(180 * (1 - r/130))), '02x')
        item = canvas.create_oval(310-r, 60-r, 310+r, 60+r,
                                   outline=f"#00C9A7",
                                   width=max(1, 3 - r//40))
        pulso_items[0] = item
        pulso_radios[0] = r + 3
    else:
        pulso_radios[0] = 0
    ventana.after(30, animar_pulso)

animar_pulso()

# ══════════════════════════════════════════════
#  Sección inferior: título + botones
# ══════════════════════════════════════════════
frame_inferior = tk.Frame(ventana, bg=COLOR_BG)
frame_inferior.place(x=0, y=200, width=620, height=280)

# Título
tk.Label(frame_inferior,
         text="Compresión de Imágenes mediante la DCT",
         font=("Courier", 15, "bold"),
         bg=COLOR_BG, fg=COLOR_ACCENT).pack(pady=(18, 2))

tk.Label(frame_inferior,
         text="Procesamiento Digital de Señales  ·  Multimedia",
         font=("Courier", 10),
         bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=(0, 18))

# ── Función hover para botones ──
def btn_hover(btn, entrando):
    if entrando:
        btn.config(bg=COLOR_BTN_HOV, fg=COLOR_BG)
    else:
        btn.config(bg=COLOR_BTN, fg=COLOR_TEXT)

def btn_hover_red(btn, entrando):
    if entrando:
        btn.config(bg=COLOR_RED, fg=COLOR_TEXT)
    else:
        btn.config(bg="#2a1a1a", fg=COLOR_RED)

# ── Frame de botones centrado ──
frame_btns = tk.Frame(frame_inferior, bg=COLOR_BG)
frame_btns.pack()

estilo_btn = dict(
    font=("Courier", 12, "bold"),
    bg=COLOR_BTN, fg=COLOR_TEXT,
    relief="flat", cursor="hand2",
    width=28, pady=10,
    bd=0
)

def TerminarSim(signum=None, frame=None):
    ventana.destroy()
    sys.exit(0)

def SelecImagen():
    ruta = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=[
            ("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff"),
            ("Todos los archivos", "*.*")
        ]
    )
    if ruta:
        img = cv2.imread(ruta)
        ventana.destroy()
        VentanaPrincipal.abrir(imagen_original=img)

def Camara():
    global camara_activa
    if camara_activa:
        return
    camara_activa = True

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        camara_activa = False
        return

    cv2.namedWindow("Camara — presiona C para capturar, Q para salir")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Camara — presiona C para capturar, Q para salir", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        if key == ord('c'):
            cap.release()
            cv2.destroyAllWindows()
            camara_activa = False
            ventana.destroy()
            VentanaPrincipal.abrir(imagen_original=frame.copy())
            return

        try:
            if cv2.getWindowProperty(
                "Camara — presiona C para capturar, Q para salir",
                cv2.WND_PROP_VISIBLE) < 1:
                break
        except:
            break

    cap.release()
    cv2.destroyAllWindows()
    camara_activa = False

b1 = tk.Button(frame_btns, text="[ Imagen almacenada ]",
               command=SelecImagen, **estilo_btn)
b1.pack(pady=6)
b1.bind("<Enter>", lambda e: btn_hover(b1, True))
b1.bind("<Leave>", lambda e: btn_hover(b1, False))

b2 = tk.Button(frame_btns, text="[ Captura por cámara ]",
               command=Camara, **estilo_btn)
b2.pack(pady=6)
b2.bind("<Enter>", lambda e: btn_hover(b2, True))
b2.bind("<Leave>", lambda e: btn_hover(b2, False))

estilo_salir = dict(
    font=("Courier", 11),
    bg="#2a1a1a", fg=COLOR_RED,
    relief="flat", cursor="hand2",
    width=28, pady=8, bd=0
)
b3 = tk.Button(frame_btns, text="salir", command=TerminarSim, **estilo_salir)
b3.pack(pady=(4, 0))
b3.bind("<Enter>", lambda e: btn_hover_red(b3, True))
b3.bind("<Leave>", lambda e: btn_hover_red(b3, False))

signal.signal(signal.SIGINT, TerminarSim)
signal.signal(signal.SIGTERM, TerminarSim)
ventana.mainloop()
