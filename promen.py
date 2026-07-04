import pygame
import sys
from pygame.locals import *
import random

def fit_square(img_path,size):
    img=pygame.image.load(img_path).convert_alpha()
    img_w,img_h=img.get_size()

    minsize=max(img_w,img_h)
    scale=size/minsize
    
    setW=int(img_w*scale)
    setH=int(img_h*scale)

    img=pygame.transform.smoothscale(img,(setW,setH))

    canvas =pygame.Surface((size,size),pygame.SRCALPHA)
    canvas.fill((0,0,0,0))

    offsetX=(size-setW)//2
    offsetY=(size-setH)//2

    canvas.blit(img,(offsetX,offsetY))
    return canvas


class AttackCircle:
    def __init__(self):
        self.flag=True
        self.goalr=100
        self.currentr=0
        self.pos=centerpos[0]
    
    def gradual(self):
        Growtime=3
        self.currentr=self.currentr+self.goalr/Growtime*dt
        
        if self.currentr<self.goalr-0.5:
            pygame.draw.circle(grid,(200,10,10,64),self.pos,self.currentr)
        else:
            pygame.draw.circle(grid,(200,10,10,255),self.pos,self.currentr)
        
        return self.currentr
    
    def flagupdate(self):
        if self.currentr>self.goalr:
            self.flag=True
            self.currentr=0
        else :
            self.flag=False

    def setpos(self,available):
        if(self.flag):
            self.pos=random.choice(available)
        return self.pos
    
class bulletManager:
    def __init__(self):
        self.bullets=[]
        self.availablepos=centerpos.copy()
        self.numberbullets=0
        self.count=0
    def makebullets(self):
        if self.numberbullets<9:
            self.bullets.append(AttackCircle())

    def updates(self):
        for bullet in self.bullets:
            bullet.flagupdate()
    
    def set(self):
        for bullet in self.bullets:
            self.availablepos.remove(bullet.setpos(self.availablepos))

    def remove(self):
        using=[]
        for bullet in self.bullets:
            if bullet.flag:
                using.append(bullet)
                self.availablepos.append(bullet.pos)
        self.bullets=using
    def blits(self):
        for bullet in self.bullets:
            bullet.gradual()
pygame.init()
baseW,baseH=1920,1080
baseSurface=pygame.Surface((baseW,baseH),SRCALPHA)

edgepos=[(660,400),(860,400),(1060,400),
         (660,600),(860,600),(1060,600),
         (660,800),(860,800),(1060,800)]
centerpos=[(760,500),(960,500),(1160,500),
           (760,700),(960,700),(1160,700),
           (760,900),(960,900),(1160,900)]

info = pygame.display.Info()
screenW,screenH=1280,720#info.current_w,info.current_h
screen=pygame.display.set_mode((screenW,screenH))


background= pygame.image.load("sky.png").convert_alpha()
background = pygame.transform.smoothscale(background, (baseW+300, baseH+300))

playerimg = fit_square("player.png",200)
sizegap=0

playerX=860
playerY=600
playerpos=(playerX,playerY)
playerXChange=0
playerYChange=0                               

LineY=400
LineX=660
gap=200

goalr=100
cradius=0
circleflag=True
clock=pygame.time.Clock()

running =True
bullet=AttackCircle()
Manager=bulletManager()
while running:
    dt=clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running =False
        
        if event.type==pygame.KEYDOWN:
            if event.key ==pygame.K_LEFT:
                playerXChange -=gap
            if event.key == pygame.K_RIGHT:
                playerXChange +=gap
            if event.key ==pygame.K_UP:
                playerYChange -=gap
            if event.key == pygame.K_DOWN:
                playerYChange += gap
    playerX += playerXChange
    if playerX <= 660:
        playerX = 660
    elif playerX >= 1060:
        playerX = 1060
    playerY+=playerYChange
    if playerY<=400:
        playerY=400
    elif playerY>=800:
        playerY=800
    
    
    baseSurface.blit(background,(0,0))
    grid=pygame.Surface((baseW,baseH),pygame.SRCALPHA)
    for i in range(4):
        pygame.draw.line(grid,(255,255,255,127),(LineX,LineY+gap*i),(LineX+gap*3,LineY+gap*i),width=5)
        pygame.draw.line(grid,(255,255,255,127),(LineX+gap*i,LineY),(LineX+gap*i,LineY+gap*3),width=5)
    
    Manager.makebullets()    
    Manager.set()
        
    


    Manager.blits()
    Manager.updates()

    baseSurface.blit(grid,(0,0))
    baseSurface.blit(playerimg,(playerX,playerY))

    scaledSurface=pygame.transform.smoothscale(baseSurface,(screenW,screenH))
    playerXChange=0
    playerYChange=0
    screen.blit(scaledSurface,(0,0))
    Manager.remove()
    pygame.display.flip()

pygame.quit()