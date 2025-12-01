#/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import os

# ESTABLECER DIMENSIONES DEL GRID
grid_size = 110
grid_spacing = 1


# FUNCION DE DIBUJADO DE GRID
def draw_grid():
    grid_list = glGenLists(1)
    glNewList(grid_list, GL_COMPILE)
    glLineWidth(1.0)
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

def load_object(filename):
    vertices = []
    face_indices = []
    edges = set()
    faces = []
    
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if line.startswith('v '):
                vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                vertices.append(vertex)
            elif line.startswith('f '):
                face_indices = [int(part) - 1 for part in parts[1:]]
                
                for i in range(len(face_indices)):
                    edges.add(tuple(sorted((face_indices[i], face_indices[(i + 1) % len(face_indices)]))))
         
        return vertices, edges, faces

def draw_model(obj_path):
    v, e, f = load_object(obj_path)
    print("CARGA CORRECTA")
    ordered_edges = sorted(list(e))

    glBegin(GL_LINES)
    for e1, e2 in ordered_edges:
        x1, y1, z1 = v[e1]
        x2, y2, z2 = v[e2]
        glVertex3f(x1, y1, z1)
        glVertex3f(x2, y2, z2)
    glEnd()
    glEndList()

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
    
    ##################################################
    base_path = os.path.dirname(__file__)
    obj_path = os.path.join(base_path, "tanque", "resto_tanque.obj")
    obj_path2 = os.path.join(base_path, "tanque", "torre.obj")
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #vertices, edges, faces = load_object(obj_path)
    #print("CARGA CORRECTA")    

    model_list = glGenLists(1)
    glNewList(model_list, GL_COMPILE)

    #ordered_edges = sorted(list(edges))
    draw_model(obj_path)
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #vertices, edges, faces = load_object(obj_path2)
    #print("CARGA COMPLETA")
    
    model_list2 = glGenLists(1)
    glNewList(model_list2, GL_COMPILE)

    #ordered_edges = sorted(list(edges))
    draw_model(obj_path2)
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


    #################################################

    grid_list = draw_grid()

    grid_mov = 0.0

    x = 0.0
    z = 0.0

    y_tower = 0.0
    sc_y = 0.0
    
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_b:
                    grid_mov = -0.05
                elif event.key == pygame.K_v:
                    grid_mov = 0.05
                elif event.key == pygame.K_c:
                    grid_mov = 0.0

        key = pygame.key.get_pressed()

        if key[pygame.K_t]:
            #glRotatef(1.0, 0.0, 1.0, 0.0)
            sc_y += 1.0
        
        elif key[pygame.K_r]:
            #glRotatef(-1.0, 0.0, 1.0, 0.0)
            sc_y -= 1.0

        if key[pygame.K_f]:
            glRotatef(0.5, 1.0, 0.0, 0.0)
        elif key[pygame.K_g]:
            glRotatef(-0.5, 1.0, 0.0, 0.0)

        if key[pygame.K_n]:
            y_tower -= 1.1
        elif key[pygame.K_m]:
            y_tower += 1.1
 
        #print(y_tower) 

        # LIMPIAR PANTALLA
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        # DIBUJOS
        glPushMatrix()
        glRotatef(sc_y, 0.0, 1.0, 0.0)
        glTranslatef(x, 0.0, z)##########
        glCallList(grid_list)
        glPushMatrix()
        glLineWidth(1.5)
        glTranslatef(0.0,0.2,-z)
        glColor3f(0.0,1.0,0.0)
        glPushMatrix()
        glRotatef(y_tower,0.0,1.0,0.0)
        glCallList(model_list2)
        glPopMatrix()
        glCallList(model_list)
        glPopMatrix()
        glPopMatrix()

        z += grid_mov

        # REFRESCO PANTALLA
        pygame.display.flip()
        pygame.time.wait(10)

    glDeleteLists(grid_list, 1)
    glDeleteLists(model_list, 1)
    glDeleteLists(model_list2, 1)
    pygame.quit()

main()
