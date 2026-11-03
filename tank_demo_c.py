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
glTranslatef(0.0, 0.0, -10.0)
#glEnable(GL_DEPTH_TEST)
glRotatef(35.0, 1.0, 0.0, 0.0)

glMatrixMode(GL_MODELVIEW)

def load_obj(path):
    vertices, faces = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if not parts or parts[0].startswith("#"):
                continue
            if parts[0] == "v":
                vertices.append([float(x) for x in parts[1:4]])
            elif parts[0] == "f":
                idx = []
                for token in parts[1:]:
                    i = int(token.split("/")[0])
                    idx.append(i - 1 if i > 0 else len(vertices) + i)
                faces.append(idx)

    return np.array(vertices, dtype=np.float32), faces 

def create_grid():
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

def build_flat_mesh(vertices, faces):
    tri = triangulate(faces).reshape(-1,3)
    tri_pos = vertices[tri]                                   # (T, 3, 3)
    n = np.cross(tri_pos[:, 1] - tri_pos[:, 0], tri_pos[:, 2] - tri_pos[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    positions = tri_pos.reshape(-1, 3).astype(np.float32)
    normals = np.repeat(n, 3, axis=0).astype(np.float32)
    return positions, normals

def triangulate(faces):
    """Abanico: [a, b, c, d] -> (a, b, c) + (a, c, d). Válido para caras convexas."""
    tris = []
    for face in faces:
        for k in range(1, len(face) - 1):
            tris += [face[0], face[k], face[k + 1]]
    return np.array(tris, dtype=np.uint32)

# GRID
line_vbo, line_count = create_grid()

# CARGA DE ARCHIVOS OBJ
base = os.path.dirname(__file__)
obj_base = os.path.join(base, "tanque", "resto_tanque.obj")
vertices, faces = load_obj(obj_base)
positions, normals = build_flat_mesh(vertices, faces)


glLineWidth(1.0)
angle = 0.0
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    #glClearColor(0.2, 0.4, 0.8, 1.0)  # color fondo
    glClear(GL_COLOR_BUFFER_BIT)

    # Cámara: alejada, inclinada hacia abajo y girando despacio
    glLoadIdentity()
    #glTranslatef(0.0, 0.0, -25.0)
    #glRotatef(30.0, 1, 0, 0)
    glRotatef(angle, 0, 1, 0)
    angle += 0.3

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

