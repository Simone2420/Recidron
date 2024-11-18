import pygame
import random

class Objeto:
    def __init__(self, tipo, imagen, vida, dimensiones, dispara=False):
        self._tipo = tipo #string
        self.imagen = pygame.image.load(imagen) #Image
        self.imagen = pygame.transform.scale(self.imagen, dimensiones) 
        self.vida = vida #int
        self.__dimensiones = dimensiones #list
        self.__dispara = dispara #bool
        self.velocidad = 5 #int
        self.posicion_x = -100  #float
        self.posicion_y = -100 #float
        self.__puntos = 0 #int
    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, (self.posicion_x, self.posicion_y))
    def get_tipo(self):
        return self._tipo

    def get_dimensiones(self):
        return self.__dimensiones

    def set_tipo(self, tipo):
        self._tipo = tipo

    def set_dimensiones(self, dimensiones):
        self.__dimensiones = dimensiones

    def set_dispara(self, dispara):
        if dispara in (True, False):
            self.__dispara = dispara
        else:
            print("Solo se admiten valores booleanos (True o False)")

    def get_dispara(self):
        return self.__dispara

    def aparecer(self, screen_width, screen_height, tasa_aparicion):
        if random.random() < tasa_aparicion:
            self.posicion_x = random.randint(0, screen_width - self.get_dimensiones()[0])
            self.posicion_y = random.randint(0, screen_height//2 - self.get_dimensiones()[1])
            #print(f"{self.get_tipo()} apareció en posición ({self.posicion_x}, {self.posicion_y})")

    def colisionar(self, otro):
        objeto_rect = pygame.Rect(self.posicion_x, self.posicion_y, *self.get_dimensiones())
        dron_rect = pygame.Rect(otro.posicion_x, otro.posicion_y, *otro.get_dimensiones())
        return objeto_rect.colliderect(dron_rect)

    def __repr__(self):
        return f"{self._tipo}" 


    def recibir_dano(self, cantidad_dano):
        self.vida -= cantidad_dano
        #print(f"{self._tipo} recibió {cantidad_dano} de daño. Vida restante: {self.vida}")
        if self.vida <= 0:
            self.invocar_morir()

    def __morir(self):
        print(f"{self._tipo} ha sido destruido.")
        self.posicion_x, self.posicion_y = -100, -100  # Elimina el objeto de la pantalla

    def invocar_morir(self):
        self.__morir()

class Basura(Objeto):
    def __init__(self, tipo, imagen, vida, dimensiones, tasa_aparicion,puntos):
        super().__init__(tipo, imagen, vida, dimensiones)
        self.tasa_aparicion = tasa_aparicion #float
        self.__puntos = puntos #int
        self.velocidad = 0.5 #float

    def aparecer(self, screen_width, screen_height):
        super().aparecer(screen_width, screen_height, self.tasa_aparicion)

    def get_puntos(self):
        return self.__puntos

class Planta(Objeto):
    def __init__(self, tipo, imagen, vida, dimensiones, tasa_aparicion):
        super().__init__(tipo, imagen, vida, dimensiones)
        self.tasa_aparicion = tasa_aparicion #float
        self.velocidad = 2 #int

    def aparecer(self, ancho_pantalla, alto_pantalla):
        super().aparecer(ancho_pantalla, alto_pantalla, self.tasa_aparicion)

class Dron(Objeto):
    def __init__(self, tipo, imagen, vida, dimensiones):
        super().__init__(tipo, imagen, vida, dimensiones)
        super().set_dispara(True)
        super().set_tipo("Dron")
        self.proyectiles = [] #list
        self.posicion_x = 0 #float
        self.posicion_y = 300 #float
        self.coeficiente_escala = 1.0 #float
        self.direccion_expansion = 1 #float
        self.escala_min = 0.9 #float
        self.escala_max = 1.2 #float
        self.velocidad_expansion = 0.01 #float
        self.__puntos = 0 #int
        self.vida_i = self.vida #int
        
    def aumentar_puntaje(self, puntos):
        self.__puntos += puntos
    def set_puntaje(self, puntos):
        self.__puntos = puntos
    def movimiento(self, keys):
        if keys[pygame.K_LEFT]:
            self.posicion_x -= self.velocidad
        if keys[pygame.K_RIGHT]:
            self.posicion_x += self.velocidad
        if keys[pygame.K_UP]:
            self.posicion_y -= self.velocidad
        if keys[pygame.K_DOWN]:
            self.posicion_y += self.velocidad
    def movimiento_ia(self, nariz_x, nariz_y):
        # Mueve el dron hacia la posición de la nariz
        if nariz_x is not None and nariz_y is not None:
            if nariz_x < self.posicion_x:
                self.posicion_x += self.velocidad
            elif nariz_x < self.posicion_x:
                self.posicion_x -= self.velocidad
            if nariz_y < self.posicion_y:
                self.posicion_y += self.velocidad
            elif nariz_y > self.posicion_y:
                self.posicion_y -= self.velocidad

    def contraccion(self,pantalla):
        self.coeficiente_escala += self.direccion_expansion * self.velocidad_expansion
        if self.coeficiente_escala >= self.escala_max or self.coeficiente_escala <= self.escala_min:
            self.direccion_expansion *= -1  # Cambia la dirección
        scaled_image = pygame.transform.scale(self.imagen, 
                                       (int(self.get_dimensiones()[0] * self.coeficiente_escala), 
                                        int(self.get_dimensiones()[1] * self.coeficiente_escala)))
        pantalla.blit(scaled_image, (self.posicion_x, self.posicion_y))
        pygame.display.flip()

    def disparar(self):
        # Crea un proyectil y lo añade a la lista de proyectiles
        nuevo_proyectil = Proyectil(self.posicion_x + self.get_dimensiones()[0] // 2, self.posicion_y, velocidad=10, daño=1)
        self.proyectiles.append(nuevo_proyectil)

    def mover_proyectiles(self, juego):
        # Mueve y dibuja cada proyectil, y verifica colisiones
        for proyectil in self.proyectiles[:]:
            proyectil.mover()
            proyectil.dibujar(juego.pantalla)
            for objeto in juego.objetos:
                if proyectil.colisiona_con(objeto):
                    # Incrementa el puntaje según el tipo de objeto
                    if isinstance(objeto, Basura):
                        if objeto.get_tipo() == "bolsa":
                            self.aumentar_puntaje(3)
                        elif objeto.get_tipo() == "botella":
                            self.aumentar_puntaje(2)
                        else:
                            self.aumentar_puntaje(1)
                    elif isinstance(objeto, Planta):
                        self.invocar_morir() 
                        juego.fin_juego() # El dron muere al colisionar con plantas o flores
                        return
                    
                    objeto.recibir_dano(proyectil.daño)
                    self.proyectiles.remove(proyectil)
                    break  # Sale del bucle una vez que el proyectil colisiona con un objeto

    def recibir_dano(self, cantidad):
        # Reduce la vida del dron
        self.vida -= cantidad
        print(f"Vida del dron: {self.vida}")
        if self.vida <= 0:
            self.invocar_morir()
    def get_puntaje(self):
        return self.__puntos


class Proyectil:
    def __init__(self, x, y, velocidad, daño):
        self.x = x #float
        self.y = y #float
        self.velocidad = velocidad #float
        self.daño = daño #int
        self.width = 5  #int
        self.height = 10  #int
        self.color = (0, 0, 0)  #tuple

    def mover(self):
        # Mueve el proyectil hacia arriba en la pantalla
        self.y -= self.velocidad

    def dibujar(self, ventana):
        # Dibuja el proyectil en la pantalla
        pygame.draw.rect(ventana, self.color, (self.x, self.y, self.width, self.height))

    def colisiona_con(self, objeto):
        # Verifica si el proyectil colisiona con un objeto
        return (self.x < objeto.posicion_x + objeto.get_dimensiones()[0] and
                self.x + self.width > objeto.posicion_x and
                self.y < objeto.posicion_y + objeto.get_dimensiones()[1] and
                self.y + self.height > objeto.posicion_y)