# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 15:19:36 2016

@author: choid
"""




import pygame
import random
from time import sleep

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

pad_width = 512
pad_height = 256
background_width = 256

aircraft_width = 30
aircraft_height = 36

enemy_width = 75
enemy_height = 38

missile_width = 116
missile_height = 14

aircraft_speed = 10
enemy_speed = 15
missile_speed = 25 
bullet_speed = 30
background_speed = 4
frame_rate = 15

FIRE_REWARD = 0  # when the UAV fires a bullet
CRASH_REWARD = -1  # when the UAV crashes an enemy or a missile
PASS_REWARD = -1  # when an enemy passed the UAV
HIT_REWARD = 1  # when a bullet hits an enemy


def drawScore(count):
    global gamepad
    
    font = pygame.font.SysFont(None, 25)
    text = font.render(str(count), True, BLUE)
    gamepad.blit(text, (0, 0))
    
def gameOver():
    global gamepad
    dispMessage('Game Over')

def textObj(text, font):
    textSurface = font.render(text, True, RED)
    return textSurface, textSurface.get_rect()
    
def dispMessage(text):
    global gamepad
    
    #largeText = pygame.font.Font('image/Ubuntu-Bold.ttf', 115)
    #TextSurf, TextRect = textObj(text, largeText)
    #TextRect.center = ((pad_width/2), (pad_height/2))
    #gamepad.blit(TextSurf, TextRect)
    pygame.display.update()
    sleep(0)
    runGame()
    
def crash():
    global gamepad
    dispMessage('Crashed!')

def drawObject(obj, x, y):
    global gamepad
    gamepad.blit(obj, (x, y))
    
def back(background, x, y):
    global gamepad
    gamepad.blit(background, (x,y))

def airplane(x, y):
    global gamepad, aircraft
    gamepad.blit(aircraft, (x, y))
    
def runGame():
    global gamepad, aircraft, clock, background1, background2
    global enemy, missile, bullet, boom
    
    isShotenemy = False
    boom_count = 0
    
    score = 0
    
    bullet_xy = []
    
    x = pad_width * 0.05
    y = pad_height * 0.8
    y_change = 0

    background1_x = 0
    background2_x = background_width
    
    enemy_x = pad_width
    enemy_y = random.randrange(0, pad_height-enemy_height)
    
    missile_x = pad_width
    missile_y = random.randrange(0, pad_height-missile_height)
    
    crashed = False
    while not crashed:
        reward = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    y_change = -aircraft_speed
                elif event.key == pygame.K_DOWN:
                    y_change = aircraft_speed
                    
                elif event.key == pygame.K_LCTRL:
                    bullet_x = x + aircraft_width
                    bullet_y = y + aircraft_height/2
                    bullet_xy.append([bullet_x, bullet_y])
             
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    y_change = 0
        
        # Clear gamepad
        gamepad.fill(WHITE)
                
        # Draw Background
        background1_x -= background_speed
        background2_x -= background_speed
        
        if background1_x == -background_width:
            background1_x = background_width
            
        if background2_x == -background_width:
            background2_x = background_width
            
                       
        drawObject(background1, background1_x, 0)   
        drawObject(background2, background2_x, 0)  
        
        drawScore(score)
        
        # Check the number of enemy passed
        #if score > 2:
        #    gameOver()
        
        # Aircraft Position
        y += y_change
        if y < 0:
            y = 0
        elif y > pad_height - aircraft_height:
            y = pad_height - aircraft_height
            

       # enemy Position
        enemy_x -= enemy_speed
        if enemy_x <= 0:
            enemy_x = pad_width
            enemy_y = random.randrange(0, pad_height-enemy_height)
            score += PASS_REWARD
            reward = PASS_REWARD

        # missile Position
        missile_x -= missile_speed
        if missile_x <= 0:
            missile_x = pad_width
            missile_y = random.randrange(0, pad_height-missile_height)
                
        # Bullets Position
        if len(bullet_xy) != 0:
            for i, bxy in enumerate(bullet_xy):
                bxy[0] += bullet_speed
                bullet_xy[i][0] = bxy[0]
                
                if bxy[0] > enemy_x:
                    if bxy[1] > enemy_y and bxy[1] < enemy_y + enemy_height:
                        bullet_xy.remove(bxy)
                        isShotenemy = True
                        score += HIT_REWARD
                        reward = HIT_REWARD
                        
                if bxy[0] >= pad_width:
                    try:
                        bullet_xy.remove(bxy)
                    except:
                        pass


        # Check aircraft crashed by enemy
        if x + aircraft_width > enemy_x:
            if ((y+aircraft_height > enemy_y) and (y < enemy_y+enemy_height)):
                score += CRASH_REWARD  
                reward = CRASH_REWARD
                # crash()   

        # Check aircraft crashed by missile
        if x + aircraft_width > missile_x:
            if ((y+aircraft_height > missile_y) and (y < missile_y+missile_height)):
                score += CRASH_REWARD     
                reward = CRASH_REWARD
                # crash()
             
        drawObject(aircraft, x, y)        
        
        if len(bullet_xy) != 0:
            for bx, by in bullet_xy:
                drawObject(bullet, bx, by)
        
        if not isShotenemy:
            drawObject(enemy, enemy_x, enemy_y)
        else:
            drawObject(boom, enemy_x, enemy_y)
            boom_count += 1
            if boom_count > 5:
                boom_count = 0
                enemy_x = pad_width
                enemy_y = random.randrange(0, pad_height - enemy_height)
                isShotenemy = False
        
        drawObject(missile, missile_x, missile_y)
        
        pygame.display.update()
        clock.tick(frame_rate)
        
        print "reward =", reward
        
    pygame.quit()
    quit()
        
def initGame():
    global gamepad, aircraft, clock, background1, background2
    global enemy, missile, bullet, boom
    
    pygame.init()
    gamepad = pygame.display.set_mode((pad_width, pad_height))
    pygame.display.set_caption('Connected-X')
    aircraft = pygame.image.load('images/plane1.png')
    background1 = pygame.image.load('images/background.png')
    background2 = background1.copy()
    
    enemy = pygame.image.load('images/enemy.png')
    missile = pygame.image.load('images/missile.png')
    boom = pygame.image.load('images/explosion.png')
    bullet = pygame.image.load('images/bullet.png')
        
    
    clock = pygame.time.Clock()
    runGame()
    
if __name__ == '__main__':
    initGame()      