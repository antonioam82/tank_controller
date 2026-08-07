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
import numpy as np
from pathlib import Path

grid_size = 190
grid_spacing = 1

def load_object(filename):
    model = Path(filename).name
    face_indices = []
    faces = []
    vertices = []
    edges = set()
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v '):
                parts = line.strip().split()
                vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                vertices.append(vertex)
            elif line.startswith('f '):
                parts = line.strip().split()
                face_indices = [int(part) - 1 for part in parts[1:]]
                faces.append(face_indices)
                for i in range(len(face_indices)):
                    edges.add(tuple(sorted((face_indices[i], face_indices[(i + 1) % len(face_indices)]))))
        
        if model == 'maze_large_with_plazes.obj':
            verts_np = np.array(vertices)
            min_v = np.min(verts_np, axis=0)
            max_v = np.max(verts_np, axis=0)
            center = (min_v + max_v) / 2.0

            vertices = [list(np.array(v) - center) for v in vertices]

    return vertices, edges, faces 

def draw_model(path):
    model_name = os.path.basename(path)
    v, e, f = load_object(path)
    glBegin(GL_LINES)
    for a, b in e:
        glVertex3f(*v[a])
        glVertex3f(*v[b])
    glEnd()

    glColor3f(0.0, 0.1, 0.0)
    glBegin(GL_QUADS)
    for face in f:
        for vertex in face:
            glVertex3fv(v[vertex])
    glEnd()


def draw_grid():
    grid_list = glGenLists(1)
    glNewList(grid_list, GL_COMPILE)
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(0.9,0.9)
    
    glBegin(GL_QUADS)
    glColor3f(0.4,0.5,0.1)
    glVertex3f(-grid_size,-2,-grid_size)
    glVertex3f(grid_size,-2,-grid_size)
    glVertex3f(grid_size,-2,grid_size)
    glVertex3f(-grid_size,-2,grid_size)
    glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)

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

    scene_rotx = 0.0
    scene_roty = 0.0
    scene_rotz = 0.0

    scene_scale = 1.5
    
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)

    # CORRECCIÓN: Configurar la lente de la cámara (Perspectiva)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 30, 80,   # posición de la cámara (alejada y elevada)
              0, 0, 0,     # punto al que mira (ajustá según el centro real de tu maze)
              0, 1, 0)     # vector "arriba"
    
    base = os.path.dirname(__file__)
    obj_maze = os.path.join(base, "tanque", "maze_large_with_plazes.obj")

    model_maze = glGenLists(1)
    glNewList(model_maze, GL_COMPILE)
    draw_model(obj_maze)
    glEndList()
    
    grid = draw_grid()
    #glScale(scene_scale,scene_scale,scene_scale)


    clock = pygame.time.Clock()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    running = False

        key = pygame.key.get_pressed()

        if key[pygame.K_r]:
            glRotatef(2,0.0,1.0,0.0)
        elif key[pygame.K_t]:
            glRotatef(-2,0.0,1.0,0.0)

        if key[pygame.K_f]:
            glRotatef(2,1.0,0.0,0.0)
        elif key[pygame.K_g]:
            glRotatef(-2,1.0,0.0,0.0)

        if key[pygame.K_z]:
            scene_scale += 0.05
        elif key[pygame.K_x]:
            scene_scale -= 0.05



        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glScalef(scene_scale,scene_scale,scene_scale)
     
        glCallList(grid)
        glPushMatrix()
        glRotatef(90, 1.0, 0.0, 0.0)
        glScalef(10.0,10.0,2.5)
        glTranslatef(0,0,0)
        glCallList(model_maze)
        glPopMatrix()
        #glTranslatef(0,0,mov_z)
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

    glDeleteLists(grid, 1)
    pygame.quit()

if __name__ == "__main__":
    main()

