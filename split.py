#Mario Guisado García
import cv2
import numpy as np
lena = cv2.imread('lena.tif')

b, g, r = cv2.split(lena)

lena[:,:,0] = 0
lena[:,:,1] = 0
lena[:,:,2] = r
cv2.imshow('Rojo', lena)

lena[:,:,0] = 0
lena[:,:,1] = g
lena[:,:,2] = 0
cv2.imshow('Verde', lena)


lena[:,:,0] = b
lena[:,:,1] = 0
lena[:,:,2] = 0
cv2.imshow('Azul', lena)

cv2.waitKey()
cv2.destroyAllWindows()
