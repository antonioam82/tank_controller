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
    grid_list = glGenList(1)
    glNewList(grid_list, GL_COMPILE)
    glLineWidth(1.2)
    glBegin(GL_LINES)
    glColor3f(1.0,1.0,1.0) # COLOR BLANCO

    # DIBUJADO
    for x in range(-grid_size, grid_size + 1, grid_spacing):
        glVertex3f(x, 0, -grid_size)
        glVertex3f(x, 0, grid_size)

    for y in range(-grid_size, grid_size + 1, grid_spacing):
        glVertex3f(-grid_size, 0, z)
        glVertex3f(grid_size, 0, z)

    glEnd()
    glEndList()
    return grid_list


# TODO BIEN
print("OK")
