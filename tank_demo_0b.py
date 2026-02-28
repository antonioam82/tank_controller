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
    glBegin(GL_LINES)
    glColor3f(1, 1, 1)

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

    # ================= ESTADO =================
    x = z = 0.0
    grid_mov_x = grid_mov_z = 0.0

    model_angle = 180.0
    target_angle = 180.0
    rotation_speed = 3.0

    y_tower = 0.0
    direction = 'front'
    new_direction = 'front'
    rotating = False

    bullets = []
    bullet_speed = 0.5

    # <<< MAPA DE DIRECCIONES CORRECTO
    DIRECTION_ANGLE = {
        'front': 180,
        'right': 90,
        'back': 0,
        'left': 270
    }

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False

            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    running = False

                elif e.key == K_UP:
                    new_direction = 'front'
                elif e.key == K_DOWN:
                    new_direction = 'back'
                elif e.key == K_LEFT:
                    new_direction = 'left'
                elif e.key == K_RIGHT:
                    new_direction = 'right'

                if new_direction != direction:
                    target_angle = DIRECTION_ANGLE[new_direction]
                    rotating = True
                    grid_mov_x = grid_mov_z = 0.0

                elif e.key == K_y:
                    rot = model_angle + y_tower
                    rad = math.radians(rot)
                    bullets.append({
                        "pos": [-x + math.sin(rad) * 2.2, 0.2, -z + math.cos(rad) * 2.2],
                        "dir": [math.sin(rad), 0.0, math.cos(rad)]
                    })

        # ================= GIRO SUAVE CORRECTO =================
        if rotating:
            diff = (target_angle - model_angle + 180) % 360 - 180
            if abs(diff) < rotation_speed:
                model_angle = target_angle
                rotating = False
                direction = new_direction
            else:
                model_angle += rotation_speed * (1 if diff > 0 else -1)

        # ================= MOVIMIENTO =================
        if not rotating:
            rad = math.radians(model_angle)
            grid_mov_x = -math.sin(rad) * 0.05
            grid_mov_z = math.cos(rad) * 0.05

        x += grid_mov_x
        z += grid_mov_z

        # ================= BALAS =================
        for b in bullets:
            b["pos"][0] += b["dir"][0] * bullet_speed
            b["pos"][2] += b["dir"][2] * bullet_speed

        # ================= RENDER =================
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glTranslatef(x, 0, z)
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

        # ===== BALAS =====
        for b in bullets:
            glPushMatrix()
            glTranslatef(*b["pos"])
            ang = math.degrees(math.atan2(b["dir"][0], b["dir"][2]))
            glRotatef(ang, 0, 1, 0)
            glCallList(model_bullet)
            glPopMatrix()

        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()


main()
