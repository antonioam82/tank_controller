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


def load_object(filename):
    vertices = []
    edges = set()
    with open(filename, 'r') as f:
        for line in f:
            p = line.split()
            if line.startswith('v '):
                vertices.append([float(p[1]), float(p[2]), float(p[3])])
            elif line.startswith('f '):
                idx = [int(i) - 1 for i in p[1:]]
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


# ================= MAIN =================
def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, display[0] / display[1], 0.1, 90)
    glTranslatef(0, 0, -10)
    glRotatef(35, 1, 0, 0)
    glEnable(GL_DEPTH_TEST)

    base = os.path.dirname(__file__)
    obj_base = os.path.join(base, "tanque", "resto_tanque.obj")
    obj_tower = os.path.join(base, "tanque", "torre.obj")
    obj_bullet = os.path.join(base, "tanque", "bullet.obj")

    model_base = glGenLists(1)
    glNewList(model_base, GL_COMPILE)
    draw_model(obj_base)
    glEndList()

    model_tower = glGenLists(1)
    glNewList(model_tower, GL_COMPILE)
    draw_model(obj_tower)
    glEndList()

    model_bullet = glGenLists(1)
    glNewList(model_bullet, GL_COMPILE)
    draw_model(obj_bullet)
    glEndList()

    grid = draw_grid()

    # ============== ESTADO ==============
    x = y = z = 0.0                # desplazamiento del mundo
    grid_mov_x = grid_mov_z = 0.0
    model_angle = 180
    y_tower = 0.0
    sc_y = 0.0
    scale = 1.0

    bullets = []
    bullet_speed = 0.2

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False

            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    running = False

                elif e.key == K_UP:
                    grid_mov_z = 0.05
                    grid_mov_x = 0.0
                    model_angle = 180

                elif e.key == K_DOWN:
                    grid_mov_z = -0.05
                    grid_mov_x = 0.0
                    model_angle = 0

                elif e.key == K_LEFT:
                    grid_mov_x = 0.05
                    grid_mov_z = 0.0
                    model_angle = -90

                elif e.key == K_RIGHT:
                    grid_mov_x = -0.05
                    grid_mov_z = 0.0
                    model_angle = 90

                # ===== DISPARO CORRECTO =====
                elif e.key == K_y:
                    rot = model_angle + y_tower
                    rad = math.radians(rot)

                    bx = -x + math.sin(rad) * 2.2
                    bz = -z + math.cos(rad) * 2.2

                    bullets.append({
                        "pos": [bx, 0.2, bz],
                        "dir": [math.sin(rad), 0.0, math.cos(rad)]
                    })

        keys = pygame.key.get_pressed()

        if keys[K_t]:
            sc_y += 1.0
        if keys[K_r]:
            sc_y -= 1.0
        if keys[K_n]:
            y_tower += 1.1
        if keys[K_m]:
            y_tower -= 1.1
        if keys[K_z]:
            scale += 0.02
        if keys[K_x]:
            scale -= 0.02

        # ===== ACTUALIZACIÓN =====
        x += grid_mov_x
        z += grid_mov_z

        for b in bullets:
            b["pos"][0] += b["dir"][0] * bullet_speed
            b["pos"][2] += b["dir"][2] * bullet_speed

        # ===== RENDER =====
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glScalef(scale, scale, scale)
        glRotatef(sc_y, 0, 1, 0)
        glTranslatef(x, y, z)

        glCallList(grid)

        # ===== TANQUE =====
        glPushMatrix()
        glTranslatef(-x, 0.2, -z)
        glRotatef(model_angle, 0, 1, 0)

        glPushMatrix()
        glRotatef(y_tower, 0, 1, 0)
        glCallList(model_tower)
        glPopMatrix()

        glCallList(model_base)
        glPopMatrix()

        # ===== BALAS (MUNDO REAL) =====
        for b in bullets:
            glPushMatrix()
            glTranslatef(b["pos"][0], b["pos"][1], b["pos"][2])
            ang = math.degrees(math.atan2(b["dir"][0], b["dir"][2]))
            glRotatef(ang, 0, 1, 0)
            glCallList(model_bullet)
            glPopMatrix()

        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()


main()







