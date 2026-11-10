import numpy as np
import pygame
from pygame.locals import * #DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective
import os
import time

# DIMENSIONES DEL GRID
grid_size = 20
grid_spacing = 1


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


def triangulate(faces):
    """Abanico: [a, b, c, d] -> (a, b, c) + (a, c, d). Válido para caras convexas."""
    tris = []
    for face in faces:
        for k in range(1, len(face) - 1):
            tris += [face[0], face[k], face[k + 1]]
    return np.array(tris, dtype=np.uint32)


def build_flat_mesh(vertices, faces):
    tri = triangulate(faces).reshape(-1, 3)
    tri_pos = vertices[tri]                                   # (T, 3, 3)
    n = np.cross(tri_pos[:, 1] - tri_pos[:, 0], tri_pos[:, 2] - tri_pos[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    positions = tri_pos.reshape(-1, 3).astype(np.float32)
    normals = np.repeat(n, 3, axis=0).astype(np.float32)
    return positions, normals


def upload(array):
    """Sube un array NumPy a un VBO y devuelve su identificador."""
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)
    return vbo


def create_grid():
    line_data = []
    for x in range(-grid_size, grid_size + 1, grid_spacing):
        line_data += [x, 0, -grid_size, x, 0, grid_size]
    for z in range(-grid_size, grid_size + 1, grid_spacing):
        line_data += [-grid_size, 0, z, grid_size, 0, z]
    line_vertices = np.array(line_data, dtype=np.float32)
    return upload(line_vertices), len(line_vertices) // 3

def draw_model(pos_vbo,nrm_vbo,m_count):
    glEnable(GL_LIGHTING)
    glEnableClientState(GL_NORMAL_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, pos_vbo)
    glVertexPointer(3, GL_FLOAT, 0, None)
    glBindBuffer(GL_ARRAY_BUFFER, nrm_vbo)
    glNormalPointer(GL_FLOAT, 0, None)
    glDrawArrays(GL_TRIANGLES, 0, m_count)


if __name__ == "__main__":
    pygame.init()
    display = (800, 600)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
    #pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1) #antialiasing
    #pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 6)         #antialiasing

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    #glEnable(GL_MULTISAMPLE)                                          #antialiasing
    #glEnable(GL_LINE_SMOOTH)                                          #antialiasing
    #glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)                            #antialiasing

    # PROYECCIÓN: solo la perspectiva
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50, display[0] / display[1], 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    glClearColor(0.2, 0.4, 0.8, 1.0)   # fondo azul
    glEnable(GL_DEPTH_TEST)

    # LUZ (solo se activa mientras se dibuja el modelo)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.30, 0.30, 0.30, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.85, 0.85, 0.85, 1.0))
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # GRID
    line_vbo, line_count = create_grid()

    # MODELOS OBJ -----------------------------------------------------------------------------------------
    base = os.path.dirname(os.path.abspath(__file__))

    # RESTO TANQUE
    obj_base = os.path.join(base, "tanque", "resto_tanque.obj")
    vertices, faces = load_obj(obj_base)
    positions, normals = build_flat_mesh(vertices, faces)
    model_pos_vbo = upload(positions)
    model_nrm_vbo = upload(normals)
    model_count = len(positions)
    ground = -float(vertices[:, 1].min()) + 0.01   # sube el modelo para que su base apoye sobre el grid
    
    # TORRE2
    obj_base2 = os.path.join(base, "tanque", "torre2.obj")
    vertices, faces = load_obj(obj_base2)
    positions, normals = build_flat_mesh(vertices, faces)
    model_pos_vbo2 = upload(positions)
    model_nrm_vbo2 = upload(normals)
    model_count2 = len(positions)

    # ------------------------------------------------------------------------------------------------------

    angle = 0.0
    clock = pygame.time.Clock()
    last_time = time.perf_counter()
    rotating = True
    tower_y_rot = 0.0

    running = True
    while running:
        now = time.perf_counter()
        dt = min(now - last_time, 0.05)
        last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_s:
                    rotating = not rotating

                elif event.key == pygame.K_b:
                    tower_y_rot = 0.0

        keys = pygame.key.get_pressed()
            
        if keys[K_m]:
            tower_y_rot += 40.0 * dt
        elif keys[K_n]:
            tower_y_rot -= 40.0 * dt

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # CÁMARA: alejar, inclinar y luego girar la escena
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -10.0)
        glRotatef(35.0, 1.0, 0.0, 0.0)
        glLightfv(GL_LIGHT0, GL_POSITION, (0.3, 1.0, 0.5, 0.0))   # luz fija en el mundo
        glRotatef(angle, 0, 1, 0)
 
        if rotating:
            angle += 15.0 * dt
        else:
            angle += 0.0

        # --- GRID (sin iluminación) ---
        glDisable(GL_LIGHTING)
        glEnableClientState(GL_VERTEX_ARRAY)
        glColor3f(1.0, 1.0, 1.0)
        glBindBuffer(GL_ARRAY_BUFFER, line_vbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawArrays(GL_LINES, 0, line_count)

        # --- MODELOS (relleno, iluminado) ---

        '''# RESTO TANAQUE
        glEnable(GL_LIGHTING)
        glEnableClientState(GL_NORMAL_ARRAY)
        glPushMatrix()
        glTranslatef(0.0, ground, 0.0)     # apoya el modelo sobre el grid
        glColor3f(0.35, 0.65, 0.35)
        glBindBuffer(GL_ARRAY_BUFFER, model_pos_vbo)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, model_nrm_vbo)
        glNormalPointer(GL_FLOAT, 0, None)
        glDrawArrays(GL_TRIANGLES, 0, model_count)
        # TORRE2
        glPushMatrix()
        #glTranslatef(0.0, ground, 0.0)     # apoya el modelo sobre el grid
        #glColor3f(0.35, 0.65, 0.35)
        glBindBuffer(GL_ARRAY_BUFFER, model_pos_vbo2)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, model_nrm_vbo2)
        glNormalPointer(GL_FLOAT, 0, None)
        glDrawArrays(GL_TRIANGLES, 0, model_count2)
        glPopMatrix()

        glPopMatrix()'''
        
        # ----------- SUSTITUYE A BLOQUE DE ARRIBA -----------
        glPushMatrix()
        glTranslatef(0.0, ground, 0.0) 
        glColor3f(0.35, 0.65, 0.35)
        draw_model(model_pos_vbo,model_nrm_vbo,model_count)
        glPushMatrix()
        glRotatef(tower_y_rot, 0.0, 1.0, 0.0)
        draw_model(model_pos_vbo2,model_nrm_vbo2,model_count2)
        glPopMatrix()
        glPopMatrix()
        # ----------------------------------------------------

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

        pygame.display.flip()
        clock.tick(60)

    glDeleteBuffers(5, [line_vbo, model_pos_vbo, model_nrm_vbo, model_pos_vbo2, model_nrm_vbo2])
    pygame.quit()
