#/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os

# ESTABLECER DIMENSIONES DEL GRID
grid_size = 20 #110
grid_spacing = 1


# FUNCION DE DIBUJADO DE GRID
def draw_grid():
    grid_list = glGenLists(1)
    glNewList(grid_list, GL_COMPILE)

    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(0.9,0.9)
    glBegin(GL_QUADS)
    glColor3f(0.1,0.5,0.4)
    glVertex3f(-grid_size,0,-grid_size)
    glVertex3f(grid_size,0,-grid_size)
    glVertex3f(grid_size, 0, grid_size)
    glVertex3f(-grid_size, 0, grid_size)
    glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)

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

def draw_text(f, x, y, text):
    textSurface = f.render(text, True, (0, 0, 0), (0,0,255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

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
    #glEndList()

def main():
    pygame.init()
    display = (800, 600)

    font = pygame.font.SysFont('arial', 15)
    
    #-------------------------------------ANTIALIASING------------------------------------#
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 6)
    
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glClearColor(0.2, 0.4, 0.8, 1.0)  # color fondo 

    glEnable(GL_MULTISAMPLE)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    #-------------------------------------------------------------------------------------#


    gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
    glTranslatef(0.0, 0.0, -10.0)
    glEnable(GL_DEPTH_TEST)
    glRotatef(35.0, 1.0, 0.0, 0.0)
    
    ##################################################
    base_path = os.path.dirname(__file__)
    obj_path = os.path.join(base_path, "tanque", "resto_tanque.obj")
    obj_path2 = os.path.join(base_path, "tanque", "torre.obj")
    obj_path3 = os.path.join(base_path, "tanque", "bullet.obj")
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++   

    model_list = glGenLists(1)
    glNewList(model_list, GL_COMPILE)

    draw_model(obj_path)
    glEndList()
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    model_list2 = glGenLists(1)
    glNewList(model_list2, GL_COMPILE)

    draw_model(obj_path2)
    glEndList()
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    model_list3 = glGenLists(1)
    glNewList(model_list3, GL_COMPILE)

    draw_model(obj_path3)
    glEndList()
    #################################################

    grid_list = draw_grid()
   
    grid_mov_x = 0.0
    grid_mov_z = 0.0
    stop_camera = False

    show_bullet = False
    bullet_pos = [0.0,0.0,0.0]
    bullet_rot = 0.0

    direction = 'front'

    x = 0.0
    y = 0.0
    z = 0.0
    bullet_z = 2.05
    model_angle = 180

    y_tower = 0.0
    sc_y = 0.0
    counter = 0

    hide_text = False
    scale = 1.0

    
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_UP:
                    grid_mov_z = 0.05
                    grid_mov_x = 0.00
                    direction = 'front'
                    model_angle = 180
                elif event.key == pygame.K_LEFT:
                    grid_mov_z = 0.00
                    grid_mov_x = 0.05
                    direction = 'left'
                    model_angle = -90
                elif event.key == pygame.K_RIGHT:
                    grid_mov_z = 0.00
                    grid_mov_x = -0.05
                    direction = 'right'
                    model_angle = 90
                elif event.key == pygame.K_DOWN:
                    grid_mov_z = -0.05
                    grid_mov_x = 0.00
                    direction = 'back'
                    model_angle = 0
                elif event.key == pygame.K_s:
                    stop_camera = not stop_camera
                elif event.key == pygame.K_c:
                    grid_mov_z = 0.00
                    grid_mov_x = 0.00
                    direction = direction
                    model_angle = model_angle
                elif event.key == pygame.K_y:
                    show_bullet = True

                    # guardar posición GLOBAL del extremo del cañón
                    bullet_pos[0] = x
                    bullet_pos[1] = 0.00
                    bullet_pos[2] = 3.0 #z #+ bullet_z #+ 0.25

                    # guardar rotación GLOBAL en el momento del disparo
                    bullet_rot = model_angle + y_tower


                elif event.key == pygame.K_a:
                    scale = 1.0
                elif event.key == pygame.K_l:
                    grid_mov_x = 0.0
                    grid_mov_z = 0.0

                    direction = 'front'
                    #stuck = False

                    x = 0.0
                    y = 0.0
                    z = 0.0
          
                    model_angle = 180

                    y_tower = 0.0
                    sc_y = 0.0
                    scale = 1.0
                    glLoadIdentity()
                    gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
                    glTranslatef(0.0, 0.0, -10)
                    glRotatef(35.0, 1.0, 0.0, 0.0)
                elif event.key == pygame.K_b:
                    y_tower = 0.0


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
        
        if direction == 'front' or direction == 'right':
            if key[pygame.K_n]:
                y_tower += 1.1
            elif key[pygame.K_m]:
                y_tower -= 1.1
        elif direction == 'back' or direction == 'left':
            if key[pygame.K_n]:
                y_tower -= 1.1
            elif key[pygame.K_m]:
                y_tower += 1.1

        if key[pygame.K_z]:
            scale += 0.02
        elif key[pygame.K_x]:
            scale -= 0.02 

        # LIMPIAR PANTALLA
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        # DIBUJOS
        glPushMatrix()
        glScalef(scale, scale, scale)
        glRotatef(sc_y, 0.0, 1.0, 0.0)
        if stop_camera:
            glTranslatef(0, 0, 0)
        else:
            glTranslatef(x, y, z)
        glCallList(grid_list)
        glPushMatrix()
        glLineWidth(1.5)
        glTranslatef(-x,0.2,-z)
        glColor3f(0.0,0.0,0.0)
        glRotatef(model_angle,0.0,1.0,0.0)###########
        glPushMatrix()
        glRotatef(y_tower,0.0,1.0,0.0)
        glCallList(model_list2)
        if show_bullet:
            glPushMatrix()
            glColor3f(1.0, 0.0, 0.0)

            # aplicar SOLO la transformación congelada
            glTranslatef(bullet_pos[0], bullet_pos[1], bullet_pos[2])
            glRotatef(bullet_rot, 0.0, 1.0, 0.0)

            glCallList(model_list3)
            glPopMatrix()
        glPopMatrix()
        #glPushMatrix()
        #glColor3f(1.0,0.0,0.0)
        #glCallList(model_list3)
        #glPopMatrix()
        glColor3f(0.0,0.0,0.0)
        glTranslatef(0.0,0.01,0.0)###########
        glCallList(model_list)
        glPopMatrix()
        glPopMatrix()

        # LIMITAR MOVIMIENTO DENTRO DEL GRID

        if x - 2 < (-grid_size - 0.1) or  x + 2 > (grid_size + 0.1):
            grid_mov_x = 0.0
            if direction == 'left':
                x -= 0.1
            elif direction == 'right':
                x += 0.1
                #stuck = True
        if z - 2 < (-grid_size - 0.1) or  z + 2 > (grid_size + 0.1):
            grid_mov_z = 0.0
            if direction == 'front':
                z -= 0.1
            elif direction == 'back':
                z += 0.1 
            #stuck = True

        x += grid_mov_x
        z += grid_mov_z
        bullet_pos[2] += 0.1

        #bullet_pos[2] += math.cos(math.radians(bullet_rot)) * 0.1
        #bullet_pos[0] += math.sin(math.radians(bullet_rot)) * 0.1


        '''if x - 2 < -grid_size:
            #x  = -grid_size
            grid_mov_x = 0.0
        if x + 2 > grid_size:
            #x = grid_size
            grid_mov_x = 0.0

        if z - 2 < -grid_size:
            #z = -grid_size
            grid_mov_z = 0.0
        if z + 2 > grid_size:
            #z = grid_size
            grid_mov_z = 0.0'''


        if not hide_text:
            draw_text(font, 20, 570, 'DEMO')

        counter += 1
        if counter >= 50:
            counter = 0
            hide_text = not hide_text

        # REFRESCO PANTALLA
        pygame.display.flip()
        pygame.time.wait(10)

    glDeleteLists(grid_list, 1)
    glDeleteLists(model_list, 1)
    glDeleteLists(model_list2, 1)
    pygame.quit()

main()
