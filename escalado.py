import cv2
import numpy as np
lena = cv2.imread('lena.tif')

minilena = cv2.resize(lena, None, fx=0.5, fy=0.5)

cv2.imshow('LENA', minilena)
cv2.waitKey()
cv2.destroyAllWindows()
