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

def draw_text(font, x, y, text):
    textSurface = font.render(text, True, (0, 255, 0), (0, 0, 0))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def show_controls():
    print("\n--------------------------- Controls ---------------------------")

    print("\nKeyboard Controls (Tank Movement):")
    print("  - Up Arrow: Move tank forward")
    print("  - Down Arrow: Move tank backward")
    print("  - Left Arrow: Turn tank left")
    print("  - Right Arrow: Turn tank right")

    print("\nTurret Controls:")
    print("  - N Key: Rotate turret clockwise")
    print("  - M Key: Rotate turret counterclockwise")
    print("  - B Key: Reset turret rotation")

    print("\nShooting Controls:")
    print("  - Y Key: Fire bullet")

    print("\nScene / Camera Controls:")
    print("  - T Key: Rotate scene clockwise around Y-axis")
    print("  - R Key: Rotate scene counterclockwise around Y-axis")
    print("  - F Key: Tilt camera downward")
    print("  - G Key: Tilt camera upward")
    print("  - S Key: Lock / unlock camera movement")

    print("\nScale Controls:")
    print("  - Z Key: Increase scale")
    print("  - X Key: Decrease scale")

    print("\nOther Controls")
    print("  - C Key: Stop tank movement")
    print("  - L Key: Reset entire scene")
    print("  - J Key: Toggle between acritive / inactive camera movement")
    print("  - ESC Key: Exit the program")

    print("\n----------------------------------------------------------------")

def main():
    show_controls()
    pygame.init()
    display = (800, 600)
    clock = pygame.time.Clock()################

    font = pygame.font.SysFont('arial',15)

    # ========================== ANTIALIASING ========================
    #pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    #pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 6)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    #glEnable(GL_MULTISAMPLE)
    #glEnable(GL_LINE_SMOOTH)
    #glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    # ================================================================

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

    hide_text = False
    #stop_camera = False
    
    scale = 1.0

    sc_y = 0.0

    DIRECTION_ANGLE = {
        'front': 180,
        'right': 90,
        'back': 0,
        'left': 270
    }
 

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
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


        #keys = pygame.key.get_pressed()
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
            if direction == 'front' or direction == 'back':
                rad = math.radians(model_angle)
                grid_mov_x = math.sin(rad) * 0.05
                grid_mov_z = -math.cos(rad) * 0.05
            else:
                rad = math.radians(model_angle)
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

        pygame.display.flip()

    pygame.quit()


main()


