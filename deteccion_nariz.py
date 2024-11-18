import cv2
import mediapipe as mp

class DeteccionNariz:
    def __init__(self):
        # Inicializar Mediapipe para detección de malla facial
        self.mp_face_mesh = mp.solutions.face_mesh #Module (mp.solutions.face_mesh)
        self.face_mesh = self.mp_face_mesh.FaceMesh() #FaceMesh

    def detectar_nariz(self, frame):
        # Convertir la imagen a RGB ya que Mediapipe requiere este formato
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesar la imagen para detectar puntos faciales
        resultado = self.face_mesh.process(rgb_frame)
        
        if resultado.multi_face_landmarks:
            for face_landmarks in resultado.multi_face_landmarks:
                # Acceder al punto de la nariz (índice 1 en Mediapipe)
                nariz = face_landmarks.landmark[1]
                altura, ancho, _ = frame.shape
                cx, cy = int(nariz.x * ancho), int(nariz.y * altura)
                
                # Dibujar un círculo en la nariz detectada
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                
                # Devolver las coordenadas de la nariz
                return (cx, cy)
        
        # Si no se detecta la nariz, devolver None
        return None

    def liberar_recursos(self):
        # Liberar los recursos de Mediapipe
        self.face_mesh.close()
