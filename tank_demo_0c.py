# -*- coding: utf-8 -*-
import glfw
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

# Nota: El renderizado de texto en GLFW puro requiere texturas o bibliotecas extra.
# Se mantiene la estructura para no romper la lógica, pero sin funcionalidad de Pygame.
def draw_text(x, y, text):
    pass 

def show_controls():
    print("\n--------------------------- Controls ---------------------------")
    print("\nKeyboard Controls (Tank Movement):")
    print("  - Up Arrow: Move tank forward")
    print("  - Down Arrow: Move tank backward")
    print("  - Left Arrow: Turn tank left")
    print("  - Right Arrow: Turn tank right")
    print("  - ESC Key: Exit the program")
    print("\n----------------------------------------------------------------")

def main():
    show_controls()
    
    if not glfw.init():
        return

    display = (800, 600)
    window = glfw.create_window(display[0], display[1], "OpenGL Tank - GLFW", None, None)
    
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1) # V-Sync para limitar FPS

    # Configuración inicial de OpenGL
    gluPerspective(45, display[0] / display[1], 0.1, 90)
    glTranslatef(0, 0, -10)
    glRotatef(35, 1, 0, 0)
    glEnable(GL_DEPTH_TEST)

    grid = draw_grid()

    # =================== ESTADO ====================
    x = y = z = 0.0
    grid_mov_x = grid_mov_z = 0.0
    model_angle = 180.0
    target_angle = 180.0
    rotation_speed = 3.0
    direction = 'front'
    new_direction = 'front'
    rotating = False
    scale = 1.0
    sc_y = 0.0

    DIRECTION_ANGLE = {
        'front': 180,
        'right': 90,
        'back': 0,
        'left': 270
    }

    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        # Cálculo de DT (Delta Time)
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time

        glfw.poll_events()

        # Gestión de entrada (Input)
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)
        
        temp_direction = direction
        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            new_direction = 'front'
        elif glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            new_direction = 'back'
        elif glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
            new_direction = 'left'
        elif glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
            new_direction = 'right'

        if new_direction != direction:
            target_angle = DIRECTION_ANGLE[new_direction]
            rotating = True
            grid_mov_x = grid_mov_z = 0.0

        # ================= GIRO SUAVE =================
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
            if direction in ['front', 'back']:
                grid_mov_x = math.sin(rad) * 0.05
                grid_mov_z = -math.cos(rad) * 0.05
            else:
                grid_mov_x = -math.sin(rad) * 0.05
                grid_mov_z = math.cos(rad) * 0.05

        x += grid_mov_x
        z += grid_mov_z

        # ===== RENDER =====
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glScalef(scale, scale, scale)
        glRotatef(sc_y, 0, 1, 0)
        glTranslatef(x, y, z)

        glCallList(grid)
        glPopMatrix()

        glfw.swap_buffers(window)

    glDeleteLists(grid, 1)
    glfw.terminate()

if __name__ == "__main__":
    main()

