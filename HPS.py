import cv2

# Load the OpenPose model
net = cv2.dnn.readNetFromTensorflow('path/to/model.pb')

# Load the input image
image = cv2.imread('C:\Users\Usuario\Pictures\running.jpg')

# Preprocess the image
image = cv2.resize(image, (320, 240))
image = cv2.dnn.blobFromImage(image, 1.0 / 255, (320, 240), (0, 0, 0), swapRB=False, crop=False)

# Run the model
net.setInput(image)
output = net.forward()

# Visualize the keypoints
for i in range(0, output.shape[0]):
    # Draw circles on the keypoints
    for j in range(0, output.shape[1]):
        x = int(output[i,j,0] * image.shape[3])
        y = int(output[i,j,1] * image.shape[2])
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)

# Show the output image
cv2.imshow('Output', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
