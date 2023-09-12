import random
import numpy as np
import cv2
import os
import face_recognition as face
import threading
import speech_recognition as sr
import tkinter as tk
from PIL import ImageTk, Image


rutaCarpeta = "./"
archivos = [nombre for nombre in os.listdir(rutaCarpeta) if os.path.isfile(os.path.join(rutaCarpeta, nombre))]
archivos_txt = [nombre for nombre in archivos if nombre.endswith(".txt") and not "Datos" in nombre]


texto_reconocido = [""]

carta_detectada = [False]

class VoiceThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone()
        self.stop_event = threading.Event()

    def run(self):
        with self.mic as source:
          while not self.stop_event.is_set():
               self.rec.adjust_for_ambient_noise(source, duration=0.5)
               audio = self.rec.listen(source)
               try:
                    texto_reconocido[0] = self.rec.recognize_google(audio, language='es-ES')
                    print("Texto reconocido:", texto_reconocido[0])
               except sr.UnknownValueError:
                    print("No se pudo reconocer el audio")
               except sr.RequestError as e:
                    print("Error al realizar la solicitud al servicio de reconocimiento de voz; {0}".format(e))

    def stop(self):
        self.stop_event.set()

cameraMatriz = np.array([[610.27809167,   0.        , 309.09661634],
       [  0.        , 610.27809167, 233.72715096],
       [  0.        ,   0.        ,   1.        ]])
distCoeffs = np.array([[-3.72938563e+00],
       [-1.38273308e+01],
       [ 2.25774006e-03],
       [ 1.30140654e-03],
       [ 1.03818043e+02],
       [-3.80087886e+00],
       [-1.33634098e+01],
       [ 1.02730858e+02],
       [ 0.00000000e+00],
       [ 0.00000000e+00],
       [ 0.00000000e+00],
       [ 0.00000000e+00],
       [ 0.00000000e+00],
       [ 0.00000000e+00]])


vidas = [2]


imagen_atacar = cv2.imread('ataque.jpg')
imagen_recuperar = cv2.imread('recuperar.jpg')
imagen_proteger = cv2.imread('proteger.jpg')
imagen_confirmar = cv2.imread('confirmar.jpg')
imagen_carta = [imagen_atacar]

accion_elegida = [-1]

def aruco_display(corners, ids, rejected, image, texto):
    
	if len(corners) > 0:
		
		ids = ids.flatten()
		
		for (markerCorner, markerID) in zip(corners, ids):
			
			corners = markerCorner.reshape((4, 2))
			(topLeft, topRight, bottomRight, bottomLeft) = corners
			
			topRight = (int(topRight[0]), int(topRight[1]))
			bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
			bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
			topLeft = (int(topLeft[0]), int(topLeft[1]))

			cv2.line(image, topLeft, topRight, (0, 255, 0), 1)
			cv2.line(image, topRight, bottomRight, (0, 255, 0), 1)
			cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 1)
			cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 1)
			
			if (markerID == 0 or markerID == 10 or markerID == 20 or markerID == 30):
				accion_elegida[0] = markerID
				carta_detectada[0] = True
                
			cv2.putText(image, str(texto),(topLeft[0], topLeft[1] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
	return image


def augmentation(bbox, img, img_augment):
    top_left = bbox[0][0][0], bbox[0][0][1]
    top_right = bbox[0][1][0], bbox[0][1][1]
    bottom_right = bbox[0][2][0], bbox[0][2][1]
    bottom_left = bbox[0][3][0], bbox[0][3][1]

    height, width, _, = img_augment.shape

    points_1 = np.array([top_left, top_right, bottom_right, bottom_left])
    points_2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])

    matrix, _ = cv2.findHomography(points_2, points_1)
    image_out = cv2.warpPerspective(img_augment, matrix, (img.shape[1], img.shape[0]))
    cv2.fillConvexPoly(img, points_1.astype(int), (0, 0, 0))
    image_out = img + image_out

    return image_out

def pose_estimation(frame, aruco_dict_type, matrix_coefficients, distortion_coefficients,texto):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)

    corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, cv2.aruco_dict)

    if len(corners) > 0:
        for i in range(0, len(ids)):
           
            aruco_display(corners, ids, rejected_img_points, frame, texto)
            
            if accion_elegida[0] == 0:
                 imagen_carta[0] = imagen_atacar
            elif accion_elegida[0] == 10:
                 imagen_carta[0] = imagen_recuperar
            elif accion_elegida[0] == 20:
                 imagen_carta[0] = imagen_proteger
            elif accion_elegida[0] == 30:
                 imagen_carta[0] = imagen_confirmar
            frame = augmentation(np.array(corners)[0], frame,imagen_carta[0])

    return frame



def abrir_camara():
     aruco_type = cv2.aruco.DICT_4X4_100


     intrinsic_camera = np.array(((933.15867, 0, 657.59),(0,933.1586, 400.36993),(0,0,1)))
     distortion = np.array((-0.43948,0.18514,0,0))


     cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

     voice_thread = VoiceThread()
     

     texto = ""
     registro_batalla = ""
     vidas_enemigo = 2

     ataques_restantes = 2
     ataques_restantes_oponente = 2

     escudos_restantes = 2
     escudos_restantes_enemigo = 2

     ultima_carta = -99
     acciones = {
          0: "Atacar",
          10: 'Recuperar Fuerzas',
          20: 'Protegerse',
          30: 'Confirmar Accion'
     }

     probabilidad = 0
     accion_oponente = -1
     nivel = 1
     gameover = False
     mensaje_accion_actual = ""
     cara_reconocida = False
     jugador= "Desconocido"
     nuevosDatos = ""
     colorPreferido = 1
     color = (0,0,0)
     voice_thread.start()

     while cap.isOpened():
     
          ret, img = cap.read()
          output = pose_estimation(img, aruco_type, intrinsic_camera, distortion, texto)
          
          if cara_reconocida == False:
               framergb = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
               mini = cv2.resize(framergb, dsize=None, fx=0.5, fy=0.5)
               locs = face.face_locations(mini, model='hog')
               cods = face.face_encodings(mini, locs, model='large')
               if locs is not None:
                         for i in range(len(locs)):
                              if archivos != None:
                                   for nombre in archivos_txt:
                                        ruta = rutaCarpeta+ nombre
                                        cod_cara = np.loadtxt(ruta)
                                        print(ruta)
                                        dist = face.face_distance(cod_cara, [cods[i]])[0]
                                        distancia = f'{dist:.2f}'
                                        dist_as_int = float(distancia)
                                        if dist_as_int < 0.6:
                                             cara_reconocida = True
                                             jugador = nombre.replace(".txt","")
                                             colorPreferido = np.loadtxt(jugador+"Datos.txt")
                                             break
                                   if cara_reconocida == False:
                                        nueva_codificacion = input("Escribe tu nombre: ")
                                        jugador = nueva_codificacion
                                        nueva_codificacion += ".txt"
                                        nuevosDatos = jugador + "Datos.txt"
                                        
                                        dato = []
                                        res = ""
                                        while res not in ["1", "2", "3"]:
                                             res = input("Elige el tema: 1 (Rojo), 2 (Verde), 3 (Azul): ")
                                        dato.append(int(res))

                                        np.savetxt(nuevosDatos, dato)

                                        colorPreferido = int(res)

                                        print(colorPreferido)
                                        np.savetxt(nueva_codificacion, cods[0])

                                        cara_reconocida = True

                                   if colorPreferido == 1:
                                        color = (0,20,255)
                                   elif colorPreferido == 2:
                                        color = (0,250,150)
                                   else:
                                        color = (255,255,0)

          if carta_detectada[0] == False and cara_reconocida == True:
               imagen_negra = np.zeros_like(img)
               cv2.putText(imagen_negra, 'Bienvenido ' + jugador + "!",(10, 50), cv2.FONT_HERSHEY_COMPLEX,1.3,color,1)
               texto_introduccion = 'En este juego de realidad aumentada seras un guerrero que debera enfrentarse a sus oponentes armado con su mazo de 4 cartas:'
               cv2.putText(imagen_negra, texto_introduccion,(10, 90), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)
               texto_introduccion = 'Ataque: Blande tu espada y carga con todas tus fuerzas hacia el enemigo'
               cv2.putText(imagen_negra, texto_introduccion,(10, 130), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)
               texto_introduccion = 'Recuperar Fuerzas: Recuerda que hasta los mejores guerreros necesitan descansar de vez en cuando!'
               cv2.putText(imagen_negra, texto_introduccion,(10, 170), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)
               texto_introduccion = 'Protegerse: El enemigo devolvera los golpes, cubrete!'
               cv2.putText(imagen_negra, texto_introduccion,(10, 210), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)
               texto_introduccion = 'Confirmar Accion: Para cuando estes seguro de cual sera tu proximo movimiento.'
               cv2.putText(imagen_negra, texto_introduccion,(10, 250), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)

               texto_introduccion = 'No dejes que tu vida llegue a 0 o perderas!'
               cv2.putText(imagen_negra, texto_introduccion,(10, 310), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)
               texto_introduccion = 'Tras cada enemigo vencido se te concedera un respiro y tus stats se reiniciaran... pero el proximo sera mas duro.'
               cv2.putText(imagen_negra, texto_introduccion,(10, 350), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)
               texto_introduccion = 'Hasta donde podras llegar?'
               cv2.putText(imagen_negra, texto_introduccion,(10, 390), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)

               cv2.putText(imagen_negra, 'Para jugar muestra las cartas de accion o si lo prefieres usa los comandos de voz.',(10, 450), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)
               cv2.putText(imagen_negra, 'Ademas de los asociados a las cartas, dispones del comando "comenzar" y "terminar" para iniciar o finalizar la partida.',(10, 490), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)
               cv2.putText(imagen_negra, 'Usa el comando "comenzar" o muestra la carta de ataque para continuar.',(10, 530), cv2.FONT_HERSHEY_COMPLEX,0.5,color,1)
               
               if texto_reconocido[0] == "comenzar":
                    carta_detectada[0] = True
                    accion_elegida[0] = 0
                    texto_reconocido[0] = ""
               
                    
          
          elif carta_detectada[0] == True and cara_reconocida: 
                    
               mensaje_jugador= "Jugador: " + jugador
               mensaje_vidas = "Vidas restantes: " + str(vidas[0])
               mensaje_ataques_restantes = "Ataques restantes: " + str(ataques_restantes)
               mensaje_escudos_restantes = "Escudos restantes: " + str(escudos_restantes)
               
               mensaje_vidas_oponente = 'Vidas de tu oponente: ' + str(vidas_enemigo)
               mensaje_ataques_oponente = "Ataques de tu oponente: " + str(ataques_restantes_oponente)
               mensaje_escudos_restantes_oponente = "Escudos de tu oponente: " + str(escudos_restantes_enemigo)
               
               mensaje_registro_batalla = "Registro: " + registro_batalla
               mensaje_nivel_actual = "Nivel actual: " + str(nivel)

               cv2.putText(output, str(mensaje_jugador),(50, 50), cv2.FONT_HERSHEY_COMPLEX,0.8,color,1)
               cv2.putText(output, str(mensaje_vidas),(900, 50), cv2.FONT_HERSHEY_COMPLEX,0.8,color,1)
               cv2.putText(output, str(mensaje_ataques_restantes),(900, 80), cv2.FONT_HERSHEY_COMPLEX,0.8,color,1)
               cv2.putText(output, str(mensaje_escudos_restantes),(900, 110), cv2.FONT_HERSHEY_COMPLEX,0.8,color,1)

               cv2.putText(output, str(mensaje_vidas_oponente),(900, 150), cv2.FONT_HERSHEY_COMPLEX,0.8,color,1)
               cv2.putText(output, str(mensaje_ataques_oponente),(900, 180), cv2.FONT_HERSHEY_COMPLEX,0.8,color,1)
               cv2.putText(output, str(mensaje_escudos_restantes_oponente),(900, 210), cv2.FONT_HERSHEY_COMPLEX,0.8,color,1)
               
               cv2.putText(output, mensaje_nivel_actual,(10, 250), cv2.FONT_HERSHEY_COMPLEX,0.6,color,1)
               cv2.putText(output, mensaje_accion_actual,(10, 350), cv2.FONT_HERSHEY_COMPLEX,0.6,color,1)
               cv2.putText(output, str(mensaje_registro_batalla),(10, 650), cv2.FONT_HERSHEY_COMPLEX,0.6,color,1)

               #Resaltado en negro:
               cv2.putText(output, str(mensaje_jugador),(51, 49), cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,0),1)
               cv2.putText(output, str(mensaje_vidas),(901, 49), cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,0),1)
               cv2.putText(output, str(mensaje_ataques_restantes),(901, 79), cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,0),1)
               cv2.putText(output, str(mensaje_escudos_restantes),(901, 109), cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,0),1)

               cv2.putText(output, str(mensaje_vidas_oponente),(901, 149), cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,0),1)
               cv2.putText(output, str(mensaje_ataques_oponente),(901, 179), cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,0),1)
               cv2.putText(output, str(mensaje_escudos_restantes_oponente),(901, 209), cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,0),1)
               
               cv2.putText(output, mensaje_nivel_actual,(11, 249), cv2.FONT_HERSHEY_COMPLEX,0.6,(0,0,0),1)
               cv2.putText(output, mensaje_accion_actual,(11, 349), cv2.FONT_HERSHEY_COMPLEX,0.6,(0,0,0),1)
               cv2.putText(output, str(mensaje_registro_batalla),(11, 649), cv2.FONT_HERSHEY_COMPLEX,0.6,(0,0,0),1)
               
   
          #Cuando detectemos una carta
          if carta_detectada[0] == True or texto:
               texto = 'Carta: ' + acciones[accion_elegida[0]]
               if texto_reconocido[0] == "atacar":
                    accion_elegida[0] = 0
                    texto_reconocido[0] = ""
               if texto_reconocido[0] == "recuperar":
                    accion_elegida[0] = 10
                    texto_reconocido[0] = ""
               if texto_reconocido[0] == "proteger":
                    accion_elegida[0] = 20
                    texto_reconocido[0] = ""
               if texto_reconocido[0] == "confirmar":
                    accion_elegida[0] = 30
                    texto_reconocido[0] = ""
               #Si atacamos:
               if accion_elegida[0] == 0:
                    mensaje_accion_actual = "Accion actual: Atacar"
                    if ataques_restantes > 0:
                         ultima_carta = 0
                    else:
                         cv2.putText(output, "No puedes atacar de nuevo!",(200, 100), cv2.FONT_HERSHEY_COMPLEX,1,(0,0,200),1)
               
               #Si nos recuperamos
               elif accion_elegida[0] == 10:
                    mensaje_accion_actual = "Accion actual: Recuperar"
                    ultima_carta = 10
               #Si nos cubrimos
               elif accion_elegida[0] == 20:
                    mensaje_accion_actual = "Accion actual: Cubrirse"
                    if escudos_restantes > 0:
                         ultima_carta = 20
                    else:
                         cv2.putText(output, "No tienes mas escudos!",(200, 100), cv2.FONT_HERSHEY_COMPLEX,1,(0,0,200),1)
               
               #Si estamos seguro de nuestra elección y mostramos la carta de pasar al siguiente turno:
               if accion_elegida[0] == 30 and ultima_carta != -1 and gameover == False:
                    #Lógica del oponente:
                    accion_oponente = 10
                    #Si atacamos
                    if ultima_carta == 0:
                              #Si está a punto de morir:
                              if vidas_enemigo < 2 and escudos_restantes_enemigo > 0:
                                   #Se cubrirá:
                                   accion_oponente = 20
                              #En otro caso comprueba sus ataques, si no tiene, recargará:
                              elif ataques_restantes_oponente == 0:
                                   accion_oponente = 10
                              #Si no tiene que recargar ni cubrirse, siempre devolverá el golpe
                              elif ataques_restantes_oponente > 0:
                                   accion_oponente = 0
                    #Si recargamos:
                    elif ultima_carta == 10:
                         #Si le quedan ataques siempre nos intentará atacar
                         if ataques_restantes_oponente > 0:
                              accion_oponente = 0
                         #En otro caso aprovechará para recargar:
                         else:
                              accion_oponente = 10
                    #Si nos cubrimos:
                    elif ultima_carta == 20:
                         #Si tiene mas de un ataque, siempre nos intentará atacar:
                         if ataques_restantes_oponente > 1:
                              accion_oponente = 0
                         #En otro caso aprovechará para recargar:
                         else:
                              accion_oponente = 10
                    
                    #Calculamos el resultado de la ronda:
                    #Si atacamos
                    if ultima_carta == 0:
                         #Calculamos la probabilidad de golpear con éxito:
                         probabilidad = random.randint(1, 3)
                         registro_batalla = "Ataque lanzado..."
                         #Si el enemigo se cubre:
                         if accion_oponente == 20:
                              registro_batalla += " El enemigo se protegio del ataque!"
                              escudos_restantes_enemigo -= 1
                         #Si el enemigo recarga:
                         elif accion_oponente == 10:
                              if probabilidad < 3:
                                   vidas_enemigo -= 1
                              registro_batalla += " Golpeado!"
                              escudos_restantes_enemigo = 2
                              registro_batalla += " El enemigo recupero fuerzas!"
                         #Si el enemigo ataca:
                         elif accion_oponente == 0:
                              ataques_restantes_oponente -= 1
                              if probabilidad < 3:
                                   vidas_enemigo -= 1
                              registro_batalla += " Golpeado!"
                              #Calculamos su probabilidad de ataque:
                              probabilidad_ataque_enemigo = random.randint(1, 3)
                              if probabilidad_ataque_enemigo < 3:
                                   vidas[0] -= 1
                                   registro_batalla += " El enemigo te devuelve el golpe!"
                              elif probabilidad_ataque_enemigo == 3:
                                   registro_batalla += " El enemigo intenta devolver el golpe pero falla!"
                    
                         if probabilidad == 3:
                              registro_batalla += " Fallo tu ataque!"
                         #Nos quedará un turno de ataque menos:
                         ataques_restantes -= 1
                    #Si recargamos
                    elif ultima_carta == 10:
                         #Reestablecemos los ataques
                         ataques_restantes = 2
                         registro_batalla = "Se han restaurado los ataques."
                         #Si nos intenta golpear:
                         if accion_oponente == 0:
                              registro_batalla += " El enemigo aprovecha para atacarte"
                              probabilidad_ataque_enemigo = random.randint(1, 3)
                              ataques_restantes_oponente -= 1
                              if probabilidad < 3:
                                   vidas[0] -= 1
                                   registro_batalla += " y te golpea!"
                              elif probabilidad == 3:
                                   registro_batalla += " pero falla!"
                         #Si recarga:
                         elif accion_oponente == 10:
                              ataques_restantes_oponente = 2
                              registro_batalla += " El enemigo aprovecha para recuperarse."
                    
                    # Si nos cubrimos:
                    elif ultima_carta == 20:
                         registro_batalla = "Escudo levantado..."
                         escudos_restantes -= 1
                         if accion_oponente == 0:
                              ataques_restantes_oponente -= 1
                              registro_batalla += " El enemigo intento atacarte pero repeliste el ataque."
                         elif accion_oponente == 10:
                              registro_batalla += " El enemigo aprovecha para recuperarse"
                              ataques_restantes_oponente = 2
                    
                    if vidas[0] == 0 or vidas_enemigo == 0:
                         gameover = True
                         registro_batalla += " Fin del juego."
          
                    ultima_carta = -1

               #Comprobamos en que condiciones ha acabado el juego:
               if gameover and vidas[0] == 0 and vidas_enemigo > 0:
                    cv2.putText(output, "Has muerto",(100, 100), cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),1)
               elif vidas[0] > 0 and vidas_enemigo == 0:
                    cv2.putText(output, "Has derrotado a tu oponente",(100, 100), cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),1)
               elif vidas[0] == 0 and vidas_enemigo == 0:
                    cv2.putText(output, "Empate",(100, 100), cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),1)

               #Cuando haya acabado el juego:
               if gameover:
                    cv2.putText(output, 'Muestra la carta de atacar para continuar',(20, 420), cv2.FONT_HERSHEY_COMPLEX,1.1,color,1)
                    cv2.putText(output, 'Muestra la carta de atacar para continuar',(21, 4199), cv2.FONT_HERSHEY_COMPLEX,1.1,(0,0,0),1)
                    if accion_elegida[0] == 0:
                         #Si morimos o empatamos se reiniciarán las estadísticas:
                         if vidas[0] == 0:
                              nivel = 1
                              vidas[0] = 2
                              vidas_enemigo = 2
                              ataques_restantes = 2
                              ataques_restantes_oponente = 2
                              escudos_restantes = 2
                              escudos_restantes_enemigo = 2
                         #Si no pasaremos de nivel y el enemigo tendrá cada vez más ventaja:
                         else:
                              nivel += 1
                              vidas[0] = 2
                              vidas_enemigo = 1+nivel
                              ataques_restantes = 2
                              ataques_restantes_oponente = 1+nivel
                              escudos_restantes = 2
                              escudos_restantes_enemigo = 1+nivel

                         gameover = False
                         accion_elegida[0] = -1
                         accion_oponente = -1
                         registro_batalla = ""
                         
          if carta_detectada[0] == False and cara_reconocida == True:
               cv2.imshow('CUIA', imagen_negra) 
          else:
               cv2.imshow('CUIA', output)

          key = cv2.waitKey(1) & 0xFF
          if key == ord('q') or texto_reconocido[0] == "terminar":
               texto_reconocido[0] = ""
               break

     carta_detectada[0] = False
     cap.release()
     cv2.destroyAllWindows()
     voice_thread.stop()


ventana = tk.Tk()
ventana.geometry("980x720")

imagen_fondo = Image.open("fondo.png")
imagen_fondo = imagen_fondo.resize((980, 720), Image.ANTIALIAS) 
fondo = ImageTk.PhotoImage(imagen_fondo)
label_fondo = tk.Label(ventana, image=fondo)
label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
btn_comenzar = tk.Button(ventana, text="Comenzar", command=abrir_camara)
btn_salir = tk.Button(ventana, text="Salir", command=ventana.quit)
btn_comenzar.pack()
btn_salir.pack()
btn_comenzar.place(x=150, y=350)
btn_salir.place(x=160, y=400)
ventana.mainloop()