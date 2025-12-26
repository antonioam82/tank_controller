#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os

# ================= GRID =================
grid_size = 110
grid_spacing = 1


def draw_grid():
    grid_list = glGenLists(1)
    glNewList(grid_list, GL_COMPILE)

    glLineWidth(1.0)
    glBegin(GL_LINES)
    glColor3f(1.0, 1.0, 1.0)

    for x in range(-grid_size, grid_size + 1, grid_spacing):
        glVertex3f(x, 0, -grid_size)
        glVertex3f(x, 0, grid_size)

    for z in range(-grid_size, grid_size + 1, grid_spacing):
        glVertex3f(-grid_size, 0, z)
        glVertex3f(grid_size, 0, z)

    glEnd()
    glEndList()
    return grid_list


# ================= OBJ =================
def load_object(filename):
    vertices = []
    edges = set()

    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if line.startswith('v '):
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('f '):
                idx = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                for i in range(len(idx)):
                    edges.add(tuple(sorted((idx[i], idx[(i + 1) % len(idx)]))))

    return vertices, edges


def draw_model(path):
    v, e = load_object(path)
    glBegin(GL_LINES)
    for a, b in e:
        glVertex3f(*v[a])
        glVertex3f(*v[b])
    glEnd()


# ================= TEXT =================
def draw_text(font, x, y, text):
    surf = font.render(text, True, (0, 0, 0), (0, 0, 255))
    data = pygame.image.tostring(surf, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(surf.get_width(), surf.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, data)


# ================= MAIN =================
def main():
    pygame.init()
    display = (800, 600)
    font = pygame.font.SysFont('arial', 15)

    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 6)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glClearColor(0, 0, 0, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_LINE_SMOOTH)

    gluPerspective(45, display[0] / display[1], 0.1, 200)
    glTranslatef(0, 0, -10)
    glRotatef(35, 1, 0, 0)

    base = os.path.dirname(__file__)
    tank_body = os.path.join(base, "tanque", "resto_tanque.obj")
    tank_tower = os.path.join(base, "tanque", "torre.obj")
    bullet_obj = os.path.join(base, "tanque", "bullet.obj")

    grid_list = draw_grid()

    model_list = glGenLists(1)
    glNewList(model_list, GL_COMPILE)
    draw_model(tank_body)
    glEndList()

    model_list2 = glGenLists(1)
    glNewList(model_list2, GL_COMPILE)
    draw_model(tank_tower)
    glEndList()

    model_list3 = glGenLists(1)
    glNewList(model_list3, GL_COMPILE)
    draw_model(bullet_obj)
    glEndList()

    # ======= STATE =======
    x = z = 0.0               # movimiento del mundo
    grid_mov_x = grid_mov_z = 0.0

    model_angle = 180
    y_tower = 0.0
    sc_y = 0.0
    scale = 1.0

    show_bullet = False
    bullet_pos = [0.0, 0.2, 0.0]
    bullet_rot = 0.0
    bullet_speed = 0.3

    direction = 'front'
    running = True
    hide_text = False
    counter = 0

    # ======= LOOP =======
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

                elif event.key == K_UP:
                    grid_mov_z = 0.05
                    grid_mov_x = 0
                    model_angle = 180
                    direction = 'front'

                elif event.key == K_DOWN:
                    grid_mov_z = -0.05
                    grid_mov_x = 0
                    model_angle = 0
                    direction = 'back'

                elif event.key == K_LEFT:
                    grid_mov_x = 0.05
                    grid_mov_z = 0
                    model_angle = -90
                    direction = 'left'

                elif event.key == K_RIGHT:
                    grid_mov_x = -0.05
                    grid_mov_z = 0
                    model_angle = 90
                    direction = 'right'

                elif event.key == K_c:
                    grid_mov_x = grid_mov_z = 0

                elif event.key == K_y:
                    bullet_rot = model_angle + y_tower
                    rad = math.radians(bullet_rot)

                    bullet_pos[0] = math.sin(rad) * 2.2
                    bullet_pos[1] = 0.2
                    bullet_pos[2] = math.cos(rad) * 2.2

                    show_bullet = True

        key = pygame.key.get_pressed()
        if key[K_n]:
            y_tower += 1.2
        elif key[K_m]:
            y_tower -= 1.2

        # ===== UPDATE =====
        x += grid_mov_x
        z += grid_mov_z

        if show_bullet:
            rad = math.radians(bullet_rot)
            bullet_pos[0] += math.sin(rad) * bullet_speed
            bullet_pos[2] += math.cos(rad) * bullet_speed

            # <<< CAMBIO CRÍTICO
            bullet_pos[0] -= grid_mov_x
            bullet_pos[2] -= grid_mov_z

        # ===== DRAW =====
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glScalef(scale, scale, scale)
        glRotatef(sc_y, 0, 1, 0)
        glTranslatef(x, 0, z)

        glCallList(grid_list)

        glPushMatrix()
        glTranslatef(-x, 0.2, -z)
        glRotatef(model_angle, 0, 1, 0)

        glPushMatrix()
        glRotatef(y_tower, 0, 1, 0)
        glColor3f(0, 1, 0)
        glCallList(model_list2)
        glPopMatrix()

        glColor3f(0, 1, 0)
        glCallList(model_list)
        glPopMatrix()

        glPopMatrix()

        if show_bullet:
            glPushMatrix()
            glColor3f(1, 0, 0)
            glTranslatef(*bullet_pos)
            glRotatef(bullet_rot, 0, 1, 0)
            glCallList(model_list3)
            glPopMatrix()

        if not hide_text:
            draw_text(font, 20, 570, "DEMO")

        counter += 1
        if counter > 50:
            counter = 0
            hide_text = not hide_text

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()


main()





