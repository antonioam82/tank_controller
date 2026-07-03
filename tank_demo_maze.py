#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os
import time
import argparse

grid_size = 110
grid_spacing = 1

def draw_grid():
    grid_list = glGenLists(1)
    glNewList(grid_list, GL_COMPILE)
    '''glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(0.9,0.9)
    
    glBegin(GL_QUADS)
    glColor3f(0.1,0.4,0.2)
    glVertex3f(-grid_size,-10,-grid_size)
    glVertex3f(grid_size,-10,-grid_size)
    glVertex3f(grid_size,-10,grid_size)
    glVertex3f(-grid_size,-10,-grid_size)
    glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)'''

    glLineWidth(1.0)
    glBegin(GL_LINES)
    glColor3f(1.0, 1.0, 1.0)
    
    for x in range(-grid_size, grid_size + 1, grid_spacing):
        glVertex3f(x, -2, -grid_size)
        glVertex3f(x, -2, grid_size)

    for z in range(-grid_size, grid_size + 1, grid_spacing):
        glVertex3f(-grid_size, -2, z)
        glVertex3f(grid_size, -2, z)

    glEnd()
    glEndList()
    return grid_list


def main():
    pygame.init()
    display = (800, 600)
    #mov_z = 0.001
    
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)

    # CORRECCIÓN: Configurar la lente de la cámara (Perspectiva)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
    
    grid = draw_grid()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glCallList(grid)
        #glTranslatef(0,0,mov_z)

        pygame.display.flip()

    glDeleteLists(grid, 1)
    pygame.quit()

if __name__ == "__main__":
    main()

