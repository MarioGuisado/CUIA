import cv2
import numpy as np
import time

video = cv2.VideoCapture("1 Minute Timer.mp4")
#video.set(cv2.CAP_PROP_FPS, 60)
fps = video.get(cv2.CAP_PROP_FPS)
numframes = video.get(cv2.CAP_PROP_FRAME_COUNT)

if not video.isOpened():
    print("No se puede abrir el fichero")
    exit()
inicio = time.time()

#tiempo_por_frame = 1 / fps
contador = 0
while True:
    #tiempoframe = time.time()
    ret, frame = video.read()
    
    if not ret:
        print("No he podido leer el frame")
        break

    #cv2.waitKey(37)
    contador+=1
    tiempoframe = inicio + contador / fps
    ahora = time.time()

    if ahora <= tiempoframe:
        time.sleep(tiempoframe-ahora)
        cv2.imshow('VIDEO', frame)
    else:
        video.set(cv2.CAP_PROP_POS_FRAMES, (ahora -inicio) * fps)
    




    cv2.imshow('VIDEO', frame)
   # tiempo = time.time()
    #if tiempo - tiempoframe < tiempo_por_frame:
     #   time.sleep(tiempo_por_frame-(tiempo - tiempoframe))

    if cv2.waitKey(1) == ord(' '):
        break
fin = time.time()
video.release()

print("FPS: ", fps)
print("Número de frames: ", numframes)
print("Duración: ", fin-inicio, " segundos")
print("FPS efectivos: ", numframes/(fin-inicio))


cv2.destroyWindow('VIDEO')