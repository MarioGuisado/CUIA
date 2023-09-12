import cv2
import numpy as np
lena = cv2.imread('lena.tif')
anel = cv2.flip(lena, 1)
mezcla = cv2.addWeighted(lena, 0.5, anel, 0.5, 0)
cv2.imshow('MEZCLA', mezcla)
cv2.waitKey()
cv2.destroyAllWindows()