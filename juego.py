import pygame
from objetos import Dron, Basura, Planta  # Asegúrate de que estos objetos están definidos correctamente
import random
from capturar_video import VideoCapture
from deteccion_nariz import DeteccionNariz
import cv2
import time

def pantalla_dinamica():
    pygame.init()
    pantalla = pygame.display.Info()
    pantalla_alto = pantalla.current_h - 60
    return pantalla_alto

pantalla_dinamica = pantalla_dinamica()
class Juego:
    def __init__(self, ancho_pantalla=pantalla_dinamica, alto_pantalla=pantalla_dinamica):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla)) #Screen
        pygame.display.set_caption("Recidron")
        self.reloj = pygame.time.Clock() # Clock
        self.ejecutando = True #bool
        self.ancho_pantalla = ancho_pantalla #int
        self.alto_pantalla = alto_pantalla #int
        self.color_fondo = (240, 240, 240) #tuple
        
        # Crear la instancia del dron
        self.dron = Dron("Dron", r"imagenes\dron.png", 2, (100, 100)) #Dron Object
        self.mejor_puntaje = 0
        self.font_puntaje = pygame.font.Font(None, 36) #Font
        self.tiempo_disparo = 2
        self.ultimo_tiempo_disparo = 0
        # Lista para los objetos
        self.objetos = [] #list
        self.detector_nariz = DeteccionNariz() #DectetorNariz
        self.captura_video = VideoCapture() #VideoCapture
    def actualizar_mejor_puntaje(self):
        puntaje_actual = self.dron.get_puntaje()
        if puntaje_actual > self.mejor_puntaje:
            self.mejor_puntaje = puntaje_actual
    def mostrar_mejor_puntaje(self):
        text_mejor_puntaje = self.font_puntaje.render(f"Mejor Puntaje: {self.mejor_puntaje}", True, (0, 0, 255))
        self.pantalla.blit(text_mejor_puntaje, (10, 90))
    def disparar_automaticamente(self):
        tiempo_actual = time.time()
        if tiempo_actual - self.ultimo_tiempo_disparo >= self.tiempo_disparo:
            self.dron.disparar()  # Dispara
            self.ultimo_tiempo_disparo = tiempo_actual

    def generar_objeto(self):
        tipo = random.choice(['bolsa', 'botella', 'papel', 'planta', 'flor'])
        if tipo in ['planta', 'flor']:
            objeto = Planta(tipo, f"imagenes/{tipo}.png", 1, (75, 75), 0.002)
        else:
            if tipo == 'bolsa':
                objeto = Basura(tipo, f"imagenes/{tipo}.png", 1, (75, 75), 0.005,3)
            elif tipo == 'botella':
                objeto = Basura(tipo, f"imagenes/{tipo}.png", 1, (75, 75), 0.007,2)
            else:
                objeto = Basura(tipo, f"imagenes/{tipo}.png", 1, (75, 75), 0.008,1)
        
        objeto.aparecer(self.ancho_pantalla, self.alto_pantalla)
        self.objetos.append(objeto)
    def ciclo(self):
        for objeto in self.objetos:
            objeto.dibujar(self.pantalla)
            if objeto.posicion_y > self.alto_pantalla:
                objeto.posicion_y = -100
            if isinstance(objeto, Basura):
                objeto.posicion_y += objeto.velocidad
                if objeto.colisionar(self.dron):
                    self.dron.recibir_dano(1)
                    self.objetos.remove(objeto)
            elif isinstance(objeto, Planta):
                objeto.posicion_y += objeto.velocidad
                if objeto.colisionar(self.dron):
                    self.fin_juego()
    def mostrar_puntaje(self):
        text_puntaje = self.font_puntaje.render(f"Puntaje: {self.dron.get_puntaje()}", True, (255, 0, 0))
        self.pantalla.blit(text_puntaje, (10, 10))
    #mostrar vida del dron
    def mostrar_vida(self):
        text_vida = self.font_puntaje.render(f"Vida: {self.dron.vida}", True, (255, 0, 0))
        self.pantalla.blit(text_vida, (10, 50))
    
    def run(self):
        while self.ejecutando:
            # Manejo de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.ejecutando = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dron.disparar()

            # Generar objetos al azar
            for _ in range(5):
                self.generar_objeto()
            # Llenar la pantalla con el color de fondo y mostrar el puntaje
            self.pantalla.fill(self.color_fondo)
            self.mostrar_puntaje()
            self.actualizar_mejor_puntaje()
            self.mostrar_mejor_puntaje()
            self.mostrar_vida()
            self.ciclo()
            keys = pygame.key.get_pressed()
            self.dron.movimiento(keys)
            self.dron.mover_proyectiles(self)
                    
            self.dron.posicion_x = max(0, min(self.ancho_pantalla - self.dron.get_dimensiones()[0], self.dron.posicion_x))
            self.dron.posicion_y = max(0, min(self.alto_pantalla - self.dron.get_dimensiones()[1], self.dron.posicion_y))
            self.dron.contraccion(self.pantalla)

            pygame.display.flip()
            self.reloj.tick(60)

        pygame.quit()
    def run_ia(self):
        while self.ejecutando:
            frame = self.captura_video.obtener_frame()
            if frame is None:
                print("Error al capturar el video.")
                break
            frame = cv2.resize(frame, (self.ancho_pantalla, self.alto_pantalla))
            nariz_pos = self.detector_nariz.detectar_nariz(frame)
            if nariz_pos:
                x_nariz, y_nariz = nariz_pos
                dron_ancho = self.dron.imagen.get_width()
                dron_alto = self.dron.imagen.get_height()

                # Centrar el dron en la nariz
                self.dron.posicion_x = x_nariz - dron_ancho // 2
                self.dron.posicion_y = y_nariz - dron_alto // 2

                # Lógica para que el dron no salga de la pantalla
                self.dron.posicion_x = max(0, min(self.ancho_pantalla - dron_ancho, self.dron.posicion_x))
                self.dron.posicion_y = max(0, min(self.ancho_pantalla - dron_alto, self.dron.posicion_y))

                #print(f"Nariz detectada en: {nariz_pos}")
            # Convertir frame de OpenCV (BGR) a formato de Pygame (RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb)
            frame_surface = pygame.transform.rotate(frame_surface, -90)  # Rotar la imagen si es necesario
            frame_surface = pygame.transform.flip(frame_surface, True, False)  # Espejar la imagen si es necesario
            self.pantalla.blit(frame_surface, (0, 0))
            self.dron.mover_proyectiles(self)
            self.dron.contraccion(self.pantalla)
            self.disparar_automaticamente()
            self.actualizar_mejor_puntaje()
            self.mostrar_mejor_puntaje()
            # Dibujar el dron en la pantalla
            self.pantalla.blit(self.dron.imagen, (self.dron.posicion_x, self.dron.posicion_y))
            for _ in range(5):
                self.generar_objeto()
            # Llenar la pantalla con el color de fondo y mostrar el puntaje
            self.mostrar_puntaje()
            self.mostrar_vida()
            self.ciclo()
            # Actualizar pantalla
            pygame.display.flip()

            # Manejo de eventos para salir del bucle
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.ejecutando = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.dron.disparar()
        # Liberar recursos
        self.captura_video.liberar()  # Asegúrate de que esta función esté implementada en VideoCapture
        self.detector_nariz.liberar_recursos()  # Libera recursos del detector de nariz
        pygame.quit()

    def reiniciar_juego(self):
        self.dron.set_puntaje(0)
        self.dron.vida = self.dron.vida_i
        self.objetos.clear()  # Limpia la lista de objetos
        self.dron.posicion_x = self.ancho_pantalla/2  # Resetea la posición del dron
        self.dron.posicion_y = self.alto_pantalla 

    def fin_juego(self):
        # Lógica para mostrar la pantalla de fin de juego
        while True:
            self.pantalla.fill(self.color_fondo)
            font = pygame.font.Font(None, 74)
            text = font.render("Fin del juego", True, (0, 0, 0))
            self.pantalla.blit(text, (self.ancho_pantalla // 2 - text.get_width() // 2, 50))
            # Crear botón volver al menú
            button_color = (210, 210, 210)
            button_width = 380
            button_height = 70
            button_rect = pygame.Rect(self.ancho_pantalla // 2 - button_width // 2, 170, button_width, button_height)
            pygame.draw.rect(self.pantalla, button_color, button_rect)
            menu = font.render("Volver al menú", True, (0, 0, 0))
            self.pantalla.blit(menu, (button_rect.x + button_width // 2 - menu.get_width() // 2, button_rect.y + 10))
            puntaje = font.render(f"Puntaje: {self.dron.get_puntaje()}", True, (0, 0, 0))
            self.pantalla.blit(puntaje, (self.ancho_pantalla // 2 - puntaje.get_width() // 2, 250))
            text_mejor_puntaje = font.render(f"Mejor Puntaje: {self.mejor_puntaje}", True, (0, 0, 255))
            self.pantalla.blit(text_mejor_puntaje, (self.ancho_pantalla // 2 - text_mejor_puntaje.get_width() // 2, 320))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.mostrar_menu()
                        return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if button_rect.collidepoint(mouse_pos):
                        self.reiniciar_juego()
                        self.mostrar_menu()
                        return
            
            pygame.display.flip()
            self.reloj.tick(60)
    def mostrar_descripcion(self):
        descripcion_texto = [
            "Tu objetivo es eliminar la mayor cantidad de basura posible,",
            "sin eliminar a las plantas. Si eliminas a las plantas,",
            "morirás inmediatamente. El dron no debe colisionar",
            "ni con plantas ni con basura. ¡Buena suerte!"
        ]
        font_titulo = pygame.font.Font(None, 74)
        font_texto = pygame.font.Font(None, 36)
        titulo = font_titulo.render("Descripción", True, (0, 0, 0))
        # Botón para volver al menú principal
        button_color = (210, 210, 210)
        button_width, button_height = 250, 50
        button_rect = pygame.Rect(self.ancho_pantalla // 2 - button_width // 2, 350, button_width, button_height)
        while True:
            self.pantalla.fill(self.color_fondo)
            # Dibujar el título
            self.pantalla.blit(titulo, (self.ancho_pantalla // 2 - titulo.get_width() // 2, 50))
            # Dibujar cada línea de texto en el centro de la pantalla
            for i, linea in enumerate(descripcion_texto):
                texto = font_texto.render(linea, True, (0, 0, 0))
                self.pantalla.blit(texto, (self.ancho_pantalla // 2 - texto.get_width() // 2, 150 + i * 40))
            # Dibujar el botón
            pygame.draw.rect(self.pantalla, button_color, button_rect)
            texto_boton = font_texto.render("Volver al menú", True, (0, 0, 0))
            self.pantalla.blit(texto_boton, (button_rect.x + button_width // 2 - texto_boton.get_width() // 2, button_rect.y + 10))
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if button_rect.collidepoint(mouse_pos):
                        self.mostrar_menu()
                        return
            pygame.display.flip()
            self.reloj.tick(60)

    def mostrar_menu(self):
        while True:
            self.pantalla.fill(self.color_fondo)
            font = pygame.font.Font(None, 74)
            text = font.render("Menu", True, (0, 0, 0))
            self.pantalla.blit(text, (self.ancho_pantalla // 2 - text.get_width() // 2, 50))


            # Crear botones
            button_color = (200, 200, 200)
            button_width = 680
            button_height = 70
            button1_rect = pygame.Rect(self.ancho_pantalla // 2 - button_width // 2, 150, button_width, button_height)
            button2_rect = pygame.Rect(self.ancho_pantalla // 2 - button_width // 2, 250, button_width, button_height)
            button3_rect = pygame.Rect(self.ancho_pantalla // 2 - button_width // 2, 350, button_width, button_height)
            # Dibuja los botones
            pygame.draw.rect(self.pantalla, button_color, button1_rect)
            pygame.draw.rect(self.pantalla, button_color, button2_rect)
            pygame.draw.rect(self.pantalla, button_color, button3_rect)
            # Renderiza el texto sobre los botones
            text1_button = font.render("1.) Jugar sin IA", True, (0, 0, 0))
            text2_button = font.render("2.) Jugar con IA", True, (0, 0, 0))
            text3_button = font.render("3.) Descripción del juego", True, (0, 0, 0))
            self.pantalla.blit(text1_button, (button1_rect.x + button_width // 2 - text1_button.get_width() // 2, 
                                             button1_rect.y + button_height // 2 - text1_button.get_height() // 2))
            self.pantalla.blit(text2_button, (button2_rect.x + button_width // 2 - text2_button.get_width() // 2, 
                                             button2_rect.y + button_height // 2 - text2_button.get_height() // 2))
                                            # Dibujar el botón de descripción
            self.pantalla.blit(text3_button, (button3_rect.x + button_width // 2 - text3_button.get_width() // 2,
                                             button3_rect.y + button_height // 2 - text3_button.get_height() // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:  # Jugar sin IA
                        self.run()
                        return
                    elif event.key == pygame.K_2:  # Jugar con IA
                        self.reiniciar_juego()
                        self.run_ia()
                        return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if button1_rect.collidepoint(mouse_pos):
                        self.reiniciar_juego()  # Botón 1
                        self.run()
                        return
                    elif button2_rect.collidepoint(mouse_pos):  # Botón 2
                        self.reiniciar_juego()
                        self.run_ia()
                        return
                    elif button3_rect.collidepoint(mouse_pos):
                        self.reiniciar_juego()  # Botón 3
                        self.mostrar_descripcion()
# Ejecución del juego
if __name__ == "__main__":
    juego = Juego(pantalla_dinamica,pantalla_dinamica)
    juego.mostrar_menu()
