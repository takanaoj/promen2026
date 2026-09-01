import pygame 
from pygame.locals import *
import random 
import os


pygame.init()
pygame.mixer.init()
pygame.display.set_caption("鶏を救え")
baseW,baseH=1920,1080
baseSurface=pygame.Surface((baseW,baseH),SRCALPHA)

info = pygame.display.Info()
infoW,infoH=info.current_w,info.current_h
screenratio=0.85#フルスクリーンでないときディスプレイより少し小さめの大きさに
aspectraio=16/9#想定しているアスペクト比
if infoW/infoH<aspectraio:
    screenW=int(infoW*screenratio)
    screenH=int(screenW/aspectraio)
    infoH=int(infoW/aspectraio)
else:
    screenH=int(infoH*screenratio)
    screenW=int(screenH*aspectraio)
    infoW=int(infoH*aspectraio)
screensize=(infoW,infoH)
screen=pygame.display.set_mode(screensize,FULLSCREEN) 
isfull=False
difficulty=1#0,1,2,3
totalpause=0
running = True
isbarrier=False
isfullscreen=False
gamestate='menu' #menu,pause,defense,finish,lost,win
countshot=0
counthit=0
counthurt=0
countbarrier=0
countbullet=0
score=0
gamelength=0
HorizonY=baseH//2+100
#マス目の座標
edgepos=[[(660,400),(860,400),(1060,400)],
         [(660,600),(860,600),(1060,600)],
         [(660,800),(860,800),(1060,800)]]
centerpos=[[(760,500),(960,500),(1160,500)],
           [(760,700),(960,700),(1160,700)],
           [(760,900),(960,900),(1160,900)]]
enemycenterpos=[[(893, 203), (960, 203), (1026, 203)],#baseSurfaceの座標での敵マスの中心座標
                [(893, 270), (960, 270), (1026, 270)], 
                [(893, 336), (960, 336), (1026, 336)]]
gridsize=(200,200)
circlecolor=[(255,0,0,127),(255,0,0,200)]
linecolor=(255,255,240,200)

LineY=400#一つ目の枠線のX座標
LineX=660#一つ目の枠線のy座標
gap=200#枠線の幅

font =pygame.font.SysFont("msgothic",50)
menumoji1=font.render("鶏を救え",True,(200,200,200,255))
menumoji1=pygame.transform.smoothscale(menumoji1,(menumoji1.get_width()*3,menumoji1.get_height()*3))
menumoji1_W,menumoji1_H=menumoji1.get_size()
menumoji2=font.render("press Space to start ,F to close",True,(200,200,200,255))
menumoji2_W,menumoji2_H=menumoji2.get_size()
posemoji=font.render("ポーズ中",True,(200,100,80,255))
posemoji_W,posemoji_H=posemoji.get_size()
finishmoji=font.render("Thanks for playing",True,(255,255,255,255))
finishmoji_W,finishmoji_H=finishmoji.get_size()
scorerabel=font.render('Score ',True,(255,255,255,255),(0,0,0,255))

pygame.mixer.music.load('assets/maou_game_battle03.mp3')
pygame.mixer.music.set_volume(0.2)

Soundeffect_player=pygame.mixer.Sound('assets/maou_se_battle_gun05.mp3')
Soundeffect_player.set_volume(0.4)
Soundeffect_win=pygame.mixer.Sound('assets/maou_se_jingle06.mp3')
Soundeffect_win.set_volume(0.4)
Soundeffect_lose=pygame.mixer.Sound('assets/maou_se_onepoint33.mp3')
Soundeffect_lose.set_volume(0.4)

def gametime(totalpause):
    return pygame.time.get_ticks()-totalpause

def setsquare(file):
    tmpimg=pygame.image.load(file)
    img_W,img_H=tmpimg.get_size()
    size=200
    minsize=max(img_W,img_H)
    scale=size/minsize
    
    setW=int(img_W*scale)
    setH=int(img_H*scale)

    img=pygame.transform.smoothscale(tmpimg,(setW,setH))

    canvas =pygame.Surface((size,size),pygame.SRCALPHA)
    canvas.fill((0,0,0,0))

    offsetX=(size-setW)//2
    offsetY=(size-setH)//2

    canvas.blit(img,(offsetX,offsetY))
    return canvas

class barrier:
    def __init__(self):
        self.radius=100
        self.color1=(200, 200, 255, 54)
        self.color2=(0, 0, 255, 255)
        self.DurationTick=1000#ミリ秒
        self.StartTime=None
        self.State='Ready'#Ready,Cooling,
    def keypushed(self,currenttime):
        if self.State=='Ready':
            self.StartTime=currenttime
            self.State='Using'
            return True
        else:
            return False
    def drawbarrier(self,barrierposition,currenttime):
        if self.State != 'Using':
            return
        if currenttime-self.StartTime<=self.DurationTick:
            pygame.draw.circle(grid,self.color1,barrierposition,self.radius-5)
            pygame.draw.circle(grid,self.color2,barrierposition,self.radius,width=5)
    def Readyupdate(self,currenttime):
        if self.State == 'Cooling':
                if currenttime-self.StartTime>self.DurationTick+500:
                    self.State='Ready'
        elif self.State =='Using':
            if currenttime-self.StartTime>self.DurationTick:
                self.State='Cooling'
    
            

class AttackCircle:
    GoalRadius=100
    def __init__(self,x,y):
        self.state="dead"#"dead","hold","spread"
        self.CurrentRadius=0
        self.SpeadingTime=round(random.uniform(2.0,4.0),2)#秒
        self.WaitTime=random.uniform(500,3000)#ミリ秒
        self.Position=centerpos[y][x]
        self.Y=y
        self.X=x
        
        self.HoldingTime=300#ミリ秒
        self.time=gametime(totalpause)
        self.HoldStart=None
        self.hittime=0
        self.distance=int(((self.Position[0]-enemycenterpos[1][1][0])**2+(self.Position[1]-enemycenterpos[1][1][1])**2)**0.5)
    def blit(self,currenttime):

        if self.state=="spread":
            deltatime=(currenttime-self.time)/1000
            self.CurrentRadius+=self.GoalRadius/self.SpeadingTime*deltatime
            if self.GoalRadius-self.CurrentRadius<0.5:
                self.CurrentRadius=self.GoalRadius
                self.state="hold"
                self.HoldStart=currenttime
            pygame.draw.circle(grid,circlecolor[0],self.Position,self.CurrentRadius)
            progress=max(0,self.CurrentRadius/self.GoalRadius)
            startx,starty=enemycenterpos[1][1]
            endx=self.Position[0]
            endy=self.Position[1]
            y=starty+progress*(endy-starty)
            x=startx+(endx-startx)*progress+500*progress*(progress-1)
            pygame.draw.circle(baseSurface,(255,0,0,int(100*progress)),(int(x),int(enemycenterpos[1][1][1]+progress*(self.Position[1]-enemycenterpos[1][1][1]))),int(75*progress))
            pygame.draw.circle(baseSurface,(255,255,255,int(100*progress)),(int(x),int(enemycenterpos[1][1][1]+progress*(self.Position[1]-enemycenterpos[1][1][1]))),int(50*progress))
            self.time=currenttime
        elif self.state=="hold":
            pygame.draw.circle(grid,circlecolor[1],self.Position,self.GoalRadius)
            if (currenttime-self.HoldStart)>self.HoldingTime:
                self.state="dead"
                self.time=currenttime
                self.CurrentRadius=0
                self.WaitTime=self.WaitTime2
        elif self.state=="dead":
            if currenttime-self.time>self.WaitTime:
                self.state="spread"
                self.time=currenttime
    def setstatus(self,difficulty):
        self.WaitTime2=random.uniform(200,max(500-(difficulty-1)*5,300))
        self.SpeadingTime=round(random.uniform(max(1.0,2.0-0.1*(difficulty-1),4.0),2))
        
                
    def isHit(self,playerX,playerY,currenttime):
        global countbarrier,counthurt, countbullet
        if playerX== self.X and playerY==self.Y and self.state=='hold':
            if currenttime-self.hittime>self.HoldingTime:
                if Barrier.State !='Using': 
                    self.hittime=currenttime
                    counthurt+=1
                    return True
                else: 
                    countbarrier+=1
                countbullet+=1
        return False
                      
class CircleManager:
    def __init__(self):
        self.bullets=[]
        self.MaxNumber=9
    def Make(self):
        self.bullets=[]
        for i in range(3):
            for j in range(3):
                self.bullets.append(AttackCircle(i,j))
    def blits(self,currenttime):
        for bullet in self.bullets:
             bullet.blit(currenttime)
             
    def isHits(self,playerX,playerY,currenttime):
        for bullet in self.bullets:
            if (bullet.isHit(playerX,playerY,currenttime)):
                return True
        return False
    def setstatus(self,difficulty):
        for bullet in self.bullets:
            bullet.setstatus(difficulty)
        
class Player:
    def __init__(self):
        self.maxHP=100
        self.HP=100
        self.X=1
        self.Y=1
        self.img=setsquare('assets/player.png')
        self.ColorBar1=(100,100,100,255)
        self.ColorBar2=[(100,255,100,255),(255,255,100,255),(255,100,100,255)]
        self.cursorcolor=(100,100,255,255)
        self.cursorX=1
        self.cursorY=1
        self.position=edgepos[self.X][self.Y]
        self.power=15
        self.level=1
        self.exp=0
    def HPdraw(self):
        if gamestate=='defense':
            if self.HP/self.maxHP>0.6:
                BarColor=self.ColorBar2[0]
            elif self.HP/self.maxHP>0.3:
                BarColor=self.ColorBar2[1]
            else:
                BarColor=self.ColorBar2[2]
            pygame.draw.rect(grid,self.ColorBar1,(0,0,500,70))
            pygame.draw.rect(grid,BarColor,(10,10,480*self.HP/self.maxHP,50))
    def display(self):
        self.position=edgepos[self.Y][self.X]
        baseSurface.blit(self.img,self.position)
    def levelup(self,difficulty):
        exp=difficulty*5
        self.exp+=exp
        if self.exp>=self.level*8:
            self.level+=1
            self.exp=self.exp-self.level*8
            self.power=(self.level-1)*2+15
            self.maxHP=100+self.level*2
class Playerattack:
    def __init__(self):
        self.pretime=gametime(totalpause)
        self.Colorshot=(200,255,0,255)
        self.position=list(centerpos[player.Y][player.X])
        self.preposition=self.position.copy()
        self.vector=None
        self.state='Ready'#Ready,shooting,holding
        self.speed=5
        self.destination=enemycenterpos[1][1]
        self.ishit=False
    def shot(self,currenttime):
        if self.state=='shooting':
            dt=(currenttime-self.pretime)/1000
            dx=int(self.vector[0]*dt*self.speed)
            dy=int(self.vector[1]*dt*self.speed)
            movedistance=(dx**2+dy**2)**0.5
            rest=(self.rest[0]**2+self.rest[1]**2)**0.5
            if movedistance>=rest:
                self.position=list(self.destination).copy()
            else:
                self.position[0]+=dx
                self.position[1]+=dy
            pygame.draw.line(baseSurface, (255,255,255,245), self.preposition, self.position, width=12)
            pygame.draw.line(baseSurface, self.Colorshot, self.preposition, self.position, width=10)
            
            self.preposition=self.position.copy()
            self.rest=[self.destination[0]-self.position[0],self.destination[1]-self.position[1]]            

            if abs(self.position[0]-self.destination[0])<10 and abs(self.position[1]-self.destination[1])<10:
                self.state='holding'
                self.holdstart=gametime(totalpause)
        elif self.state=='holding':
            color=list(self.Colorshot)
            color[3]-=75
            color=tuple(color)
            pygame.draw.circle(baseSurface,color,self.position,20)
            if (currenttime-self.holdstart)/1000>0.3:
                self.state='Ready'
                self.vector=None
    def start(self):
        global countshot
        if self.vector==None and self.state=='Ready':
            self.position = list(centerpos[player.Y][player.X])      
            self.preposition = self.position.copy() 
            ValueX=((enemycenterpos[player.cursorY][player.cursorX])[0]-self.position[0])
            ValueY=((enemycenterpos[player.cursorY][player.cursorX])[1]-self.position[1])
            distance=(ValueX**2+ValueY**2)**0.5
            self.speed=distance/50
            ValueX=ValueX/distance
            ValueY=ValueY/distance
            self.vector=[ValueX,ValueY]
            self.destination=enemycenterpos[player.cursorY][player.cursorX]
            self.state='shooting'
            self.holdstart=None
            self.rest=[self.destination[0]-self.position[0],self.destination[1]-self.position[1]]
            countshot+=1
            self.ishit=False
            

def read_savedata(difficulty,player):
    path ='save/save.txt'
    list1=[]
    try:
        with open(path,'r') as f:
            l=f.readlines()
            for tmpl in l:
                list=tmpl.rstrip().split(':')
                print(list)
                list1.append(list)
                for tmplist in list1:
                    if tmplist[0]=='difficulty':
                        difficulty.difficulty=int(tmplist[1])
                    elif tmplist[0]=='maxdifficulty':
                        difficulty.maxdifficulty=int(tmplist[1])
                    elif tmplist[0]=='playerlevel':
                        player.level=int(tmplist[1])
                    elif tmplist[0]=='playerexp':
                        player.exp=int(tmplist[1])
                    elif tmplist[0]=='playerpower':
                        player.power=int(tmplist[1])
    except FileNotFoundError:
        os.makedirs("save", exist_ok=True)
        pass
def save_savedata(difficulty,player):
    path ='save/save.txt'    
    with open(path,'w') as f:
        f.write(f"difficulty:{difficulty.difficulty}\nmaxdifficulty:{difficulty.maxdifficulty}\nplayerlevel:{player.level}\nplayerexp:{player.exp}\nplayerpower:{player.power}")
class Enemy:
    def __init__(self):
        self.img=setsquare('assets/enemy.png')
        self.maxHP=200
        self.X=1
        self.Y=1
        self.HP=200
        self.ColorBar1=(100,100,100,255)
        self.ColorBar2=[(100,255,100,255),(255,255,100,255),(255,100,100,255)]
        self.movedtime=None
        self.imgposition=[[(0,0)  ,(200,0)  ,(400,0)],
                          [(0,200),(200,200),(400,200)],
                          [(0,400),(200,400),(400,400)]]
        self.lineposition=[[(0,0),(0,200),(0,400),(0,600)],
                           [(200,0),(200,200),(200,400),(200,600)],
                           [(400,0),(400,200),(400,400),(400,600)],
                           [(600,0),(600,200),(600,400),(600,600)]]
        self.enemysurface=pygame.Surface((600,600),SRCALPHA)
        self.ColorBar1=(100,100,100,255)
        self.ColorBar2=[(100,255,100,255),(255,255,100,255),(255,100,100,255)]
        self.hittime=gametime(totalpause)
    def move(self,currenttime):
        if self.movedtime==None:
            if gametime(totalpause)>500:
                self.X=random.randint(0,2)
                self.Y=random.randint(0,2)
                self.movedtime=currenttime
        else:
            if (currenttime-self.movedtime)/1000>3:
                self.X=random.randint(0,2)
                self.Y=random.randint(0,2)
                self.movedtime=currenttime
    def blitenemy(self,currenttime):   
        self.enemysurface.fill((255,255,255,0))
        self.move(currenttime)
        enemysurface=self.enemysurface
        if gamestate=='defense':
            enemysurface.blit(self.img,self.imgposition[self.Y][self.X])
            for i in range(4):
                pygame.draw.line(enemysurface,linecolor,self.lineposition[i][0],(self.lineposition[i][3]),width=5)
                pygame.draw.line(enemysurface,linecolor,self.lineposition[0][i],self.lineposition[3][i],width=5)
        
        enemysurface=pygame.transform.smoothscale(enemysurface,(200,200))
        
        baseposition=(baseW//2-enemysurface.get_width()//2,170)
        baseSurface.blit(enemysurface,baseposition)

        if self.HP/self.maxHP>0.6:
            BarColor=self.ColorBar2[0]
        elif self.HP/self.maxHP>0.3:
            BarColor=self.ColorBar2[1]
        else:
            BarColor=self.ColorBar2[2]
        pygame.draw.rect(grid,self.ColorBar1,(baseW-70,0,70,300))
        pygame.draw.rect(grid,BarColor,(baseW-60,10,50,280*self.HP/self.maxHP))
        enemyHP=font.render(str(self.HP),True,(255,255,255,255),(0,0,0,255))
        enemyHP=pygame.transform.rotate(enemyHP,-90)
        grid.blit(enemyHP,(baseW-60,0))
    def ishit(self,currenttime,power):
        global counthit
        result=False
        if shot.state=='holding' and shot.ishit==False:
            dx=enemycenterpos[self.Y][self.X][0]-shot.position[0]
            dy=enemycenterpos[self.Y][self.X][1]-shot.position[1]
            distance=(dx**2+dy**2)**0.5
            if distance<20 and (currenttime-self.hittime)/1000>0.3:
                result= True
                self.hittime=currenttime
                self.HP=max(0,self.HP-power)
                counthit+=1
                shot.ishit=True
        return result
    def statusset(self,difficulty):
        self.maxHP=200+(int(difficulty)-1)*20
        self.power=int(20+(int(difficulty)-1)*0.4)
class Ground:
    def __init__(self):
        img1=pygame.image.load('assets/ground1.jpg')
        img2=pygame.image.load('assets/ground2.jpg')
        self.img1=pygame.transform.smoothscale(img1,(baseW,img1.get_height()*baseW/img1.get_width()))            
        self.img2=pygame.transform.smoothscale(img2,(baseW,img1.get_height()*baseW/img1.get_width()))
        
        tmpdisplay=pygame.Surface((self.img1.get_width()*2,self.img1.get_height()),SRCALPHA)
        tmpdisplay.blit(self.img1,(0,0))
        tmpdisplay.blit(self.img2,(self.img1.get_width(),0))
        self.img=tmpdisplay
        self.prevtime=gametime(totalpause)
        self.count=0
        self.position=[(0,HorizonY),(baseW//2,HorizonY)]
        rate=1
        self.subsurfacesize=(int(baseW//2*rate),int((baseH-HorizonY)*rate))
        self.realsize=(baseW//2,baseH-HorizonY)
        self.startX=0
        self.startY=self.img.get_height()-self.subsurfacesize[1]

        distance=(((self.img.get_width()-self.subsurfacesize[0])-self.startX)**2+(0-self.startY)**2)**0.5
        self.currentX=self.startX
        self.currentY=self.startY


        self.vectorX=((self.img.get_width()-self.subsurfacesize[0])-self.startX)/distance#左から右
        self.vectorY=(0-self.startY)/distance#下から上
    def display(self,currenttime):
        speed=30
        
        dt=(currenttime-self.prevtime)/1000
        self.currentX+=self.vectorX*dt*speed
        self.currentY+=self.vectorY*dt*speed
        subsurface1=self.img.subsurface(int(self.currentX),int(self.currentY),self.subsurfacesize[0],self.subsurfacesize[1])
        subsurface1=pygame.transform.smoothscale(subsurface1,self.realsize)
        subsurface2=pygame.transform.smoothscale(self.img.subsurface(int(self.img.get_width()-self.currentX-self.subsurfacesize[0]),int(self.currentY),self.subsurfacesize[0],self.subsurfacesize[1]),self.realsize)
        baseSurface.blit(subsurface1,self.position[0])
        baseSurface.blit(subsurface2,self.position[1])
        if abs(self.currentX-self.img.get_width())<10 and abs(self.currentY-self.img.get_height())<10:
            self.currentX=self.startX
            self.currentY=self.startY
        
        self.prevtime=currenttime
class Movingground:
    def __init__(self):
        self.img1=pygame.image.load('assets/ground1.jpg')
        self.img2=pygame.image.load('assets/ground2.jpg')
        self.width,self.height=self.img1.get_size()
        self.img=pygame.Surface((self.width,self.height*3),SRCALPHA)
        for i in range(3):
            if i%2==0:
                tmpimg=self.img1
            else:
                tmpimg=self.img2
            self.img.blit(tmpimg,(0,self.height*i))    
        self.pretime=gametime(totalpause)
        self.Y=self.height*2#開始位置
        self.GoalY=0#切り替え位置　ここまでself.Yが到達すれば開始位置に戻る
        self.GoalW=baseW-1000 #sufaceの上側の辺の長さ
        self.result=pygame.Surface((baseW,HorizonY),SRCALPHA)
        self.result.fill((0,0,0,0))
        
    def display(self,curenttime):
        self.result.fill((0,0,0,0))
        MAX_ROOP=200
        imgs=[]
        count=0
        totaldy=400
        ys=[]
        ys.append(self.Y)
        groundY=0#現時点までに作成した画像の合計高さ
        startW=baseW-1500
        startH=10
        GoalW=baseW
        katamuki=(GoalW-startW)/(HorizonY)
        GoalH=50
        
        while(groundY<baseH-HorizonY):
            progress = groundY / (baseH-HorizonY)
            progress = max(0, min(1, progress))
            progress = progress ** 2



            dy=10
            y=min(ys[count]+dy,totaldy+self.Y)
            ys.append(y)
            imgs.append(self.img.subsurface(0,ys[count],self.width,ys[count+1]-ys[count]))
            
            currentW=int(startW+katamuki*(groundY))
            currentH = int(startH + (GoalH - startH) * progress)
            imgs[count]=pygame.transform.smoothscale(imgs[count],(currentW,currentH))
            imgX,imgY=imgs[count].get_size()
            
            self.result.blit(imgs[count],(baseW//2-imgX//2,groundY))
            groundY+=imgY
            count+=1
            if count>=MAX_ROOP:
                break
            
        self.Y-=2
        if self.Y<0:
            self.Y=self.height*2
        baseSurface.blit(self.result,(0,HorizonY))

        
class Button:
    def __init__(self,moji,mojicolor,buttoncolor,center):
        self.moji=font.render(moji,True,mojicolor)
        self.sizeofmoji=list(self.moji.get_size())
        self.sizeofbutton=[self.sizeofmoji[0]+20,self.sizeofmoji[1]+20]
        self.buttoncolor=buttoncolor
        self.Surface=pygame.Surface((tuple(self.sizeofbutton)),SRCALPHA)
        listcenter=list(center)
        self.position=(listcenter[0]-self.sizeofbutton[0]//2,listcenter[1]-self.sizeofbutton[1]//2)
    def put(self):
        (self.Surface).fill(self.buttoncolor)
        (self.Surface).blit(self.moji,(10,10))
        baseSurface.blit(self.Surface,self.position)
    def ispushed(self,mouseX,mouseY):
        if mouseX>=self.position[0] and mouseX<self.position[0]+self.sizeofbutton[0]:
            if mouseY>=self.position[1] and mouseY<self.position[1]+self.sizeofbutton[1]:
                return True
        return False
    def set_center(self,newcenter):
        self.position=(newcenter[0]-self.sizeofbutton[0]//2,newcenter[1]-self.sizeofbutton[1]//2)
    
class Difficulty:
    def __init__(self):
        self.moji=font.render('難易度',True,(255,100,100,255))
        self.colorback=(170,170,170,255)
        self.buttonup=Button('▲',(255,255,255,255),(170,170,170,255),(baseW-100,50))
        self.buttondown=Button('▼',(255,255,255,255),(170,170,170,255),(baseH-50,50))
        self.difficulty=1#難易度
        self.maxdifficulty=1
        self.enemyattackwait=random.uniform(200,max(500-(self.difficulty-1)*5,300))
        self.enemyattackspreadtime=round(random.uniform(max(1.0,2.0-0.1*(difficulty-1),4.0),2))
        self.buttondown.set_center((baseW-self.buttondown.sizeofbutton[0]//2,self.buttondown.sizeofbutton[1]//2+20))
        self.buttonup.set_center((baseW-self.buttondown.sizeofbutton[0]-self.buttondown.sizeofbutton[0]//2,self.buttondown.sizeofbutton[1]//2+20))
        
    def button(self):
        self.moji=font.render('難易度　'+str(self.difficulty),True,(255,100,100,255),(255,255,255,255))
        self.buttonup.put()
        self.buttondown.put()
        baseSurface.blit(self.moji,(baseW-self.buttondown.sizeofbutton[0]-self.buttondown.sizeofbutton[0]-self.moji.get_width(),20))
    
    def setstatus(self):
        self.enemyattackwait=random.uniform(200,max(500-(self.difficulty-1)*5,300))
        self.enemyattackspreadtime=round(random.uniform(max(1.0,2.0-0.1*(difficulty-1),4.0),2))
    
    def ispushed(self,mouseX,mouseY):
        if mouseX>=self.buttondown.position[0] and mouseX<self.buttondown.position[0]+self.buttondown.sizeofbutton[0]:
            if mouseY>=self.buttondown.position[1] and mouseY<self.buttondown.position[1]+self.buttondown.sizeofbutton[1]:
                if self.difficulty>1:
                    self.difficulty-=1
        if mouseX>=self.buttonup.position[0] and mouseX<self.buttonup.position[0]+self.buttonup.sizeofbutton[0]:
            if mouseY>=self.buttonup.position[1] and mouseY<self.buttonup.position[1]+self.buttonup.sizeofbutton[1]:
                if self.difficulty<self.maxdifficulty:
                    self.difficulty+=1
class Menu:
    def __init__(self):
        niwatorimenu=setsquare('assets/animalhealth_niwatori_genki.png')
        niwatorimenu=pygame.transform.smoothscale(niwatorimenu,(niwatorimenu.get_width()*2,niwatorimenu.get_height()*2))
        self.menuscreen=pygame.Surface((baseW,baseH),SRCALPHA)
        self.menuscreen.fill((200,150,20,255))
        self.menuscreen.blit(niwatorimenu,(baseW-niwatorimenu.get_width(),baseH//2-niwatorimenu.get_height()//2))
        self.menuscreen.blit(menumoji1,(baseW//2-menumoji1_W//2,baseH//2-menumoji1_H//2))
        self.menuscreen.blit(menumoji2,(baseW//2-menumoji2_W//2,baseH//2+menumoji1_H//2))
        self.buttons=[]
        tmplist=[]
        tmplist.append(Button('Start(SPACE)',(255,255,255,255),(100,100,100,255),(int(baseW//2),int(baseH-200))))
        self.buttonstart=tmplist.copy()
        self.buttons.append(self.buttonstart)
        tmplist=[]
        tmplist.append(Button('Quit(F)',(255,255,255,255),(100,100,100,255),(int(baseW-150),int(baseH-100))))
        self.buttonquit=tmplist.copy()
        self.buttons.append(self.buttonquit)        
    def display(self,player,difficulty):
        statusstr=font.render('ステータス',True,(255,255,255,255))
        levelstr=font.render('レベル'+str(player.level),True,(255,255,255,255))
        powerstr=font.render('パワー'+str(player.power),True,(255,255,255,255))
        maxHPstr=font.render('最大HP'+str(player.maxHP),True,(255,255,255,255))
        maxdifstr=font.render('最大難易度'+str(difficulty.maxdifficulty),True,(255,255,255,255))
        statussurface=pygame.Surface((max(statusstr.get_width(),levelstr.get_width(),powerstr.get_width(),maxHPstr.get_width(),maxdifstr.get_width()),statusstr.get_height()+levelstr.get_height()+powerstr.get_height()+maxHPstr.get_height()+maxdifstr.get_height()))
        statussurface.fill((0,0,0,255))
        cY=0
        for moji in [statusstr,levelstr,powerstr,maxHPstr,maxdifstr]:
            statussurface.blit(moji,(0,cY))
            cY+=moji.get_height()
        self.menuscreen.blit(statussurface,(0,400))
        baseSurface.blit(self.menuscreen,(0,0))
        for list in self.buttons:
            list[0].put()
        difficulty.button()

              
    def ispusheds(self,mouseX,mouseY):
        global gamestate,Starttime,running,countshot,counthit,counthurt,countbarrier,countbullet
        if self.buttonstart[0].ispushed(mouseX,mouseY):
            gamestate='defense'
            Manager.Make()
            pygame.mixer.music.play(-1)
            Starttime=gametime(totalpause)
            countshot=0
            counthit=0
            counthurt=0
            countbarrier=0
            countbullet=0
        if self.buttonquit[0].ispushed(mouseX,mouseY):
            running=False
        
class Win:
    def __init__(self):
        pass
        self.screen=pygame.Surface((baseW,baseH),SRCALPHA)
        self.picture1=pygame.image.load('assets/food_egg_kago_white.png')
        self.picture2=pygame.image.load('assets/animalhealth_niwatori_genki.png')
        self.winmoji=font.render('You Win!!',True,(255,255,255,255),(255,255,0,255))
        self.winmoji=pygame.transform.scale2x(self.winmoji)
        self.buttons=[]
        tmplist=[]
        tmplist.append(Button('Menu(SPACE)',(255,255,255,255),(100,100,100,255),(int(baseW-400),int(baseH-100))))
        self.buttonmenu=tmplist.copy()
        self.buttons.append(self.buttonmenu)
        tmplist=[]
        tmplist.append(Button('Quit(F)',(255,255,255,255),(100,100,100,255),(int(baseW-150),int(baseH-100))))
        self.buttonquit=tmplist.copy()
        self.buttons.append(self.buttonquit)        
    def display(self):
        global gamelength,score
        self.screen.fill((255,200,200,255))
        self.screen.blit(self.winmoji,(int(baseW//2-self.winmoji.get_width()//2),0))
        self.screen.blit(self.picture1,(int(baseW//2-self.picture1.get_width()//2),int(baseH//2-self.picture1.get_height()//2)))
        self.screen.blit(self.picture2,(int(baseW//2+self.picture1.get_width()//2),int(baseH//2-self.picture2.get_height()//2)))
        gameleng=font.render('クリアタイム　'+str(gamelength/1000)+'秒',True,(60,40,20,255),(255,255,255,200))
        scoremoji=font.render('スコア　'+str(score),True,(60,40,10,255),(255,255,255,200))
        self.screen.blit(gameleng,(baseW//3,baseH//3-gameleng.get_height()//2))
        self.screen.blit(scoremoji,(baseW//3,baseH//3+gameleng.get_height()//2))        
        baseSurface.blit(self.screen,(0,0))
        for list in self.buttons:
            list[0].put()
    def ispusheds(self,mouseX,mouseY):
        global gamestate,Starttime,running,countshot,counthit,counthurt,countbarrier,countbullet
        if self.buttonmenu[0].ispushed(mouseX,mouseY):
            gamestate='menu'
        if self.buttonquit[0].ispushed(mouseX,mouseY):
            running=False
class Lost:
    def  __init__(self):
        self.screen=pygame.Surface((baseW,baseH),SRCALPHA)
        self.picture1=pygame.image.load('assets/food_shichimenchou.png')
        self.losemoji=font.render('You Lose',True,(0,0,0,255),(255,255,0,255))
        self.losemoji=pygame.transform.scale2x(self.losemoji)
        self.buttons=[]
        tmplist=[]
        tmplist.append(Button('Menu(SPACE)',(255,255,255,255),(100,100,100,255),(int(baseW-400),int(baseH-100))))
        self.buttonmenu=tmplist.copy()
        self.buttons.append(self.buttonmenu)
        tmplist=[]
        tmplist.append(Button('Quit(F)',(255,255,255,255),(100,100,100,255),(int(baseW-150),int(baseH-100))))
        self.buttonquit=tmplist.copy()
        self.buttons.append(self.buttonquit)  
    def display(self):
        global gamelength,score
        self.screen.fill((255,190,130,255))
        self.screen.blit(self.losemoji,(int(baseW//2-self.losemoji.get_width()//2),0))
        self.screen.blit(self.picture1,(int(baseW//2-self.picture1.get_width()//2),int(baseH//2-self.picture1.get_height()//2)))
        scoremoji=font.render('スコア　'+str(score),True,(60,40,10,255),(255,255,255,200))
        self.screen.blit(scoremoji,(baseW//3,baseH//3+scoremoji.get_height()//2))            
        baseSurface.blit(self.screen,(0,0))
        for list in self.buttons:
            list[0].put()    
    def ispusheds(self,mouseX,mouseY):
        global gamestate,Starttime,running,countshot,counthit,counthurt,countbarrier,countbullet
        if self.buttonmenu[0].ispushed(mouseX,mouseY):
            gamestate='menu'
        if self.buttonquit[0].ispushed(mouseX,mouseY):
            running=False
ground=Ground()
backmountain=pygame.image.load('assets/backgroundmountains.png')
scalemountain=baseW/backmountain.get_width()
backmountain=pygame.transform.smoothscale(backmountain,(baseW,200))

background=pygame.image.load("assets/sky.png").convert_alpha()
background=pygame.transform.smoothscale(background,(baseW+300,HorizonY))

maruyaki=setsquare('assets/food_shichimenchou.png')


scaledSurface=pygame.Surface((screenW,screenH),SRCALPHA)#実際に表示するsurface

lostscreen=pygame.Surface((baseW,baseH),SRCALPHA)
winscreen=pygame.Surface((baseW,baseH),SRCALPHA)




menu=Menu()
player=Player()
shot=Playerattack()
enemy=Enemy()
Manager=CircleManager()
Manager.Make()
Barrier=barrier()
clock=pygame.time.Clock()
moving=Movingground()
win=Win()
lost=Lost()
difficulty=Difficulty()
read_savedata(difficulty,player)
while running:
    clock.tick(60)
    currenttime=gametime(totalpause)
    for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running =False
            
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_F11:
                    if not isfull:
                        screensize=(infoW,infoH)
                        screen=pygame.display.set_mode((infoW,infoH),FULLSCREEN)
                        isfull=True
                    else:
                        screensize=(screenW,screenH)
                        screen=pygame.display.set_mode((screenW,screenH))
                        isfull=False
                if gamestate=='defense' or gamestate=="pause":
                    if event.key==pygame.K_ESCAPE:
                        if gamestate=="pause":
                            gamestate='defense'
                            pygame.mixer.music.unpause()
                            pausefinish = pygame.time.get_ticks()
                            totalpause += pausefinish-pausestart
                        else:
                            pausestart = pygame.time.get_ticks()
                            gamestate='pause'
                            pygame.mixer.music.pause()
                    if gamestate=='defense':
                            if event.key ==pygame.K_a:
                                player.X-=1
                            if event.key == pygame.K_d:
                                player.X +=1
                            if event.key ==pygame.K_w:
                                player.Y -=1
                            if event.key == pygame.K_s:
                                player.Y += 1  
                            if event.key ==pygame.K_LEFT:
                                player.cursorX-=1
                            if event.key == pygame.K_RIGHT:
                                player.cursorX +=1
                            if event.key ==pygame.K_UP:
                                player.cursorY -=1
                            if event.key == pygame.K_DOWN:
                                player.cursorY += 1  
                            if event.key ==pygame.K_e and Barrier.State=='Ready':
                                Barrier.keypushed(currenttime)
                            if event.key==pygame.K_SPACE and shot.state =='Ready':
                                shot.start()
                                Soundeffect_player.play()
                            
                            if player.X<0:
                                player.X=0
                            elif player.X>2:
                                player.X=2
                            if player.Y<0:
                                player.Y=0
                            elif player.Y>2:
                                player.Y=2
                            if player.cursorX<0:
                                player.cursorX=0
                            elif player.cursorX>2:
                                player.cursorX=2
                            if player.cursorY<0:
                                player.cursorY=0
                            elif player.cursorY>2:
                                player.cursorY=2
                    elif gamestate=='pause':
                        if event.key==pygame.K_m:
                            gamestate='menu'
                        if event.key==pygame.K_f:
                            gamestate='finish'

                         
                elif gamestate=="menu":
                    if event.key==pygame.K_SPACE:
                        gamestate="defense"
                        Manager.Make()
                        pygame.mixer.music.play(-1)
                        Starttime=gametime(totalpause)
                        countshot=0
                        counthit=0
                        counthurt=0
                        countbarrier=0
                        countbullet=0
                        player.HP=player.maxHP
                        enemy.HP=enemy.maxHP
                    if event.key==pygame.K_f:
                        running=False
                elif gamestate=="finish":
                    running=False

                elif gamestate=='lost':
                    if event.key==pygame.K_f:
                        gamestate='finish'
                    if event.key==pygame.K_SPACE:
                        gamestate='menu'
                elif gamestate=='win':
                    if event.key==pygame.K_f:
                        gamestate='finish'
                    if event.key==pygame.K_SPACE:
                        gamestate='menu'

            if event.type== pygame.MOUSEBUTTONDOWN:
                mouseX,mouseY=event.pos
                mouseX=int(mouseX*baseW/screensize[0])
                mouseY=int(mouseY*baseH/screensize[1])
                if gamestate=='menu':
                    menu.ispusheds(mouseX,mouseY)
                    difficulty.ispushed(mouseX,mouseY)
                elif gamestate=='lost':
                    lost.ispusheds(mouseX,mouseY)
                elif gamestate=='win':
                    win.ispusheds(mouseX,mouseY)
    
    grid=pygame.Surface((baseW,baseH),SRCALPHA)
    baseSurface.fill((0,0,0,0))
    if gamestate=="menu":
        menu.display(player,difficulty)
    elif gamestate=="defense":
        Manager.setstatus(difficulty.difficulty)
        enemy.statusset(difficulty.difficulty)
        
        ground.display(currenttime)
        moving.display(currenttime)
        baseSurface.blit(background,(0,0))
        baseSurface.blit(backmountain,(0,HorizonY-backmountain.get_height()//2-50))
        pygame.draw.rect(grid,(255,255,255,63),(LineX,LineY,600,600))
        Manager.blits(currenttime)
        
        #枠線表示
        for i in range(4):
            pygame.draw.line(grid,linecolor,(LineX,LineY+gap*i),(LineX+gap*3,LineY+gap*i),width=5)
            pygame.draw.line(grid,linecolor,(LineX+gap*i,LineY),(LineX+gap*i,LineY+gap*3),width=5)
        player.display()

        HitFlag=Manager.isHits(player.X,player.Y,currenttime)
        if HitFlag:
            player.HP = max(0, player.HP - enemy.power)
        barrierposition=centerpos[player.Y][player.X]
        Barrier.drawbarrier(barrierposition,currenttime)
        player.HPdraw()
        HPdisplay=str(int(player.HP))
        HPmoji=font.render(HPdisplay,True,(0,0,0,255))
        grid.blit(HPmoji,(10,10))
        powermoji=font.render('Power:'+str(player.power),True,(255,255,255,255),(0,0,0,255))
        grid.blit(powermoji,(0,170))
        enemy.blitenemy(currenttime)
        pygame.draw.circle(baseSurface,(255,10,10,200),enemycenterpos[player.cursorY][player.cursorX],15)
        shot.shot(currenttime)
        enemy.ishit(currenttime,player.power)
        baseSurface.blit(scorerabel,(0,100))
        Scoremoji=font.render(str(score),True,(255,255,255,255),(0,0,0,255))
        baseSurface.blit(Scoremoji,(scorerabel.get_width(),100))
        score=int(counthit*100+200*countbarrier)
    elif gamestate=="pause":
        baseSurface.fill((200,255,255,63))
        baseSurface.blit(posemoji,(baseW//2-posemoji_W//2,baseH//2-posemoji_H//2))
    elif gamestate=="finish":
        baseSurface.fill((20,0,0,255))
        baseSurface.blit(finishmoji,(baseW//2-finishmoji_W//2,baseH//2-finishmoji_H//2))
    elif gamestate=='win':
        win.display()
    elif gamestate=='lost':
        lost.display()
    baseSurface.blit(grid,(0,0))
    scaledSurface=pygame.transform.smoothscale(baseSurface,screensize)
    
    screen.blit(scaledSurface,(0,0))
    Barrier.Readyupdate(currenttime)
    

    if gamestate =='defense':
        if player.HP<=0:
            Endtime=gametime(totalpause)
            score+=counthit*100+countbarrier*200
            gamelength=Endtime-Starttime
            gamestate='lost'  
            pygame.mixer.music.pause()
            Soundeffect_lose.play()
        elif enemy.HP<=0:
            Endtime=gametime(totalpause)
            gamelength=Endtime-Starttime
            gamestate='win'
            pygame.mixer.music.pause()
            score += max(0, 100000 - gamelength+difficulty.difficulty*1000)
            player.levelup(difficulty.difficulty)
            if difficulty.difficulty>=difficulty.maxdifficulty:
                difficulty.maxdifficulty+=1
                difficulty.difficulty+=1
            Soundeffect_win.play()
        

    pygame.display.flip()
save_savedata(difficulty,player)
pygame.quit()