# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 18:47:34 2016

@author: changho
"""

#!/usr/bin/env python
#Modified from http://www.pygame.org/project-Very+simple+Pong+game-816-.html

import numpy
import pygame
import os
from pygame.locals import *
from sys import exit
import random
import pygame.surfarray as surfarray
import matplotlib.pyplot as plt

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
CRASH_REWARD = -3 # when the UAV crashes an enemy or a missile
PASS_REWARD = -1  # when an enemy passed the UAV
HIT_REWARD = 1  # when a bullet hits an enemy

# game init
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
    
    

class GameState:
    def __init__(self):
        self.uav1_x = pad_width * 0.05
        self.uav1_y = pad_height * 0.8
        self.uav1_y_change = 0
        self.isShotenemy = False
        self.boom_count = 0
        self.reward = 0

        self.bullet_xy = []
        self.x = pad_width * 0.05
        self.background1_x = 0
        self.background2_x = background_width
        self.enemy_x = pad_width
        self.enemy_y = random.randrange(0, pad_height-enemy_height)
        self.missile_x = pad_width
        self.missile_y = random.randrange(0, pad_height-missile_height)
        self.crashed = False
    

    def frame_step(self,input_vect):
        pygame.event.pump()
        reward = 0
        scroe = 0

        if sum(input_vect) != 1:
            raise ValueError('Multiple input actions!')
        
        if input_vect[1] == 1:#Key up
            self.uav1_y_change = -aircraft_speed
        elif input_vect[2] == 1:#Key down
            self.uav1_y_change = aircraft_speed
        elif input_vect[3] == 1:# launch a missile 
            self.bullet_x = x + aircraft_width
            self.bullet_y = y + aircraft_height/2
            self.bullet_xy.append([bullet_x, bullet_y])
        else: # don't move
            self.uav1_y_change = 0
        
        
        # Clear gamepad
        gamepad.fill(WHITE)
                
        # Draw Background
        self.background1_x -= background_speed
        self.background2_x -= background_speed
        
        if self.background1_x == -background_width:
            self.background1_x = background_width
            
        if self.background2_x == -background_width:
            self.background2_x = background_width
            
                       
        drawObject(background1, self.background1_x, 0)   
        drawObject(background2, self.background2_x, 0)  
        
        drawScore(score)
        
        # Check the number of enemy passed
        #if score > 2:
        #    gameOver()
        
        # Aircraft Position
        self.uav1_y += self.uav1_y_change
        if self.uav1_y < 0:
            self.uav1_y = 0
        elif self.uav1_y > pad_height - aircraft_height:
            self.uav1_y = pad_height - aircraft_height
            

       # enemy Position
        self.uav1_enemy_x -= enemy_speed
        if self.enemy_x <= 0:
            self.enemy_x = pad_width
            self.enemy_y = random.randrange(0, pad_height-enemy_height)
            score += PASS_REWARD
            reward = PASS_REWARD

        # missile Position
        self.missile_x -= missile_speed
        if self.missile_x <= 0:
            self.missile_x = pad_width
            self.missile_y = random.randrange(0, pad_height-missile_height)
                
        # Bullets Position
        if len(self.bullet_xy) != 0:
            for i, bxy in enumerate(self.bullet_xy):
                bxy[0] += bullet_speed
                self.bullet_xy[i][0] = bxy[0]
                
                if bxy[0] > self.enemy_x:
                    if bxy[1] > self.enemy_y and bxy[1] < self.enemy_y + enemy_height:
                        self.bullet_xy.remove(bxy)
                        self.isShotenemy = True
                        score += HIT_REWARD
                        reward = HIT_REWARD
                        
                if bxy[0] >= pad_width:
                    try:
                        self.bullet_xy.remove(bxy)
                    except:
                        pass


        # Check aircraft crashed by enemy
        if x + aircraft_width > self.enemy_x:
            if ((y+aircraft_height > self.enemy_y) and (y < self.enemy_y+enemy_height)):
                score += CRASH_REWARD  
                reward = CRASH_REWARD

        # Check aircraft crashed by missile
        if x + aircraft_width > self.missile_x:
            if ((y+aircraft_height > self.missile_y) and (y < self.missile_y+missile_height)):
                score += CRASH_REWARD     
                reward = CRASH_REWARD
             
        drawObject(aircraft, self.uav1_x, self.uav1_yy)        
        
        if len(self.bullet_xy) != 0:
            for bx, by in self.bullet_xy:
                drawObject(bullet, bx, by)
        
        if not isShotenemy:
            drawObject(enemy, self.enemy_x, self.enemy_y)
        else:
            drawObject(boom, self.enemy_x, self.enemy_y)
            self.boom_count += 1
            if self.boom_count > 5:
                self.boom_count = 0
                self.enemy_x = pad_width
                self.enemy_y = random.randrange(0, pad_height - enemy_height)
                self.isShotenemy = False
                
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        drawObject(missile, self.missile_x, self.missile_y)
        
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())        
        
        pygame.display.update()
        clock.tick(frame_rate)
        
        terminal = False # Now, it is a dummy. But if there exists 'game over', we need use it.
        print "reward =", reward

        return image_data, reward, terminal
