#!/usr/bin/env python
from functools import reduce
import math
import pygame
import sys

# Colours
GREEN =     (000, 200, 000)
BLACK =     (000, 000, 000)

BG_COL = BLACK              # Background colour
FG_COL = GREEN              # Foreground (vector) colour

# Initialize pygame
pygame.init()

SIZE = (700, 700)           # Size of window
PXW, PXH = 10, 10           # How many pixels until we draw a vector
SCALE = 15                  # How long the vectors are (max)
C_SCALE = 5e-6              # Scale that strength increases by (C)
SENSITIVITY_DEG = 20        # How many pixels until you could delete things
S_FACTOR = 1                # How much strength changes by

scrn = pygame.display.set_mode(SIZE)
pygame.display.set_caption('Electric Fields')

clock = pygame.time.Clock()
running = True
fields = []
strength = 1
redraw = False

def get_sign(n):
    return abs(n) / n

class Vect:
    def __init__(self, x, y):
        '''
        x, y = Component vectors x and y
        '''
        self.x = x
        self.y = y

    def __add__(self, v):
        if isinstance(v, self.__class__):
            x = self.x + v.x
            y = self.y + v.y
            return Vect(x, y)

    def __str__(self):
        return '(%d, %d)' % (self.x, self.y)

    def bound(self, scale):
        if abs(self.x) > scale: self.x = get_sign(self.x) * scale
        if abs(self.y) > scale: self.y = get_sign(self.y) * scale


def dist(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def get_field_mag(c, r):
    return 8.988e9 * c / r**2

def get_field(i, tst):
    '''
    i: the field item (x, y, c)
    tst: the test charge (x, y)
    Returns the field vector relative to the test point
    '''
    mag = get_field_mag(i[2], dist(tst[0], tst[1], i[0], i[1]))
    rad = math.atan2(tst[1]-i[1], tst[0]-i[0])
    xpos = mag * math.cos(rad)
    ypos = mag * math.sin(rad)
    return Vect(xpos, ypos)

def update_display(col):
    '''
    Runs through pixels on screen and creates a vector tail(ish) thing,
    thus creating the illusion of electric fields.

    Test charges are created positive by nature.

    fields item: (x, y, c)
    x, y: x, y position on screen
    c: charge of field (positive or negative)
    '''
    global fields, scrn

    # Sanity checking
    if len(fields) == 0: return

    for x in range(0, SIZE[0], PXW):
        for y in range(0, SIZE[1], PXH):
            # Gets a list of vector of the various fields
            strengths = map(lambda i: get_field(i, (x, y)), fields)
            # Sums all the vectors up
            aggr = reduce(lambda x,y: x+y, strengths)
            # Restricts them to stop the lines from getting too out of hand
            aggr.bound(SCALE)
            # Visually displays the vector as a line drawn
            pygame.draw.line(scrn, col, (x,y), (x+aggr.x,y+aggr.y))




while running:
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        elif evt.type == pygame.KEYDOWN:
            key = pygame.key.get_pressed()
            if key[pygame.K_UP]:
                strength += S_FACTOR
            if key[pygame.K_DOWN]:
                strength -= S_FACTOR
            if key[pygame.K_c]:
                fields = []
                redraw = True
        elif evt.type == pygame.MOUSEBUTTONDOWN:
            pressed = pygame.mouse.get_pressed()
            # Check what buttons are pressed
            if pressed[0]:
                # Button 1 was pressed
                # Add electric charge
                if strength:
                    pos = pygame.mouse.get_pos()
                    # Scales the magnitude first
                    fields.append([pos[0], pos[1], strength * C_SCALE])
            elif pressed[2] and len(fields):
                # Button 3 was pressed
                # Remove nearest electric charge, to a certain degree
                pos = pygame.mouse.get_pos()
                fmin = min(fields, key=lambda f: dist(pos[0],pos[1],f[0],f[1]))
                if dist(pos[0],pos[1],fmin[0],fmin[1]) <= SENSITIVITY_DEG:
                    fields.remove(fmin)

            redraw = True

    # Update the display
    # Doesn't redraw every frame
    if redraw:
        # Blit screen black
        scrn.fill(BG_COL)

        update_display(FG_COL)

        # Flip the display
        pygame.display.flip()

        redraw = False

    # 60 FPS
    clock.tick(60)

pygame.quit()

