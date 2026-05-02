import cv2
import numpy as np

# ── Orden zig-zag estándar JPEG para bloque 8x8 ──
ZIGZAG_INDEX = [
    (0,0),(0,1),(1,0),(2,0),(1,1),(0,2),(0,3),(1,2),
    (2,1),(3,0),(4,0),(3,1),(2,2),(1,3),(0,4),(0,5),
    (1,4),(2,3),(3,2),(4,1),(5,0),(6,0),(5,1),(4,2),
    (3,3),(2,4),(1,5),(0,6),(0,7),(1,6),(2,5),(3,4),
    (4,3),(5,2),(6,1),(7,0),(7,1),(6,2),(5,3),(4,4),
    (3,5),(2,6),(1,7),(2,7),(3,6),(4,5),(5,4),(6,3),
    (7,2),(7,3),(6,4),(5,5),(4,6),(3,7),(4,7),(5,6),
    (6,5),(7,4),(7,5),(6,6),(5,7),(6,7),(7,6),(7,7)
]

def comprimir_imagen(imagen_gris, num_coeficientes):
    """
    Comprime la imagen en escala de grises usando DCT por bloques 8x8.
    Conserva solo los primeros num_coeficientes coeficientes en orden zig-zag.
    Retorna la imagen comprimida como array numpy uint8.
    """

    num_coeficientes = int(num_coeficientes)

    if num_coeficientes < 1 or num_coeficientes > 64:
        raise ValueError("El número de coeficientes debe estar entre 1 y 64")

    img = imagen_gris.astype(np.float32)

    # Recortar para que sea múltiplo de 8
    alto, ancho = img.shape
    alto_rec = (alto // 8) * 8
    ancho_rec = (ancho // 8) * 8
    img = img[:alto_rec, :ancho_rec]

    resultado = np.zeros_like(img)

    for i in range(0, alto_rec, 8):
        for j in range(0, ancho_rec, 8):

            bloque = img[i:i+8, j:j+8]

            # Aplicar DCT al bloque
            dct_bloque = cv2.dct(bloque)

            # Máscara vacía → solo se conservan N coeficientes zig-zag
            mascara = np.zeros((8, 8), dtype=np.float32)

            for k in range(num_coeficientes):
                fila, col = ZIGZAG_INDEX[k]
                mascara[fila, col] = dct_bloque[fila, col]

            # IDCT → reconstruir bloque
            bloque_rec = cv2.idct(mascara)
            resultado[i:i+8, j:j+8] = bloque_rec

    # Recortar valores fuera de rango y convertir a uint8
    resultado = np.clip(resultado, 0, 255).astype(np.uint8)
    return resultado
