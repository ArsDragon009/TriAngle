import sys
import pygame
import math
from pygame.locals import *
from random import *
import shelve
import colorsys




_w = 1000
_h = 600
_fps = 70
_dev = False
clock = pygame.time.Clock()
particles = []
particles_E = True
screen = pygame.display.set_mode((_w, _h))
pygame.init()
pygame.display.set_caption("Triangle")
pygame.event.set_allowed([QUIT, KEYDOWN])

pygame.mouse.set_visible(False)

hpx, hpy = 25, 25
hpc = (255,255,255)
damaged = 0
cancollidehurt = 1
rgb_temp = 0.0

mode = "menu"

E_id = 1
ToGrid = 1

TriAngle = pygame.image.load("_data_/images/TriAngle.png")
TriAngleTrail = pygame.image.load("_data_/images/TriAngleTrail.png")

Cursor = pygame.image.load("_data_/images/Cursor.png")

Heal = pygame.image.load("_data_/images/Heal.png")

a_Dash = pygame.image.load("_data_/images/a_dash.png")
a_Slot = pygame.image.load("_data_/images/ability_slot.png")

l_mouse_click = pygame.image.load("_data_/images/l_mouse.png")

Enemy = pygame.image.load("_data_/images/Enemy.png")
EnemyTrail = pygame.image.load("_data_/images/EnemyTrail.png")

class Camera(object):
    def __init__(self,x,y,w,h):
        self.x, self.y, self.w, self.h, self.rect = x,y,w,h, pygame.Rect(x,y,w,h)
    def update(self):
        self.rect = pygame.Rect(self.x,self.y,self.w,self.h)

temp = 0
inMenu = False

blocks = []
hurt = []
enemies = []
drawenemies = []
drawblocks = []
drawhurt = []
drawpart = []
bgpart = []

def collide(blocks, rect):
    for b in blocks:
        if pygame.Rect.colliderect(b.rect, rect):
            return True
    return False

def text(text, x, y, size, col, autodraw = True):
    font = pygame.font.Font("_data_/font/slkscr.ttf", size)
    rendertext = font.render(text, True, col) 
    textRect = rendertext.get_rect()
    textRect.left, textRect.top = x, y 
    result = (rendertext, textRect)
    if autodraw: screen.blit(result[0], result[1])
    return result

class Player(object):
    def __init__(self, x, y, w, h, c, hp):
        self.x, self.y, self.w, self.h, self.c, self.hp, self.rect = x, y, w, h, c, hp, pygame.Rect(x,y,w,h)
        self.temp1, self.trail, self.speed = 0, pygame.Rect(x,y,w,h), 1
        self.temp2, self.trail2 = 0, pygame.Rect(x,y,w,h)
        self.temp3, self.dashed = 0, 0
        self.temp4, self.candash = 0, 0
        self.energy, self.maxenergy, self.temp5 = 100, 100, 0
        
        mx, my = pygame.mouse.get_pos()
        mx+=camera.x
        my+=camera.y
        self.a1, self.a2 = (math.atan2(mx-(self.x+10), my-(self.y+10))*57.2957795)+180, (math.atan2(mx-(self.x+10), my-(self.y+10))*57.2957795)+180
        self.r_u = pygame.Rect(x,y-6,w,3)
        self.r_d = pygame.Rect(x,y+h+3,w,3)
        self.r_l = pygame.Rect(x-6,y,3,h)
        self.r_r = pygame.Rect(x+w+3,y,3,h)
    def update(self):
        mx, my = pygame.mouse.get_pos()
        mx+=camera.x
        my+=camera.y
        if self.temp1 >= 2:
            self.temp1 = 0
            self.a1 = (math.atan2(mx-(self.x+10), my-(self.y+10))*57.2957795)+180
            self.trail = pygame.Rect(self.x, self.y, self.w, self.h)
        if self.temp2 >= 3:
            self.temp2 = 0
            self.a2 = (math.atan2(mx-(self.x+10), my-(self.y+10))*57.2957795)+180
            self.trail2 = pygame.Rect(self.x, self.y, self.w, self.h)
        if self.dashed:
            if self.temp3 >= 10:
                self.dashed = 0
                self.temp3 = 0
            mx, my = pygame.mouse.get_pos()
            mx+=camera.x
            my+=camera.y
            xx, yy = mx-(self.x+10), my-(self.y+10)
            if abs(xx) > 0 or abs(yy) > 0:
                dist = math.hypot(xx, yy)
                if not collide(blocks, pygame.Rect(self.x+min(dist, 12)*xx/dist, self.y+min(dist, 12)*yy/dist, 20, 20)):
                    self.x += min(dist, 12)*xx/dist
                    self.y += min(dist, 12)*yy/dist
            self.temp3+=1
        if not self.candash:
            if self.temp4 >= 25:
                self.candash = 1
                self.temp4 = 0
            self.temp4+=1
        if self.energy < 100:
            if self.temp5 >= 5:
                self.temp5 = 0
                self.energy += 1
            self.temp5 += 1
            

        self.r_u = pygame.Rect(self.x+4,self.y-2,self.w-8,1)
        self.r_d = pygame.Rect(self.x+4,self.y+self.h+1,self.w-8,1)
        self.r_l = pygame.Rect(self.x-2,self.y+4,1,self.h-8)
        self.r_r = pygame.Rect(self.x+self.w+1,self.y+4,1,self.h-8)
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.temp1+=1
        self.temp2+=1
        
    def draw(self):
        mx, my = pygame.mouse.get_pos()
        mx+=camera.x
        my+=camera.y
        angle = (math.atan2(mx-(self.x+10), my-(self.y+10))*57.2957795)+180
        t1 = pygame.transform.rotate(TriAngle,angle)
        t2 = pygame.transform.rotate(TriAngleTrail,self.a1)
        t3 = pygame.transform.rotate(TriAngleTrail,self.a2)
        # if _dev: pygame.draw.rect(screen, (123,123,255,100), pygame.Rect(self.x-camera.x, self.y-camera.y, self.w, self.h))
        screen.blit(t3,t2.get_rect(center=((self.trail2.x+10)-camera.x,(self.trail2.y+10)-camera.y)))
        screen.blit(t2,t2.get_rect(center=((self.trail.x+10)-camera.x,(self.trail.y+10)-camera.y)))
        screen.blit(t1,t1.get_rect(center=((self.x+10)-camera.x,(self.y+10)-camera.y)))
        pygame.draw.rect(screen, (123,123,255), (27, 50, 100*(self.energy/self.maxenergy), 10))
        pygame.draw.rect(screen, (255,255,255), (27, 50, 100, 10), 2)
    def move(self, move):
        if move == "l": 
            if not collide(blocks, self.r_l): self.x-=self.speed
        elif move == "r": 
            if not collide(blocks, self.r_r): self.x+=self.speed
        elif move == "u": 
            if not collide(blocks, self.r_u): self.y-=self.speed
        elif move == "d": 
            if not collide(blocks, self.r_d): self.y+=self.speed
    def damage(self, dmg: int):
        global damaged, cancollidehurt, particles
        damaged = 1
        cancollidehurt = 0
        self.hp-=dmg
        for i in range(10):
            s = randint(1,3)
            particles.append(MoveParticle(self.x+(10-s), self.y+(10-s), s, s, (255,255,255), randint(-3, 3), randint(-3, 3), randint(20, 40)))
    def dash(self):
        if self.candash and self.energy >= 20:
            self.dashed = 1
            self.candash = 0
            self.energy -= 20


class Enemy_(object):
    def __init__(self, x, y, w, h, c, hp, dirx, diry):
        self.x, self.y, self.w, self.h, self.c, self.hp, self.rect = x, y, w, h, c, hp, pygame.Rect(x,y,w,h)
        self.temp1, self.trail, self.speed = 0, pygame.Rect(x,y,w,h), 3
        self.temp2, self.trail2 = 0, pygame.Rect(x,y,w,h)
        self.r_u = pygame.Rect(x,y-6,w,3)
        self.r_d = pygame.Rect(x,y+h+3,w,3)
        self.r_l = pygame.Rect(x-6,y,3,h)
        self.r_r = pygame.Rect(x+w+3,y,3,h)
        self.temp3, self.collide = 0, True
        self.dirx, self.diry = dirx, diry
    def update(self):
        if self.temp1 >= 2:
            self.temp1 = 0
            self.trail = pygame.Rect(self.x, self.y, self.w, self.h)
        if self.temp2 >= 3:
            self.temp2 = 0
            self.trail2 = pygame.Rect(self.x, self.y, self.w, self.h)
        self.r_u = pygame.Rect(self.x+4,self.y-2,self.w-8,1)
        self.r_d = pygame.Rect(self.x+4,self.y+self.h+1,self.w-8,1)
        self.r_l = pygame.Rect(self.x-2,self.y+4,1,self.h-8)
        self.r_r = pygame.Rect(self.x+self.w+1,self.y+4,1,self.h-8)
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h) 
        self.temp1+=1
        self.temp2+=1
        self.move()
    def draw(self):
        t1r = Enemy.get_rect(center=((self.x+10)-camera.x,(self.y+10)-camera.y))
        t2r = EnemyTrail.get_rect(center=((self.trail.x+10)-camera.x,(self.trail.y+10)-camera.y))
        t3r = EnemyTrail.get_rect(center=((self.trail2.x+10)-camera.x,(self.trail2.y+10)-camera.y))
        screen.blit(Enemy,t1r)
        screen.blit(EnemyTrail,t2r)
        screen.blit(EnemyTrail,t3r)

        
    def move(self):
        if self.dirx != 0:
            if self.dirx == 1: # left
                if collide(blocks, self.r_l): 
                    self.dirx = 2 # right
                    for i in range(5):
                        s = randint(1,3)
                        particles.append(MoveParticle(self.x+(10-s), self.y+(10-s), s, s, (255,123,123), randint(-2, 2), randint(-2, 2), randint(20, 40)))
            if self.dirx == 2: # right
                if collide(blocks, self.r_r): 
                    self.dirx = 1 # left
                    for i in range(5):
                        s = randint(1,3)
                        particles.append(MoveParticle(self.x+(10-s), self.y+(10-s), s, s, (255,123,123), randint(-2, 2), randint(-2, 2), randint(20, 40)))
            if self.dirx == 1: 
                self.x -= self.speed # left
            if self.dirx == 2: 
                self.x += self.speed # right
        if self.diry != 0:
            if self.diry == 1: #up
                if collide(blocks, self.r_u): 
                    self.diry = 2 # down
                    for i in range(5):
                        s = randint(1,3)
                        particles.append(MoveParticle(self.x+(10-s), self.y+(10-s), s, s, (255,123,123), randint(-2, 2), randint(-2, 2), randint(20, 40)))
            if self.diry == 2: #down
                if collide(blocks, self.r_d): 
                    self.diry = 1 # up
                    for i in range(5):
                        s = randint(1,3)
                        particles.append(MoveParticle(self.x+(10-s), self.y+(10-s), s, s, (255,123,123), randint(-2, 2), randint(-2, 2), randint(20, 40)))
            if self.diry == 1: 
                self.y -= self.speed #up
            if self.diry == 2: 
                self.y += self.speed #down


class Heal_(object):
    def __init__(self, x, y, w, h, heal):
        self.x, self.y, self.w, self.h, self.heal_a, self.rect = x, y, w, h, heal, pygame.Rect(x,y,w,h)
        self.temp = 0
        self.mode = 1
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.temp += 1
        if self.temp >= 10:
            s = randint(1,3)
            particles.append(MoveParticle(self.x+(10-s), self.y+(10-s), s, s, (123,255,123), randint(-2, 2), randint(-2, 2), randint(20, 40)))
            self.temp = 0
    def draw(self):
        screen.blit(Heal, Heal.get_rect(center=((self.x+10)-camera.x,(self.y+10)-camera.y)))
    def heal(self):
        p.hp+=self.heal_a
        self.mode = 0
        for i in range(20):
            s = randint(1,3)
            particles.append(MoveParticle(self.x+(10-s), self.y+(10-s), s, s, (123,255,123), randint(-2, 2), randint(-2, 2), randint(20, 40)))
class Particle(object):
    def __init__(self, x, y, w, h, c):
        self.x, self.y, self.w, self.h, self.c, self.rect = x, y, w, h, c, pygame.Rect(x,y,w,h)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
    def draw(self):
        pygame.draw.rect(screen, self.c, pygame.Rect(self.x-camera.x, self.y-camera.y, self.w, self.h))

class MoveParticle(object):
    def __init__(self, x, y, w, h, c, mx, my, lt, collide_ = True):
        self.x, self.y, self.w, self.h, self.c, self.mx, self.my, self.ltm, self.lt, self.collide_, self.rect = x, y, w, h, c, mx, my, lt, 0, collide_, pygame.Rect(x,y,w,h)
        self.r_u = pygame.Rect(self.x+4,self.y-2,self.w-8,1)
        self.r_d = pygame.Rect(self.x+4,self.y+self.h+1,self.w-8,1)
        self.r_l = pygame.Rect(self.x-2,self.y+4,1,self.h-8)
        self.r_r = pygame.Rect(self.x+self.w+1,self.y+4,1,self.h-8)
    def update(self):
        self.x += self.mx
        self.y += self.my
        if self.collide_:
            if collide(blocks, self.r_l) and self.mx < 0:
                self.mx = -self.mx/2
            if collide(blocks, self.r_r) and self.mx > 0:
                self.mx = -self.mx/2
            if collide(blocks, self.r_u) and self.my < 0:
                self.my = -self.my/2
            if collide(blocks, self.r_d) and self.my > 0:
                self.my = -self.my/2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.r_u = pygame.Rect(self.x+4,self.y-2,self.w-8,1)
        self.r_d = pygame.Rect(self.x+4,self.y+self.h+1,self.w-8,1)
        self.r_l = pygame.Rect(self.x-2,self.y+4,1,self.h-8)
        self.r_r = pygame.Rect(self.x+self.w+1,self.y+4,1,self.h-8)
        self.lt+=1
    def draw(self):
        pygame.draw.rect(screen, self.c, pygame.Rect(self.x-camera.x, self.y-camera.y, self.w, self.h))

class BGMoveParticle(object):
    def __init__(self, x, y, c, s, mx, my, lt, r):
        self.x, self.y,  self.c, self.s, self.mx, self.my, self.ltm, self.lt, self.r, self.rect = x, y, c, s, mx, my, lt, r, 0, pygame.Rect(x,y,s,s)
    def update(self):
        self.x += self.mx
        self.y += self.my
        self.rect = pygame.Rect(self.x, self.y, self.s, self.s)
        self.lt+=1
        self.r = (self.r + 2) % 360  
    def draw(self):
        image_orig = pygame.Surface((self.s, self.s))  
        image_orig.set_colorkey((0 , 0 , 0))  
        image_orig.fill(self.c)  
        image = image_orig.copy()  
        image.set_colorkey((0 , 0 , 0))   
        rect = image.get_rect()  
        rect.center = self.rect.center
        old_center = rect.center 
        new_image = pygame.transform.rotate(image_orig , self.r)  
        rect = new_image.get_rect()  
        rect.center = old_center
        screen.blit(new_image, rect)  

class Block(object):
    def __init__(self, x, y, w, h, c):
        self.x, self.y, self.w, self.h, self.c, self.rect = x, y, w, h, c, pygame.Rect(x,y,w,h)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
    def draw(self):
        pygame.draw.rect(screen, self.c, pygame.Rect(self.x-camera.x, self.y-camera.y, self.w, self.h))

class Button(object):
    def __init__(self, x, y, s, c, scr):
        self.x, self.y, self.s, self.c, self.scr, = x, y, s, c, scr
        self.tt = text(s, self.x, self.y, 30, c, False)
        self.rect = self.tt[1]
    def draw(self):
        screen.blit(self.tt[0], self.tt[1])
    def script(self):
        global mode
        if self.scr == "play": mode = "play"
        if self.scr == "editor": mode = "editor"
        elif self.scr == "exit":
            pygame.quit()
            sys.exit()


        

# 0: {"text": "", "script": ""}
buttons = {
    0: {
        0: {"text": "Continue", "script": "menu_", "color": (255,255,255)},
        1: {"text": "Save", "script": "save_", "color": (255,255,0)},
        2: {"text": "Exit", "script": "exit_", "color": (255,255,255)},
        3: {"text": "???????", "script": "_dev", "color": (-1,-1,-1)},
        4: {"text": "Reset map", "script": "gen_", "color": (255,255,255)}
    }
}

b_s = 0
b_i = 0
playBtn = Button(100, 100, "Play", (255,255,255), "play")
exitBtn = Button(100, 150, "Editor", (255,255,255), "editor")
editorBtn = Button(100, 200, "Exit", (255,255,255), "exit")
temp = 0
temp1 = 0
temp2 = 0
temp3 = 0

camera = Camera(40, 240,_w,_h)
p = Player((40*13)+20, (40*13)+20, 20, 20, (123,123,255), 100)

with shelve.open("_data_/save/savegame") as f:
    try:
        _dev = f["_dev"]
        p.hp = f["hp"]
        p.x = f["x"]
        p.y = f["y"]
        camera.x = f["cx"]
        camera.y = f["cy"]
        enemies = f["enemies"]
        blocks = f["blocks"]
        hurt = f["hurt"]
        particles_E = f["particles_E"]
    except: pass

while 1:
    screen.fill((0, 0, 0, 255))
    if mode == "play":
        if inMenu:
            if temp >= 30:
                xx, yy = p.x-(camera.x+_w/2), p.y-(camera.y+_h/2)
                if abs(xx) > 0 or abs(yy) > 0:
                    dist = math.hypot(xx, yy)
                    camera.x += min(dist, 5)*xx/dist
                    camera.y += min(dist, 5)*yy/dist
                camera.update()
        else:
            xx, yy = p.x-(camera.x+_w/2), p.y-(camera.y+_h/2)
            if abs(xx) > 0 or abs(yy) > 0:
                dist = math.hypot(xx, yy)
                camera.x += min(dist, 5)*xx/dist
                camera.y += min(dist, 5)*yy/dist
        camera.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB and _dev: p.damage(1)
                if event.key == pygame.K_LSHIFT and _dev: p.damage(-1)
                if event.key == pygame.K_ESCAPE: inMenu = not inMenu
                if event.key == pygame.K_e: particles_E = not particles_E
                if event.key == pygame.K_w and inMenu:
                    b_i-=1
                    if b_i < 0:
                        b_i = len(buttons[b_s])-1
                if event.key == pygame.K_s and inMenu:
                    b_i+=1
                    if b_i > len(buttons[b_s])-1:
                        b_i = 0
                if event.key == pygame.K_RETURN and inMenu:
                    if buttons[b_s][b_i]["script"] == "menu_": inMenu = not inMenu
                    if buttons[b_s][b_i]["script"] == "_dev": 
                        if not _dev: _dev = True
                    elif buttons[b_s][b_i]["script"] == "exit_":
                        mode = "menu"
                    elif buttons[b_s][b_i]["script"] == "save_":
                        with shelve.open("_data_/save/savegame") as f:
                            f["_dev"] = _dev
                            f["hp"] = p.hp
                            f["x"] = p.x
                            f["y"] = p.y
                            f["cx"] = camera.x
                            f["cy"] = camera.y
                            f["enemies"] = enemies
                            f["blocks"] = blocks
                            f["hurt"] = hurt
                            f["particles_E"] = particles_E
                    elif buttons[b_s][b_i]["script"] == "gen_":
                        p.x, p.y = (40*13)+20, (40*13)+20
                        camera.x, camera.y = 40, 240
                        p.hp = 10
                        blocks = []
                        hurt = []
                        enemies = []
                        particles = []
                        for j in range(30):
                            for i in range(30):
                                if (i < 12 or i > 15) or (j < 12 or j > 15):
                                    r = randint(1,7)
                                    if r == 1: blocks.append(Block(i*40,j*40,40,40,(255,255,255,255)))
                                    elif r == 2: hurt.append(Block(i*40,j*40,40,40,(255,0,0,255)))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                p.dash()
        drawenemies = []
        drawblocks = []
        drawhurt = []
        drawpart = []
        for b in blocks:
            if pygame.Rect.colliderect(b.rect, camera.rect):
                drawblocks.append(b)
        for h in hurt:
            if pygame.Rect.colliderect(h.rect, camera.rect):
                drawhurt.append(h)
        for pa in particles:
            if pygame.Rect.colliderect(pa.rect, camera.rect):
                drawpart.append(pa)
        for e in enemies:
            if pygame.Rect.colliderect(e.rect, camera.rect):
                drawenemies.append(e)
        if inMenu:
            if temp >= 30:
                for e in enemies:
                    e.update()
        else:
            for e in enemies:
                e.update()
        pressed = pygame.key.get_pressed()
        if not inMenu:
            if pressed[pygame.K_a]:
                p.move("l")
            if pressed[pygame.K_d]:
                p.move("r")
            if pressed[pygame.K_w]:
                p.move("u")
            if pressed[pygame.K_s]:
                p.move("d")
        for b in drawblocks:
            b.draw()
        for h in drawhurt:
            h.draw()
        if particles_E:
            for pa in drawpart:
                pa.draw()
        for e in drawenemies:
            e.draw()
        p.draw()
        if inMenu:
            if temp >= 30:
                p.update()
                if cancollidehurt:
                    if collide(drawhurt, p.rect): p.damage(1)
                    elif collide(drawenemies, p.rect): p.damage(1)
                if not cancollidehurt:
                    temp2+=1
                    if temp2 >= 40:
                        cancollidehurt = 1
                        temp2=0
        else:
            p.update()
            if cancollidehurt:
                if collide(drawhurt, p.rect): p.damage(1)
                elif collide(drawenemies, p.rect): p.damage(1)
            if not cancollidehurt:
                temp2+=1
                if temp2 >= 40:
                    cancollidehurt = 1
                    temp2=0
        if damaged:
            hpx, hpy = randint(20,30), randint(20,30)
            if hpc != (255,0,0): hpc = (255,0,0)
            if p.c != (255,0,0): p.c = (255,0,0)
            temp1+=1
            if temp1 >= 10:
                temp1, damaged = 0, 0
        else:
            if hpx != 25: hpx = 25
            if hpy != 25: hpy = 25
            if hpc != (255,255,255): hpc = (255,255,255)
            if p.c != (123,123,255): p.c = (123,123,255)
        text(f"HP: {p.hp}", hpx, hpy, 25, hpc)
        if inMenu:
            if temp >= 30:
                for pa in particles:
                    pa.update()
                    if pa.lt >= pa.ltm: particles.remove(pa)
        else:
            for pa in particles:
                pa.update()
                if pa.lt >= pa.ltm: particles.remove(pa)
        if p.hp <= 0:
            p.x, p.y = (40*13)+20, (40*13)+20
            camera.x, camera.y = 40, 240
            p.hp = 10
            blocks = []
            hurt = []
            enemies = []
            particles = []
            for j in range(30):
                for i in range(30):
                    if (i < 12 or i > 15) or (j < 12 or j > 15):
                        r = randint(1,7)
                        if r == 1: blocks.append(Block(i*40,j*40,40,40,(255,255,255,255)))
                        elif r == 2: hurt.append(Block(i*40,j*40,40,40,(255,0,0,255)))
        screen.blit(a_Slot, (100, 500))
        screen.blit(a_Dash, (104, 504))
        screen.blit(l_mouse_click, (126, 477))
        if inMenu:
            s = pygame.Surface((1000,600))
            s.set_alpha(128)
            s.fill((0,0,0))
            screen.blit(s, (0,0))
            for i in range(len(buttons[b_s])):
                if i == b_i: color = (123,255,123)
                else: color = (255,255,255)
                if buttons[b_s][i]["color"] != (-1,-1,-1):
                    text(buttons[b_s][i]["text"], 50, (i*50)+50, 25, color)
                else:
                    for i2, letter in zip(range(len(buttons[b_s][i]["text"])), buttons[b_s][i]["text"]):
                        color = (randint(0,255),randint(0,255),randint(0,255))
                        text(letter, 50+(i2*18), (i*50)+50, 25, color)
        if temp >= 30:
            temp = 0
        temp += 1
    elif mode == "editor":
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: inMenu = not inMenu
                if event.key == pygame.K_e: particles_E = not particles_E
                if event.key == pygame.K_w and inMenu:
                    b_i-=1
                    if b_i < 0:
                        b_i = len(buttons[b_s])-1
                elif event.key == pygame.K_g and not inMenu: ToGrid = not ToGrid
                if event.key == pygame.K_s and inMenu:
                    b_i+=1
                    if b_i > len(buttons[b_s])-1:
                        b_i = 0
                if event.key == pygame.K_e and not inMenu: E_id = {1: 2, 2: 1}[E_id]
                if event.key == pygame.K_RETURN and inMenu:
                    if buttons[b_s][b_i]["script"] == "menu_": inMenu = not inMenu
                    if buttons[b_s][b_i]["script"] == "_dev": 
                        if not _dev: _dev = True
                    elif buttons[b_s][b_i]["script"] == "exit_":
                        mode = "menu"
                    elif buttons[b_s][b_i]["script"] == "save_":
                        pass
                        # with shelve.open("_data_/save/savegame") as f:
                        #     f["_dev"] = _dev
                        #     f["hp"] = p.hp
                        #     f["x"] = p.x
                        #     f["y"] = p.y
                        #     f["cx"] = camera.x
                        #     f["cy"] = camera.y
                        #     f["enemies"] = enemies
                        #     f["blocks"] = blocks
                        #     f["hurt"] = hurt
                            # f["particles_E"] = particles_E
                    elif buttons[b_s][b_i]["script"] == "gen_":
                        blocks, hurt = [], []
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if my > 105:
                    g1, g2 = 1, 1
                    k, l = mx+camera.x, my+camera.y
                    if ToGrid:
                        tt = int(k)
                        tstr = str(tt)
                        while tstr[-1] != "0":
                            tt-=1
                            tstr = str(tt)
                        k = tt

                        tt = int(l)
                        tstr = str(tt)
                        while tstr[-1] != "0":
                            tt-=1
                            tstr = str(tt)
                        l = tt
                    if E_id == 1: 
                        for i in blocks:
                            if (i.x, i.y) == (k, l):
                                g1 = 0
                        if g1: blocks.append(Block(k, l, 40, 40, (255,255,255)))
                    if E_id == 2:
                        for i in hurt:
                            if (i.x, i.y) == (k, l):
                                g2 = 0 
                        if g2: hurt.append(Block(k, l, 40, 40, (255,0,0)))
        for b in blocks:
            if pygame.Rect.colliderect(b.rect, camera.rect):
                b.draw()
            b.update()
        for h in hurt:
            if pygame.Rect.colliderect(h.rect, camera.rect):
                h.draw()
            h.update()
            

        if particles_E:
            for pa in drawpart:
                pa.draw()
        for e in drawenemies:
            e.draw()

        pressed = pygame.key.get_pressed()
        if not inMenu:
            if pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]: t = 1
            else: t = 0
            if pressed[pygame.K_a]: camera.x-=3+(5*t)
            if pressed[pygame.K_d]: camera.x+=3+(5*t)
            if pressed[pygame.K_w]: camera.y-=3+(5*t)
            if pressed[pygame.K_s]: camera.y+=3+(5*t)
            if pressed[pygame.K_q]:
                mx, my = pygame.mouse.get_pos()
                mx, my = mx+camera.x, my+camera.y
                for i in blocks:
                    try:
                        if i.rect.collidepoint(mx, my): blocks.remove(i)
                    except: pass
                for i in hurt:
                    try:
                        if i.rect.collidepoint(mx, my): hurt.remove(i)
                    except: pass
        

        # if ToGrid:
        #     k, l = pygame.mouse.get_pos()
        #     if l > 105:
        #         tt = int(k)
        #         tstr = str(tt)
        #         while tstr[-1] != "0" or tstr[-2] not in ["0", "4", "8"]:
        #             tt-=1
        #             tstr = str(tt)
        #         k = tt

        #         tt = int(l)
        #         tstr = str(tt)
        #         while tstr[-1] != "0" or tstr[-2] not in ["0", "4", "8"]:
        #             tt-=1
        #             tstr = str(tt)
        #         l = tt
        #         pygame.draw.rect(screen, (123,123,255), pygame.Rect(k, l, 40, 40), 1)

        pygame.draw.rect(screen, (205,205,205), pygame.Rect(0, 0, _w, 100), 4)
        pygame.draw.rect(screen, {1: (255,255,255), 2: (255,0,0)}[E_id], pygame.Rect(20, 20, 40, 40))
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(20, 20, 40, 40), 1)
        text(f"G: To Grid <{str(bool(ToGrid))}>", 100, 20, 20, (44, 44, 255))
        text(f"Q: Remove on cursor ", 100, 50, 20, (44, 44, 255))
        text(f"E", 40, 20, 30, (44, 44, 255))
                


                

        

        if inMenu:
            s = pygame.Surface((1000,600))
            s.set_alpha(128)
            s.fill((0,0,0))
            screen.blit(s, (0,0))
            for i in range(len(buttons[b_s])):
                if i == b_i: color = (123,255,123)
                else: color = (255,255,255)
                if buttons[b_s][i]["color"] != (-1,-1,-1):
                    text(buttons[b_s][i]["text"], 50, (i*50)+50, 25, color)
                else:
                    for i2, letter in zip(range(len(buttons[b_s][i]["text"])), buttons[b_s][i]["text"]):
                        color = (randint(0,255),randint(0,255),randint(0,255))
                        text(letter, 50+(i2*18), (i*50)+50, 25, color)
        camera.update()
    elif mode == "menu":
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect.colliderect(pygame.Rect(pygame.mouse.get_pos(), (2, 2)), playBtn.rect): playBtn.script()
                if pygame.Rect.colliderect(pygame.Rect(pygame.mouse.get_pos(), (2, 2)), exitBtn.rect): exitBtn.script()
        playBtn.draw()
        editorBtn.draw()
        exitBtn.draw()
        for bp in bgpart:
            bp.update()
            bp.draw()
            if bp.y >= 700: bgpart.remove(bp)
        temp3+=1
        if temp3 >= 50:
            s = randint(5, 15)
            rand = randint(1, 300)
            if rand >= 100 and rand <= 120: c = (255,0,0)
            elif rand >= 200 and rand <= 203: c = (0,255,0)
            elif rand == 300: c = (123,123,255)
            else: c = (255,255,255)
            bgpart.append(BGMoveParticle(randint(1, 1000), -100, c, s, 0, 2, randint(0, 360), 1000))
            temp3=0
    if _dev:
        (r, g, b) = colorsys.hsv_to_rgb(rgb_temp, 1.0, 1.0)
        R, G, B = int(255 * r), int(255 * g), int(255 * b)
        text(".", 975, -10, 50, (R,G,B))
        rgb_temp += 0.005
    
    screen.blit(Cursor, Cursor.get_rect(topleft = pygame.mouse.get_pos()))
    pygame.display.flip()
    clock.tick(_fps)
