# -*- coding: utf-8 -*-
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image, ImageDraw, ImageFont
import math
import os
import numpy as np

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
    print("  - C Key: Brake (progressive stop)")
    print("  - L Key: Reset entire scene")
    print("  - ESC Key: Exit the program")
    print("\n----------------------------------------------------")


# ================= TEXT RENDERING (Pillow) =================

_text_texture_cache = {}
_text_texture_ids = []


def _make_text_texture(text, font_size=15):
    key = (text, font_size)
    if key in _text_texture_cache:
        return _text_texture_cache[key]

    try:
        pil_font = ImageFont.truetype("Fixed.ttf", font_size)#("DejaVuSansMono.ttf", font_size)
    except (IOError, OSError):
        try:
            pil_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", font_size)
        except (IOError, OSError):
            pil_font = ImageFont.load_default()

    dummy = Image.new("RGBA", (1, 1))
    draw_dummy = ImageDraw.Draw(dummy)
    bbox = draw_dummy.textbbox((0, 0), text, font=pil_font)
    w = bbox[2] - bbox[0] + 10
    h = bbox[3] - bbox[1] + 10

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((2, 2), text, font=pil_font, fill=(0, 255, 0, 255))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.array(img, dtype=np.uint8)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glBindTexture(GL_TEXTURE_2D, 0)

    _text_texture_cache[key] = (tex_id, w, h)
    _text_texture_ids.append(tex_id)
    return tex_id, w, h


def draw_text(x, y, text, font_size=15):
    tex_id, w, h = _make_text_texture(text, font_size)

    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    viewport = glGetIntegerv(GL_VIEWPORT)
    win_w, win_h = viewport[2], viewport[3]
    glOrtho(0, win_w, 0, win_h, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(1.0, 1.0, 1.0, 1.0)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x,     y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x,     y + h)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glPopAttrib()


# ================= MAIN =================
def main():
    show_controls()

    if not glfw.init():
        raise RuntimeError("No se pudo inicializar GLFW")

    display = (800, 600)
    window = glfw.create_window(display[0], display[1], "Tank Simulator", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("No se pudo crear la ventana GLFW")

    glfw.make_context_current(window)
    glfw.swap_interval(1)  # vsync

    # ===== Estado de teclado =====
    keys_pressed   = set()
    keys_just_down = set()

    def key_callback(win, key, scancode, action, mods):
        if action == glfw.PRESS:
            keys_pressed.add(key)
            keys_just_down.add((key, mods))
        elif action == glfw.RELEASE:
            keys_pressed.discard(key)

    glfw.set_key_callback(window, key_callback)

    # ===== OpenGL inicial =====
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

    hide_info    = False
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

    model_angle  = 180
    y_tower      = 0.0
    rot_x        = 35.0
    rot_y        = 0.0
    stop_camera  = False
    scale        = 1.00
    direction    = 'front'
    braking      = False   # True mientras se aplica frenada progresiva

    bullets = []

    # ===== Delta time =====
    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # --- Delta time ---
        now = glfw.get_time()
        dt  = min(now - last_time, 0.05)   # clamp a 50 ms para evitar saltos
        last_time = now

        # ===== KEYDOWN (pulsación única) =====
        current_just_down = keys_just_down.copy()
        keys_just_down.clear()

        for (key, mods) in current_just_down:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)

            elif key == glfw.KEY_0 and (mods & glfw.MOD_ALT):
                glLoadIdentity()
                gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
                rot_x = 0.0
                scale = 0.39
                glTranslatef(0.0, 0.0, -10.0)
                glRotatef(90.0, 1.0, 0.0, 0.0)

            elif key == glfw.KEY_1 and (mods & glfw.MOD_ALT):
                glLoadIdentity()
                gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
                glTranslatef(0.0, 0.0, -10.0)
                rot_x = 90.0
                scale = 0.39
                dest_scale = 0.81
                act_anim = True
                dest_rot_x = 1.0
                cen_counter = 0.0

            elif key == glfw.KEY_2 and (mods & glfw.MOD_ALT):
                act_anim2 = True

            elif key == glfw.KEY_3 and (mods & glfw.MOD_ALT):
                act_anim3 = True
                dest_rot_x = 6.3
                braking = True   # frenar al iniciar esta animación

            elif key == glfw.KEY_4 and (mods & glfw.MOD_ALT):
                act_anim4 = True

            elif key == glfw.KEY_5 and (mods & glfw.MOD_ALT):
                act_anim5 = True
                vel_x = -TANK_SPEED
                vel_z = 0.0
                model_angle = 90
                direction   = 'right'
                rot_x       = 18.5
                scale       = 2.92

            elif key == glfw.KEY_UP:
                vel_z       =  TANK_SPEED
                vel_x       = 0.0
                model_angle = 180
                direction   = 'front'
                braking     = False

            elif key == glfw.KEY_DOWN:
                vel_z       = -TANK_SPEED
                vel_x       = 0.0
                model_angle = 0
                direction   = 'back'
                braking     = False

            elif key == glfw.KEY_LEFT:
                vel_x       =  TANK_SPEED
                vel_z       = 0.0
                model_angle = -90
                direction   = 'left'
                braking     = False

            elif key == glfw.KEY_RIGHT:
                vel_x       = -TANK_SPEED
                vel_z       = 0.0
                model_angle = 90
                direction   = 'right'
                braking     = False

            elif key == glfw.KEY_B:
                y_tower = 0.0

            elif key == glfw.KEY_V:
                y_tower = 180.0

            elif key == glfw.KEY_C:
                braking = True   # activar frenada progresiva

            elif key == glfw.KEY_J:
                hide_info = not hide_info

            elif key == glfw.KEY_S:
                stop_camera = not stop_camera

            elif key == glfw.KEY_L:
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

            elif key == glfw.KEY_Y:
                rot = model_angle + y_tower
                rad = math.radians(rot)
                bx  = -x + math.sin(rad) * 2.2
                bz  = -z + math.cos(rad) * 2.2
                bullets.append({
                    "pos": [bx, 0.2, bz],
                    "dir": [math.sin(rad), 0.0, math.cos(rad)]
                })

        # ===== Teclas mantenidas (escala por dt) =====
        if glfw.KEY_T in keys_pressed:
            rot_y += CAM_ROT_SPEED * dt
        elif glfw.KEY_R in keys_pressed:
            rot_y -= CAM_ROT_SPEED * dt

        if glfw.KEY_F in keys_pressed:
            rot_x += CAM_TILT_SPEED * dt
        elif glfw.KEY_G in keys_pressed:
            rot_x -= CAM_TILT_SPEED * dt

        if glfw.KEY_P in keys_pressed:
            y += CAM_Y_SPEED * dt
        elif glfw.KEY_O in keys_pressed:
            y -= CAM_Y_SPEED * dt

        if direction in ('front', 'right'):
            if glfw.KEY_N in keys_pressed:
                y_tower += TURRET_SPEED * dt
            elif glfw.KEY_M in keys_pressed:
                y_tower -= TURRET_SPEED * dt
        elif direction in ('back', 'left'):
            if glfw.KEY_N in keys_pressed:
                y_tower -= TURRET_SPEED * dt
            elif glfw.KEY_M in keys_pressed:
                y_tower += TURRET_SPEED * dt

        if glfw.KEY_Z in keys_pressed:
            scale += SCALE_SPEED * dt
        elif glfw.KEY_X in keys_pressed:
            scale -= SCALE_SPEED * dt

        # ===== Animaciones (escala por dt) =====
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

        # ===== Frenada progresiva (desaceleración por dt) =====
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

        # ===== Limitar movimiento dentro del grid =====
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

        # ===== Actualizar balas =====
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

        # ===== Tanque =====
        glPushMatrix()
        glTranslatef(-x, 0.2, -z)
        glRotatef(model_angle, 0, 1, 0)

        glPushMatrix()
        glRotatef(y_tower, 0, 1, 0)
        glCallList(model_tower)
        glPopMatrix()

        glCallList(model_base)
        glPopMatrix()

        # ===== Balas =====
        for b in bullets:
            glPushMatrix()
            glTranslatef(b["pos"][0], b["pos"][1], b["pos"][2])
            ang = math.degrees(math.atan2(b["dir"][0], b["dir"][2]))
            glRotatef(ang, 0, 1, 0)
            glCallList(model_bullet)
            glPopMatrix()

        glPopMatrix()

        # ===== HUD =====
        if not hide_info:
            draw_text(10, 570, f'CAMERA MOV: {not stop_camera}')
            draw_text(10, 553, f'DIRECTION: {direction}')
            draw_text(10, 536, f'X: {x:.4f}')
            draw_text(10, 519, f'Y: {y:.4f}')
            draw_text(10, 502, f'Z: {z:.4f}')
            draw_text(10, 485, f'VEL X: {vel_x:.4f}')
            draw_text(10, 468, f'VEL Z: {vel_z:.4f}')
            draw_text(10, 451, f'BRAKING: {braking}')
            draw_text(10, 434, f'ROT X: {rot_x:.4f}')
            draw_text(10, 417, f'ROT Y: {rot_y:.2f}')
            draw_text(10, 400, f'TOWER ROT: {y_tower:.4f}')
            draw_text(10, 383, f'SCALE: {scale:.2f}')
            draw_text(10, 366, f'FPS: {1.0/dt:.0f}' if dt > 0 else 'FPS: --')

        glfw.swap_buffers(window)

    # ===== Limpieza =====
    glDeleteLists(grid, 1)
    glDeleteLists(model_base, 1)
    glDeleteLists(model_tower, 1)
    glDeleteLists(model_bullet, 1)

    if _text_texture_ids:
        glDeleteTextures(len(_text_texture_ids), _text_texture_ids)

    glfw.destroy_window(window)
    glfw.terminate()


main()
