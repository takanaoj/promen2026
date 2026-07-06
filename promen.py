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
    def __init__(self,x,y):
        self.state="dead"
        self.goalr=100
        self.currentr=0
        self.indexs=[x,y]
        self.pos=centerpos[y][x]
        self.time=pygame.time.get_ticks()
        self.wait=random.uniform(500,5000)
        self.dt=self.time
        self.holdtime=300#ミリ秒
    def gradual(self,ct):
        if self.state=="dead":
            return
        elif self.state=="growing":
            dt=(ct-self.dt)/1000
            Growtime=15
            self.currentr=self.currentr+self.goalr/Growtime*dt
            self.dt=ct
            if self.currentr<self.goalr-0.5:
                pygame.draw.circle(grid,(200,10,10,64),self.pos,self.currentr)
            
        else :
            pygame.draw.circle(grid,(200,10,10,255),self.pos,self.currentr)
        
    
    def flagupdate(self,ct):
        if self.state=="growing":
            if self.currentr>self.goalr:
                self.state="holding"
                self.time=ct
                
        elif self.state=="dead" :
            if(ct-self.time)>self.wait:
                self.state="growing"
                self.dt=ct
        elif self.state=="holding":
            if (ct-self.time)>self.holdtime:
                self.currentr=0
                self.time=ct
                self.wait=random.uniform(100,2500)
                self.state="dead"
    
    def ishit(self,playerpos):
        if self.state=="holding":
            py,px=playerpos
            y=self.indexs[1]
            x=self.indexs[0]
            if px==x and py==y:
                return True
            else:
                return False
        else:
            return False

    
class bulletManager:
    def __init__(self):
        self.bullets=[]
    def makebullets(self):
        for x in range(3):
            for y in range(3):
                self.bullets.append(AttackCircle(x,y))

    def updates(self,ct):
        for bullet in self.bullets:
            bullet.flagupdate(ct)
    
    def blits(self,ct):
        for bullet in self.bullets:
            bullet.gradual(ct)
pygame.init()
baseW,baseH=1920,1080
baseSurface=pygame.Surface((baseW,baseH),SRCALPHA)

edgepos=[[(660,400),(860,400),(1060,400)],
         [(660,600),(860,600),(1060,600)],
         [(660,800),(860,800),(1060,800)]]
centerpos=[[(760,500),(960,500),(1160,500)],
           [(760,700),(960,700),(1160,700)],
           [(760,900),(960,900),(1160,900)]]

info = pygame.display.Info()
screenW,screenH=1280,720#info.current_w,info.current_h
screen=pygame.display.set_mode((screenW,screenH))


background= pygame.image.load("sky.png").convert_alpha()
background = pygame.transform.smoothscale(background, (baseW+300, baseH+300))

playerimg = fit_square("player.png",200)
sizegap=0

playerX=1
playerY=1

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
Manager=bulletManager()
Manager.makebullets()

while running:
    currenttime=pygame.time.get_ticks()
    clock.tick(60)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running =False
        
        if event.type==pygame.KEYDOWN:
            if event.key ==pygame.K_LEFT:
                playerX-=1
            if event.key == pygame.K_RIGHT:
                playerX +=1
            if event.key ==pygame.K_UP:
                playerY -=1
            if event.key == pygame.K_DOWN:
                playerY += gap
    
    if playerX <= 0:
        playerX = 0
    elif playerX >= 2:
        playerX = 2
    
    if playerY<=0:
        playerY=0
    elif playerY>=2:
        playerY=2
    
    playerpos=[playerY,playerX]
    
    
    baseSurface.blit(background,(0,0))
    grid=pygame.Surface((baseW,baseH),pygame.SRCALPHA)
    for i in range(4):
        pygame.draw.line(grid,(255,255,255,127),(LineX,LineY+gap*i),(LineX+gap*3,LineY+gap*i),width=5)
        pygame.draw.line(grid,(255,255,255,127),(LineX+gap*i,LineY),(LineX+gap*i,LineY+gap*3),width=5)
    
        
    


    Manager.blits(currenttime)
    Manager.updates(currenttime)

    baseSurface.blit(grid,(0,0))
    baseSurface.blit(playerimg,edgepos[playerY][playerX])

    scaledSurface=pygame.transform.smoothscale(baseSurface,(screenW,screenH))
    playerXChange=0
    playerYChange=0
    screen.blit(scaledSurface,(0,0))
    pygame.display.flip()

pygame.quit()