# -*- coding: utf-8 -*-
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

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

# ================= TEXT (PIL) =================
font = ImageFont.load_default()

def draw_text(x, y, text):
    img = Image.new("RGBA", (300, 30), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font, fill=(0, 255, 0, 255))

    img_data = np.array(img, dtype=np.uint8)

    glWindowPos2d(x, y)
    glDrawPixels(img.size[0], img.size[1], GL_RGBA, GL_UNSIGNED_BYTE, img_data)

# ================= OBJ =================
def load_object(filename):
    vertices, faces, edges = [], [], set()

    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v '):
                parts = line.split()
                vertices.append(list(map(float, parts[1:4])))

            elif line.startswith('f '):
                parts = line.split()
                idx = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                faces.append(idx)

                for i in range(len(idx)):
                    edges.add(tuple(sorted((idx[i], idx[(i+1) % len(idx)]))))

    return vertices, edges, faces

def draw_model(path):
    v, e, f = load_object(path)

    glColor3f(1, 0, 0)
    glBegin(GL_LINES)
    for a, b in e:
        glVertex3f(*v[a])
        glVertex3f(*v[b])
    glEnd()

# ================= MAIN =================
def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "OpenGL Tank", None, None)
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)

    gluPerspective(45, 800/600, 0.1, 90)
    glTranslatef(0, 0, -10)

    grid = draw_grid()

    # estado
    x = z = 0.0
    grid_mov_x = grid_mov_z = 0.0
    direction = 'front'
    rot_x = 35
    rot_y = 0
    scale = 1.0

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # INPUT
        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            grid_mov_z = 0.00005
            direction = 'front'
        elif glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            grid_mov_z = -0.00005
            direction = 'back'
        else:
            grid_mov_z = 0

        if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
            grid_mov_x = 0.0005
            direction = 'left'
        elif glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
            grid_mov_x = -0.005
            direction = 'right'
        else:
            grid_mov_x = 0

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            break

        # UPDATE
        x += grid_mov_x
        z += grid_mov_z

        # RENDER
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glScalef(scale, scale, scale)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)
        glTranslatef(x, 0, z)

        glCallList(grid)

        glPopMatrix()

        # TEXT
        draw_text(10, 570, f'X: {x:.2f}')
        draw_text(10, 540, f'Z: {z:.2f}')
        draw_text(10, 510, f'DIR: {direction}')

        glfw.swap_buffers(window)

    glfw.terminate()

main()
