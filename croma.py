import cv2
import numpy as np
from matplotlib import pyplot as plt



def eventoraton(evento, x, y, flags, params):
    if evento == cv2.EVENT_LBUTTONUP:
        print("H: ", framehsv[y, x, 0])
        print("S: ", framehsv[y, x, 1])
        print("V: ", framehsv[y, x, 2])
        print("-----")

lena = cv2.imread("lena.tif")

cv2.namedWindow("WEBCAM")
cv2.setMouseCallback("WEBCAM", eventoraton)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se puede abrir la cámara")
    exit()

ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fondo = cv2.resize(lena, (ancho,alto))

while cap.isOpened():
    ret, framebgr = cap.read()

    if not ret:
        print("No he podido leer el frame")
        break

    # Procesado de imágenes aquí
    framehsv = cv2.cvtColor(framebgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(framehsv)

    mbg = cv2.inRange( framehsv, (100, 80, 120), (180, 255, 255))
    mascarabg = cv2.merge((mbg,mbg,mbg))
    mascarabg = cv2.GaussianBlur(mascarabg, (7,7), 0)
    mascarafg = cv2.bitwise_not(mascarabg)

    fg =  cv2.bitwise_and(framebgr, mascarafg)
    bg =  cv2.bitwise_and(fondo, mascarabg)

    framebgr = cv2.bitwise_or(fg, bg)
    #frame = cv2.GaussianBlur(frame, (7, 7), 5)
    #framebgr = cv2.Sobel(framebgr, -1, 1, 1, scale=10)

    cv2.imshow('WEBCAM', framebgr)

    if cv2.waitKey(1) == ord(' '):
        break

cap.release()
cv2.destroyWindow('WEBCAM')
