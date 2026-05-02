import cv2
import numpy as np

def calcular_psnr(imagen_original, imagen_comprimida):
    """
    Calcula el PSNR entre la imagen original y la comprimida.
    Ambas deben ser arrays numpy (escala de grises).
    Retorna el valor PSNR en dB como string para mostrar en el label.
    """

    original   = imagen_original.astype(np.float64)
    comprimida = imagen_comprimida.astype(np.float64)

    # Error cuadrático medio
    mse = np.mean((original - comprimida) ** 2)

    if mse == 0:
        return "PSNR: ∞ (imágenes idénticas)"

    # Valor máximo de píxel (8 bits : 255)
    MAX = 255.0
    psnr = 10 * np.log10((MAX ** 2) / mse)

    return f"{psnr:.2f} dB"
