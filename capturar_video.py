# capturar_video.py
import cv2

class VideoCapture:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  #VideoCapture

    def obtener_frame(self):
        # Captura un frame de la cámara
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def liberar(self):
        # Libera la cámara
        self.cap.release()
        cv2.destroyAllWindows()
