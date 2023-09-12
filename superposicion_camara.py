#Mario Guisado García

import cv2
import numpy as np

cap = cv2.VideoCapture(0)
opencv = cv2.imread('opencv.png', cv2.IMREAD_UNCHANGED)
opencv = cv2.resize(opencv, None, fx=0.25, fy=0.25)

if not cap.isOpened():
    print("No se puede abrir la cámara")
    exit()
while True:
    ret, frame = cap.read()

    if not ret:
        print("No he podido leer el frame")
        break

	# Procesado de imágenes aquí
    #opencv_escalado = cv2.resize(opencv, (frame.shape[1], frame.shape[0]))
    
    bg = frame
    hbg, wbg, _ = bg.shape
    fg = opencv[:, :, 0:3]
    hfg, wfg, _ = fg.shape
    alfa = opencv[:, :, 3]
    afla = 255 - alfa

    alfa = cv2.cvtColor(alfa, cv2.COLOR_GRAY2BGR) / 255
    afla = cv2.cvtColor(afla, cv2.COLOR_GRAY2BGR) / 255

    x = (wbg//2 - wfg//2) + 280
    y = (hbg//2 - hfg//2) + 200

    mezcla = bg
    mezcla[y:y+hfg, x:x+wfg] = mezcla[y:y+hfg, x:x+wfg]*afla + fg*alfa

    cv2.imshow('MEZCLA', mezcla)

    if cv2.waitKey(1) == ord(' '):
        break

cap.release()
cv2.destroyWindow('WEBCAM')