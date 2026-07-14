import math
import pygame
import constantes
import random

class Weapon():
    def __init__(self,image,imagen_bala):
        self.imagen_bala=imagen_bala
        self.image_original=image
        self.angulo=0
        self.image=pygame.transform.rotate(self.image_original,self.angulo)
        self.forma=self.image.get_rect()
        self.disparar=False
        self.ultimo_Disparo=pygame.time.get_ticks()


    def update(self, personaje):
        disparo_cooldaown=constantes.COOLDOWN_BALA
        bala=None
        self.forma.center = personaje.forma.center
        if personaje.flip == False:
            self.forma.x = self.forma.x + personaje.forma.width / 2
            self.rotar_Arma(False)

        if personaje.flip == True:
            self.forma.x = self.forma.x - personaje.forma.width / 2
            self.rotar_Arma(True)

        #Mover pistola

        mouse_pos=pygame.mouse.get_pos()
        distanciax=mouse_pos[0]-self.forma.centerx
        diferencia_y=-(mouse_pos[1]-self.forma.centery)
        self.angulo=math.degrees(math.atan2(diferencia_y,distanciax))

        #detectar los clicks
        if pygame.mouse.get_pressed()[0] and self.disparar==False and (pygame.time.get_ticks()-self.ultimo_Disparo>=disparo_cooldaown) :
            bala=Bala(self.imagen_bala,self.forma.centerx,self.forma.centery,self.angulo)
            self.ultimo_Disparo=pygame.time.get_ticks()
            self.disparar=True
            #RESET MOUSE
        if pygame.mouse.get_pressed()[0]==False:
            self.disparar=False
        return bala


    def rotar_Arma(self, rotar ):
        if rotar==True:
            image_flip=pygame.transform.flip(self.image_original,
                                             True,False)
            self.image = pygame.transform.rotate(image_flip, self.angulo)
        else :
            image_flip=pygame.transform.flip(self.image_original,
                                             False, False)
            self.image = pygame.transform.rotate(image_flip, self.angulo)

    def dibujar(self, interfaz):

        self.image=pygame.transform.rotate(self.image, self.angulo)

        interfaz.blit(self.image, self.forma)
        pygame.draw.rect(interfaz, constantes.COLOR, self.forma, 1)


class Bala (pygame.sprite.Sprite):
    def __init__(self,image,x,y,angle):
        pygame.sprite.Sprite.__init__(self)
        self.image_original=image
        self.angle=angle
        self.image=pygame.transform.rotate(self.image_original,self.angle)
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        #CALCULAR LA VELOCIDAD DE LAS BALAS
        self.deta_x=math.cos(math.radians(self.angle))*constantes.VELOCIDAD_BALA
        self.deta_y=-math.sin(math.radians(self.angle))*constantes.VELOCIDAD_BALA

    def update(self, lista_enemigos):
        daño=0
        pos_daño=None
        self.rect.x+=self.deta_x
        self.rect.y+= self.deta_y

        if self.rect.right < 0 or self.rect.left>constantes.ANCHO_ventana or self.rect.top<0 or self.rect.bottom>constantes.ALTO_ventana:
            self.kill()

    #VERIFICAR COLISIONES
        for enemigo in lista_enemigos :
            if enemigo.forma.colliderect(self.rect):
                daño=15+random.randint(-7,7)
                pos_daño=enemigo.forma
                enemigo.energia=enemigo.energia-daño
                self.kill()
                break
        return daño,pos_daño

    def dibujar(self,interfaz):
        interfaz.blit(self.image, (self.rect.centerx,
                                    self.rect.centery-int(self.image.get_height()/2),))
