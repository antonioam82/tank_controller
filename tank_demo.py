#/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# ESTABLECER DIMENSIONES DEL GRID
grid_size = 110
grid_spacing = 1


# FUNCION DE DIBUJADO DE GRID
def draw_grid():
    grid_list = glGenLists(1)
    glNewList(grid_list, GL_COMPILE)
    glLineWidth(1.2)
    glBegin(GL_LINES)
    glColor3f(1.0,1.0,1.0) # COLOR BLANCO

    # DIBUJADO
    for x in range(-grid_size, grid_size + 1, grid_spacing):
        glVertex3f(x, 0, -grid_size)
        glVertex3f(x, 0, grid_size)

    for z in range(-grid_size, grid_size + 1, grid_spacing):
        glVertex3f(-grid_size, 0, z)
        glVertex3f(grid_size, 0, z)

    glEnd()
    glEndList()
    return grid_list

def main():
    pygame.init()
    display = (800, 600)
    
    #-------------------------------------ANTIALIASING------------------------------------#
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 6)
    
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glEnable(GL_MULTISAMPLE)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    #-------------------------------------------------------------------------------------#

    gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
    glTranslatef(0.0, 0.0, -10.0)
    glEnable(GL_DEPTH_TEST)
    glRotatef(15.0, 1.0, 0.0, 0.0)

    grid_list = draw_grid()

    x = 0.0
    z = 0.0
    
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # LIMPIAR PANTALLA
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        # GRID
        glPushMatrix()
        glTranslatef(x, 0.0, z)
        glCallList(grid_list)
        glPopMatrix()

        # REFRESCO PANTALLA
        pygame.display.flip()
        pygame.time.wait(10)

    glDeleteLists(grid_list, 1)
    pygame.quit()

main()
