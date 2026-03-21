# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os
import time


# ================= GRID =================
grid_size = 110
grid_spacing = 1

# ================= VELOCIDADES (unidades por segundo) =================
TANK_SPEED        = 3.0    # velocidad de traslación del tanque
STOP_DECEL        = 6.0    # desaceleración al frenar (unidades/s²)
CAM_ROT_SPEED     = 30.0   # grados/s para rotar escena (T/R)
CAM_TILT_SPEED    = 15.0   # grados/s para inclinar cámara (F/G)
CAM_Y_SPEED       = 6.0    # unidades/s para subir/bajar cámara (P/O)
TURRET_SPEED      = 60.0   # grados/s para girar torreta (N/M)
SCALE_SPEED       = 1.2    # escala/s para zoom (Z/X)
BULLET_SPEED      = 30.0   # unidades/s para las balas
ANIM_SCALE_SPEED  = 0.6
ANIM_ROT_SPEED    = 60.0
ANIM_ROT_Y_SPEED  = 30.0
ANIM_ROT_X_SPEED  = 6.0
ANIM_TOWER_SPEED  = 60.0
ANIM_SCALE_DOWN   = 0.6


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
    face_indices = []
    faces = []
    vertices = []
    edges = set()
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v '):
                parts = line.strip().split()
                vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                vertices.append(vertex)
            elif line.startswith('f '):
                parts = line.strip().split()
                face_indices = [int(part) - 1 for part in parts[1:]]
                faces.append(face_indices)
                for i in range(len(face_indices)):
                    edges.add(tuple(sorted((face_indices[i], face_indices[(i + 1) % len(face_indices)]))))

    return vertices, edges, faces


def draw_model(path):
    # HABILITAR TRANSPARENCIA
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    model_name = os.path.basename(path)
    v, e, f = load_object(path)

    if model_name == 'bullet.obj':
        glColor4f(0.0, 1.0, 0.0, 0.5)
        glLineWidth(1.0)
    else:
        glColor3f(1.0, 0.0, 0.0)
        glLineWidth(2.0)

    glBegin(GL_LINES)
    for a, b in e:
        glVertex3f(*v[a])
        glVertex3f(*v[b])
    glEnd()

    glBegin(GL_QUADS)
    if model_name != 'bullet.obj':
        glColor3f(0.1, 0.1, 0.1)
    else:
        glColor4f(0.0, 1.0, 0.0, 0.1)
    for face in f:
        for vertex in face:
            glVertex3fv(v[vertex])
    glEnd()


def setup_view_ortho(display):
    glMatrixMode(GL_PROJECTION)
    aspect_ratio = display[0] / display[1]
    ortho_size = 10
    glOrtho(-ortho_size * 0.5 * aspect_ratio, ortho_size * 0.5 * aspect_ratio,
            -ortho_size * 0.5, ortho_size * 0.5, -50, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def setup_view_perspective(display):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50, (display[0] / display[1]), 0.1, 80)
    glMatrixMode(GL_MODELVIEW)


def show_controls():
    print("\n--------------------- Controls ---------------------")

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
    print("  - C Key: Stop tank movement (braking)")
    print("  - L Key: Reset entire scene")
    print("  - ESC Key: Exit the program")

    print("\n----------------------------------------------------")


def draw_text(font, x, y, text):
    textSurface = font.render(text, True, (0, 255, 0), (0, 0, 0))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, textData)


# ================= MAIN =================
def main():
    show_controls()
    pygame.init()
    display = (800, 600)

    font = pygame.font.SysFont('arial', 15)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, display[0] / display[1], 0.1, 90)
    glTranslatef(0, 0, -10)
    glEnable(GL_DEPTH_TEST)

    base       = os.path.dirname(__file__)
    obj_base   = os.path.join(base, "tanque", "resto_tanque.obj")
    obj_tower  = os.path.join(base, "tanque", "torre.obj")
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
    x = y = z = 0.0
    vel_x = vel_z = 0.0          # velocidad actual en unidades/segundo
    last_cam_pos_x = last_cam_pos_z = 0.0
    ortographic = False

    hide_info = False

    act_anim     = False
    act_anim2    = False
    act_anim3    = False
    act_anim4    = False
    act_anim5    = False
    cen_counter  = 0.0
    dest_scale   = 0.81
    dest_rot_y   = -152.0
    dest_y_tower = 62.0
    dest_rot_x   = 0.50

    model_angle = 180
    y_tower     = 0.0
    rot_x       = 35.0
    rot_y       = 0.0
    stop_camera = False
    scale       = 1.00
    direction   = 'front'
    braking     = False   # True mientras se aplica frenada progresiva

    bullets = []

    # ===== Delta time =====
    clock = pygame.time.Clock()
    last_time = time.perf_counter()

    running = True
    while running:

        # --- Delta time ---
        now = time.perf_counter()
        dt  = min(now - last_time, 0.05)   # clamp a 50 ms para evitar saltos
        last_time = now

        for e in pygame.event.get():
            if e.type == QUIT:
                running = False

            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    running = False

                elif e.key == K_0 and (e.mod & KMOD_ALT):
                    glLoadIdentity()
                    gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
                    rot_x = 0.0
                    scale = 0.39
                    glTranslatef(0.0, 0.0, -10.0)
                    glRotatef(90.0, 1.0, 0.0, 0.0)

                elif e.key == K_1 and (e.mod & KMOD_ALT):
                    glLoadIdentity()
                    gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
                    glTranslatef(0.0, 0.0, -10.0)
                    rot_x = 90
                    scale = 0.39
                    dest_scale = 0.81
                    act_anim = True
                    dest_rot_x = 1.0
                    cen_counter = 0.0

                elif e.key == K_2 and (e.mod & KMOD_ALT):
                    act_anim2 = True

                elif e.key == K_3 and (e.mod & KMOD_ALT):
                    act_anim3 = True
                    dest_rot_x = 6.3
                    braking = True   # frenar al iniciar esta animación

                elif e.key == K_4 and (e.mod & KMOD_ALT):
                    act_anim4 = True

                elif e.key == K_5 and (e.mod & KMOD_ALT):
                    act_anim5 = True
                    vel_x = -TANK_SPEED
                    vel_z = 0.0
                    model_angle = 90
                    direction   = 'right'
                    rot_x       = 18.5000
                    scale       = 2.92

                elif e.key == K_UP:
                    vel_z       =  TANK_SPEED
                    vel_x       = 0.0
                    model_angle = 180
                    direction   = 'front'
                    braking     = False

                elif e.key == K_DOWN:
                    vel_z       = -TANK_SPEED
                    vel_x       = 0.0
                    model_angle = 0
                    direction   = 'back'
                    braking     = False

                elif e.key == K_LEFT:
                    vel_x       =  TANK_SPEED
                    vel_z       = 0.0
                    model_angle = -90
                    direction   = 'left'
                    braking     = False

                elif e.key == K_RIGHT:
                    vel_x       = -TANK_SPEED
                    vel_z       = 0.0
                    model_angle = 90
                    direction   = 'right'
                    braking     = False

                elif e.key == K_b:
                    y_tower = 0.0

                elif e.key == K_v:
                    y_tower = 180

                elif e.key == K_c:
                    braking = True   # activar frenada progresiva

                elif e.key == K_j:
                    hide_info = not hide_info

                elif e.key == K_s:
                    stop_camera = not stop_camera

                elif e.key == K_l:
                    x = y = z = 0.0
                    vel_x = vel_z = 0.0
                    braking     = False
                    model_angle = 180
                    y_tower     = 0.0
                    rot_x       = 0.0
                    rot_y       = 0.0
                    scale       = 1.0
                    direction   = 'front'
                    stop_camera = False
                    glLoadIdentity()
                    gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
                    glTranslatef(0.0, 0.0, -10)
                    glRotatef(35.0, 1.0, 0.0, 0.0)

                # ===== DISPARO =====
                elif e.key == K_y:
                    rot = model_angle + y_tower
                    rad = math.radians(rot)
                    bx  = -x + math.sin(rad) * 2.2
                    bz  = -z + math.cos(rad) * 2.2
                    bullets.append({
                        "pos": [bx, 0.2, bz],
                        "dir": [math.sin(rad), 0.0, math.cos(rad)]
                    })

        keys = pygame.key.get_pressed()

        # ===== Teclas mantenidas (escala por dt) =====
        if keys[K_t]:
            rot_y += CAM_ROT_SPEED * dt
        elif keys[K_r]:
            rot_y -= CAM_ROT_SPEED * dt

        if keys[K_f]:
            rot_x += CAM_TILT_SPEED * dt
        elif keys[K_g]:
            rot_x -= CAM_TILT_SPEED * dt

        if keys[K_p]:
            y += CAM_Y_SPEED * dt
        elif keys[K_o]:
            y -= CAM_Y_SPEED * dt

        if direction == 'front' or direction == 'right':
            if keys[pygame.K_n]:
                y_tower += TURRET_SPEED * dt
            elif keys[pygame.K_m]:
                y_tower -= TURRET_SPEED * dt
        elif direction == 'back' or direction == 'left':
            if keys[pygame.K_n]:
                y_tower -= TURRET_SPEED * dt
            elif keys[pygame.K_m]:
                y_tower += TURRET_SPEED * dt

        if keys[K_z]:
            scale += SCALE_SPEED * dt
        elif keys[K_x]:
            scale -= SCALE_SPEED * dt

        # ===== ACTUALIZACIÓN =====

        # -------------- animaciones (escala por dt) --------------
        if act_anim:
            if scale < dest_scale:
                scale += ANIM_SCALE_SPEED * dt
            elif rot_x > dest_rot_x:
                rot_x -= ANIM_ROT_SPEED * dt
            else:
                act_anim = False

        if act_anim2:
            if rot_y > dest_rot_y:
                rot_y -= ANIM_ROT_Y_SPEED * dt
            else:
                act_anim2 = False

        if act_anim3:
            if rot_x < dest_rot_x:
                rot_x += ANIM_ROT_X_SPEED * dt
            else:
                act_anim3 = False

        if act_anim4:
            if y_tower < dest_y_tower:
                y_tower += ANIM_TOWER_SPEED * dt
            else:
                act_anim4 = False

        if act_anim5:
            if scale > 1.0:
                scale -= ANIM_SCALE_DOWN * dt
            else:
                act_anim5 = False
        # ---------------------------------------------------------

        # ===== FRENADA PROGRESIVA (desaceleración por dt) =====
        if braking:
            decel = STOP_DECEL * dt
            if direction in ('front', 'back'):
                if vel_z > 0.0:
                    vel_z = max(0.0, vel_z - decel)
                elif vel_z < 0.0:
                    vel_z = min(0.0, vel_z + decel)
                if vel_z == 0.0:
                    braking = False
            else:
                if vel_x > 0.0:
                    vel_x = max(0.0, vel_x - decel)
                elif vel_x < 0.0:
                    vel_x = min(0.0, vel_x + decel)
                if vel_x == 0.0:
                    braking = False

        # ===== Integrar posición =====
        x += vel_x * dt
        z += vel_z * dt

        if not stop_camera:
            last_cam_pos_x = x
            last_cam_pos_z = z

        # ===== LIMITAR MOVIMIENTO DENTRO DEL GRID =====
        if x - 2 < (-grid_size - 0.1) or x + 2 > (grid_size + 0.1):
            vel_x = 0.0
            if direction == 'left':
                x -= 0.1
            elif direction == 'right':
                x += 0.1
        elif z - 2 < (-grid_size - 0.1) or z + 2 > (grid_size + 0.1):
            vel_z = 0.0
            if direction == 'front':
                z -= 0.1
            elif direction == 'back':
                z += 0.1

        for b in bullets:
            b["pos"][0] += b["dir"][0] * BULLET_SPEED * dt
            b["pos"][2] += b["dir"][2] * BULLET_SPEED * dt

        # ===== RENDER =====
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glScalef(scale, scale, scale)
        glRotatef(rot_x, 1.0, 0.0, 0.0)
        glRotatef(rot_y, 0.0, 1.0, 0.0)
        if not stop_camera:
            glTranslatef(x, y, z)
        else:
            glTranslatef(last_cam_pos_x, y, last_cam_pos_z)

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

        if not hide_info:
            draw_text(font, 10, 570, f'CAMERA MOV: {not stop_camera}')
            draw_text(font, 10, 553, f'DIRECTION: {direction}')
            draw_text(font, 10, 536, f'X: {x:.4f}')
            draw_text(font, 10, 519, f'Y: {y:.4f}')
            draw_text(font, 10, 502, f'Z: {z:.4f}')
            draw_text(font, 10, 485, f'VEL X: {vel_x:.4f}')
            draw_text(font, 10, 468, f'VEL Z: {vel_z:.4f}')
            draw_text(font, 10, 451, f'BRAKING: {braking}')
            draw_text(font, 10, 434, f'ROT X: {rot_x:.4f}')
            draw_text(font, 10, 417, f'ROT Y: {rot_y:.2f}')
            draw_text(font, 10, 400, f'TOWER ROT: {y_tower:.4f}')
            draw_text(font, 10, 383, f'SCALE: {scale:.2f}')
            draw_text(font, 10, 366, f'FPS: {clock.get_fps():.0f}')

        pygame.display.flip()
        clock.tick(0)   # sin límite de FPS; el vsync del driver limita naturalmente

    glDeleteLists(grid, 1)
    glDeleteLists(model_base, 1)
    glDeleteLists(model_tower, 1)
    glDeleteLists(model_bullet, 1)
    pygame.quit()


main()
