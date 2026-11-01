import sys
import numpy as np
import pygame 
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
import math
import os

# DIMENSIONES DEL GRID
grid_size = 20
grid_spacing = 1

pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(50, display[0] / display[1], 0.1, 100.0)
glMatrixMode(GL_MODELVIEW)

def draw_grid():
    line_data = []
    for x in range(-grid_size, grid_size + 1, grid_spacing):
        line_data += [x, 0, -grid_size, x, 0, grid_size]
    for z in range(-grid_size, grid_size + 1, grid_spacing):
        line_data += [-grid_size, 0, z,  grid_size, 0, z]
    
    line_vertices = np.array(line_data, dtype=np.float32)

    line_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, line_vbo)
    glBufferData(GL_ARRAY_BUFFER, line_vertices.nbytes, line_vertices, GL_STATIC_DRAW)

    return line_vbo, len(line_vertices) // 3   # el VBO y cuántos vértices tiene


line_vbo, line_count = draw_grid()
glLineWidth(1.0)
#angle = 0.0
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    glClear(GL_COLOR_BUFFER_BIT)

    # Cámara: alejada, inclinada hacia abajo y girando despacio
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -25.0)
    glRotatef(30.0, 1, 0, 0)
    #glRotatef(angle, 0, 1, 0)
    #angle += 0.3

    # --- Se hace en CADA frame: una sola llamada de dibujo ---
    glEnableClientState(GL_VERTEX_ARRAY)
    glColor3f(1.0, 1.0, 1.0)
    glBindBuffer(GL_ARRAY_BUFFER, line_vbo)
    glVertexPointer(3, GL_FLOAT, 0, None)
    glDrawArrays(GL_LINES, 0, line_count)
    glDisableClientState(GL_VERTEX_ARRAY)

    pygame.display.flip()
    clock.tick(60)

glDeleteBuffers(1, [line_vbo])
pygame.quit()

