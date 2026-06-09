# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os
import time
import argparse

#antena_rotor2.obj
#base_antena2.obj 

# ================= GRID =================
grid_size = 110
grid_spacing = 1


def draw_grid(floor):
    grid_list = glGenLists(1)
    glNewList(grid_list, GL_COMPILE)
    
    if floor:

        # HABILITAR TRANSPARENCIA
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glDepthMask(GL_FALSE)######################

        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(0.9,0.9)

        glBegin(GL_QUADS)
        glColor4f(0.1,0.2,0.4,0.2)
        glVertex3f(-grid_size,0,-grid_size)
        glVertex3f(grid_size,0,-grid_size)
        glVertex3f(grid_size, 0, grid_size)
        glVertex3f(-grid_size, 0, grid_size)
        glEnd()
        glDisable(GL_POLYGON_OFFSET_FILL)

        glDepthMask(GL_TRUE)#######################
        glDisable(GL_BLEND)########################

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
    #glColor3f(0.0,1.0,0.0) if model_name == 'bullet.obj' else glColor3f(1.0,0.0,0.0), glLineWidth(2.0)

    if model_name == 'bullet.obj':
        glColor4f(0.0,1.0,0.0,0.5)
        glLineWidth(1.0)
        #glDisable(GL_BLEND)
    else:
        glColor3f(1.0,0.0,0.0)
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
    #glLoadIdentity()
    aspect_ratio = display[0] / display[1]
    ortho_size = 10
    glOrtho(-ortho_size * 0.5 * aspect_ratio, ortho_size * 0.5 * aspect_ratio, -ortho_size * 0.5, ortho_size * 0.5, -50, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def setup_view_perspective(display):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50, (display[0] / display[1]), 0.1, 80)#50.0)
    glMatrixMode(GL_MODELVIEW)
    #glLoadIdentity()
    #glTranslatef(0.0, 0.0, -10.0)

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
    print("  - C Key: Stop tank movement")
    print("  - L Key: Reset entire scene")
    print("  - ESC Key: Exit the program")

    print("\n----------------------------------------------------")

def draw_text(font, x, y, text):
    textSurface = font.render(text, True, (0, 255, 0), (0, 0, 0))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

'''def stop_movement(direction):
    stop_rate_z = 0.0000
    stop_rate_x = 0.0000
    if direction == 'front' or direction == 'back':
        stop_rate_z = 0.01
    elif direction == 'right' or direction == 'left':
        stop_rate_x = 0.01
    return stop_rate_x, stop_rate_z'''


# ================= MAIN LOOP =================
def main_loop(args):
    show_controls()
    pygame.init()
    display = (800, 600)
    #display = (1600, 900)
    floor = args.floor

    font = pygame.font.SysFont('arial',15)
    
    if args.antialiasing:

        # ========================== ANTIALIASING =========================
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 6)

        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

        glEnable(GL_MULTISAMPLE)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        # =================================================================

    else:
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)


    gluPerspective(45, display[0] / display[1], 0.1, 120)#90
    glTranslatef(0, 0, -10)
    #glRotatef(35, 1, 0, 0)#!
    glEnable(GL_DEPTH_TEST)

    base = os.path.dirname(__file__)
    obj_base = os.path.join(base, "tanque", "resto_tanque.obj")
    obj_tower = os.path.join(base, "tanque", "torre.obj")
    obj_bullet = os.path.join(base, "tanque", "bullet.obj")
    obj_base_antena = os.path.join(base, "tanque", "base_antena2.obj")
    obj_rotor_antena = os.path.join(base, "tanque", "antena_rotor2.obj")

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

    model_base_antena = glGenLists(1)
    glNewList(model_base_antena, GL_COMPILE)
    draw_model(obj_base_antena)
    glEndList()

    model_rotor_antena = glGenLists(1)
    glNewList(model_rotor_antena, GL_COMPILE)
    draw_model(obj_rotor_antena)
    glEndList()

    grid = draw_grid(floor)

    # ============== ESTADO ==============
    x = y = z = 0.0000                # desplazamiento del mundo
    grid_mov_x = grid_mov_z = 0.0000
    #stop_rate_x = stop_rate_z = 0.0000
    stop_rate = 2.0
    last_cam_pos_x = last_cam_pos_z = 0.0
    ortographic = False

    hide_info = False

    #------------------------------------------------------
    DIRECTION_ANGLE = {
        'front': 180,
        'right': 90,
        'back': 0,
        'left': 270
    }
    #------------------------------------------------------

    act_anim = False
    cen_counter = 0.0
    dest_scale = 0.81
    dest_rot_x = 1.0 #-88.5
    act_anim2 = False
    dest_rot_y = -152.0
    #dest_rot_x = -28.0
    act_anim3 = False
    act_anim4 = False
    dest_y_tower = 62.20
    act_anim5 = False
    act_anim7 = False

    model_angle = 180
    rot_x = 35.0 #0.0
    dest_rot_x = 0.50 #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ROT_X_SPEED = 15.0 #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    rot_y = 0.0
    stop_camera = False
    scale = 1.00

    #---------------------------------------
    rotating = False
    moving = False
    model_angle = 180.0
    target_angle = 180.0
    rotation_speed = 1.8 #3.0
    y_tower = 0.0
    direction = 'front'
    new_direction = 'front'
    braking = False
    resetting = False
    rotor_pos = 0.0
    #---------------------------------------

    bullets = []
    bullet_speed = 30.0 #0.2
    stop_init = False
    tank_speed = 3.0

    clock = pygame.time.Clock()
    last_time = time.perf_counter()

    running = True
    while running:
        now = time.perf_counter()
        dt = min(now - last_time, 0.05)
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
                    rot_x = 90  ############################
                    scale = 0.39
                    dest_scale = 0.81
                    act_anim = True
                    dest_rot_x = 1.0
                    cen_counter = 0.0
                    #glRotatef(90.0, 1.0, 0.0, 0.0)

                elif e.key == K_2 and (e.mod & KMOD_ALT):
                    act_anim2 = True

                elif e.key == K_3 and (e.mod & KMOD_ALT):
                    act_anim3 = True
                    dest_rot_x = 6.3
                    stop_init = True

                elif e.key == K_4 and (e.mod & KMOD_ALT):
                    act_anim4 = True

                elif e.key == K_5 and (e.mod & KMOD_ALT):
                    act_anim5 = True
                    grid_mov_x = -300.0 * dt
                    grid_mov_z = 0.0000
                    model_angle = 90
                    direction = 'right'
                    rot_x = 18.5000
                    scale = 0.3# 2.92
                    #stop_rate_x = stop_rate_z = 0.0000

                elif e.key == K_6 and (e.mod & KMOD_ALT):
                    stop_camera = True
                    glRotatef(-34.6731, 1.0, 0.0, 0.0)

                elif e.key == K_7 and (e.mod & KMOD_ALT):
                    act_anim7 = True

                #elif  e.key == K_p and (e.mod & KMOD_ALT):
                    #ortographic = not ortographic
                    #if ortographic:
                        #setup_view_ortho(display)
                    #else:
                        #setup_view_perspective(display)

                elif e.key == K_UP:
                    #grid_mov_z = tank_speed #0.0500 * dt
                    #grid_mov_x = 0.0000
                    moving = True
                    #model_angle = 180
                    new_direction = 'front'
                    stop_rate_x = stop_rate_z = 0.0000
                    resetting = False

                elif e.key == K_DOWN:
                    #grid_mov_z = -tank_speed #-0.0500 #-0.10000
                    #grid_mov_x = 0.0000
                    moving = True
                    #model_angle = 0
                    new_direction = 'back'
                    stop_rate_x = stop_rate_z = 0.0000
                    resetting = False

                elif e.key == K_LEFT:
                    #grid_mov_x = tank_speed #0.0500
                    #grid_mov_z = 0.0000
                    moving = True
                    #model_angle = -90
                    new_direction = 'left'
                    stop_rate_x = stop_rate_z = 0.0000
                    resetting = False

                elif e.key == K_RIGHT:
                    #grid_mov_x = -tank_speed #-0.05000
                    #grid_mov_z = 0.0000
                    moving = True
                    #model_angle = 90
                    new_direction = 'right'
                    stop_rate_x = stop_rate_z = 0.0000
                    resetting = False

                elif e.key == K_b:
                    #y_tower = 0.0
                    act_anim7 = True
                    dest_y_tower = 0.0

                elif e.key == K_v:
                    y_tower = 180

                elif e.key == K_c:
                    #grid_mov_x = grid_mov_z = 0.0
                    #stop_rate_x, stop_rate_z = stop_movement(direction)
                    braking = True

                elif e.key == K_j:
                    hide_info = not hide_info

                elif e.key == K_s:
                    stop_camera = not stop_camera

                elif e.key == K_l:
                       resetting = True
                       x = y = z = 0.0
                       stop_rate_x = stop_rate_z = 0.0000
                       grid_mov_x = grid_mov_z = 0.0
                       model_angle = 180
                       target_angle = 180
                       y_tower = 0.0
                       rot_x = 0.0
                       rot_y = 0.0
                       scale = 1.0
                       direction = 'front'
                       new_direction = 'front'
                       stop_camera = False
                       glLoadIdentity()
                       gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
                       glTranslatef(0.0, 0.0, -10)
                       glRotatef(35.0, 1.0, 0.0, 0.0)


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
            rot_y += 30.0 * dt
        elif keys[K_r]:
            rot_y -= 30.0 * dt

        if keys[K_f]:
            #rot_x = 0.5
            #glRotatef(rot_x, 1.0, 0.0, 0.0)
            rot_x += ROT_X_SPEED * dt
        elif keys[K_g]:
            #rot_x = -0.5
            #glRotatef(rot_x, 1.0, 0.0, 0.0)
            rot_x -= ROT_X_SPEED * dt

        if keys[K_p]:
            y += 6.0 * dt
        elif keys[K_o]:
            y -= 6.0 * dt


        if direction == 'front' or direction == 'right':
            if keys[pygame.K_n]:
                y_tower += 60.0 * dt
            elif keys[pygame.K_m]:
                y_tower -= 60.0 * dt
        elif direction == 'back' or direction == 'left':
            if keys[pygame.K_n]:
                y_tower -= 60.0 * dt
            elif keys[pygame.K_m]:
                y_tower += 60.0 * dt

        if keys[K_z]:
            scale += 1.2 * dt
        elif keys[K_x]:
            scale -= 1.2 * dt

        # ===== ACTUALIZACIÓN =====

        #--------------animaciones--------------#
        if act_anim:
            if scale < dest_scale:
                scale += 0.6 * dt
            elif rot_x > dest_rot_x:
                rot_x -= 60.0 * dt
            else:
                act_anim = False

        if act_anim2:

            if rot_y > dest_rot_y:
                rot_y -= 30.0 * dt
            #elif rot_x < dest_rot_x:
                #rot_x += 30.0 * dt
            else:
                act_anim2 = False

        if act_anim3:
            if stop_init:
                #stop_rate_x, stop_rate_z = stop_movement(direction)
                braking = True
                stop_init = False

            if rot_x < dest_rot_x:
                rot_x += 6.0 * dt
            else:
                act_anim3 = False

        if act_anim4:
            diff = dest_y_tower - y_tower
            if abs(diff) > 0.1:
                y_tower += math.copysign(min(abs(diff), 60.0 * dt), diff)
            else:
                y_tower = dest_y_tower
                act_anim4 = False

        if act_anim5:
            #scale = 0.3
            if scale < 1.77: #if scale > 0.8:
                scale += 0.01
            else:
                act_anim5 = False

        if act_anim7:
            diff = dest_y_tower - y_tower
            if abs(diff) > 0.1:
                y_tower += math.copysign(min(abs(diff), 60.0 * dt), diff)
            else:
                y_tower = dest_y_tower
                act_anim7 = False

        #----------------------------------------#

        #FRENADA PROGRESIVA###########################################
        if braking:
            deceleration = stop_rate * dt

            if direction in ('front', 'back'):
                if grid_mov_z > 0.0:
                    #print("ok")
                    grid_mov_z = max(0.0, grid_mov_z - deceleration)
                elif grid_mov_z < 0.0:
                    #print("OK")
                    grid_mov_z = min(0.0, grid_mov_z + deceleration)
                if grid_mov_z == 0.0:
                    braking = False
                    moving = False
            else:
                if grid_mov_x > 0.0:
                    grid_mov_x = max(0.0, grid_mov_x - deceleration)
                elif grid_mov_x < 0.0:
                    grid_mov_x = min(0.0, grid_mov_x + deceleration)
                if grid_mov_x == 0.0:
                    braking = False
                    moving = False

        ###############################################################
        
        #--------------------------------ROTACION Y TRANSLACION DEL TANQUE------------------------------#
        if new_direction != direction:
           target_angle = DIRECTION_ANGLE[new_direction]
           rotating = True
           grid_mov_x = grid_mov_z = 0.0

        if not resetting:

            if rotating:
                diff = (target_angle - model_angle + 180) % 360 -180
                if abs(diff) < rotation_speed:
                    model_angle = target_angle
                    rotating = False
                    direction = new_direction
                else:
                    model_angle += rotation_speed * (1 if diff > 0 else -1) 

            if not rotating and not braking and moving:
                rad = math.radians(model_angle)
                if direction in ['front', 'back']:
                    grid_mov_x = math.sin(rad) * 3.5
                    grid_mov_z = -math.cos(rad) * 3.5
                else:
                    grid_mov_x = -math.sin(rad) * 3.5
                    grid_mov_z = math.cos(rad) * 3.5

        x += grid_mov_x * dt
        z += grid_mov_z * dt

        if not stop_camera:
            last_cam_pos_x = x
            last_cam_pos_z = z
        #------------------------------------------------------------------------------------------------#

        # ===== LIMITAR MOVIMIEMTO DENTRO DEL GRID =====
        if x - 2 < (-grid_size - 0.1) or x + 2 > (grid_size + 0.1):
            grid_mov_x = 0.0
            if direction == 'left':
                x -= 0.1
            elif direction == 'right':
                x += 0.1
            moving = False
        elif z - 2 < (-grid_size - 0.1) or z + 2 > (grid_size + 0.1):
            grid_mov_z = 0.0
            if direction == 'front':
                z -= 0.1
            elif direction == 'back':
                z += 0.1
            moving = False

        for b in bullets:
            b["pos"][0] += b["dir"][0] * bullet_speed * dt
            b["pos"][2] += b["dir"][2] * bullet_speed * dt

        # ===== RENDER =====
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glScalef(scale, scale, scale)
        glRotatef(rot_x, 1.0, 0.0, 0.0)
        glRotatef(rot_y, 0.0, 1.0, 0.0)
        if not stop_camera:
            glTranslatef(x, y, z)
        else:
            #glTranslatef(0.0, 0.0, 0.0)
            glTranslatef(last_cam_pos_x, y, last_cam_pos_z)

        glCallList(grid)

        # ===== TANQUE =====
        glPushMatrix()
        #glLineWidth(2.0)
        #glColor3f(0.0,1.0,0.0)
        glTranslatef(-x, 0.2, -z)
        glRotatef(model_angle, 0, 1, 0)

        glPushMatrix()
        glRotatef(y_tower, 0, 1, 0)
        glCallList(model_tower)
        #glScalef(0.4,0.4,0.4)
        glCallList(model_base_antena)
        #glPushMatrix()
        glRotatef(rotor_pos,0,1,0)

        glCallList(model_rotor_antena)
        #glPopMatrix()
        glPopMatrix()

        #glColor3f(0.0,1.0,0.0)
        glCallList(model_base)
        glPopMatrix()

        rotor_pos += 2.0

        # ===== BALAS (MUNDO REAL) =====
        for b in bullets:
            glPushMatrix()
            #glLineWidth(1.0)
            glTranslatef(b["pos"][0], b["pos"][1], b["pos"][2])
            ang = math.degrees(math.atan2(b["dir"][0], b["dir"][2]))
            glRotatef(ang, 0, 1, 0)
            glCallList(model_bullet)
            glPopMatrix()

        glPopMatrix() # 468, 451, 434, 417, 400, 383, 366

        if not hide_info:
            draw_text(font, 10, 570, f'CAMERA MOV: {not stop_camera}')
            draw_text(font, 10, 553, f'DIRECTION: {direction}')
            draw_text(font, 10, 536, f'X: {x:.2f}')
            draw_text(font, 10, 519, f'Y: {y:.2f}')
            draw_text(font, 10, 502, f'Z: {z:.2f}')
            #draw_text(font, 10, 485, f'SR: {stop_rate:.2f}')
            #draw_text(font, 10, 485, f'SRz: {stop_rate_z:.2f}')
            draw_text(font, 10, 485, f'GRID MOV X: {grid_mov_x:.2f}')
            draw_text(font, 10, 468, f'GRID MOV Z: {grid_mov_z:.2f}')
            draw_text(font, 10, 451, f'ROT X: {rot_x:.2f}')
            draw_text(font, 10, 434, f'ROT Y: {rot_y:.2f}')
            draw_text(font, 10, 417, f'TOWER ROT: {y_tower:.2f}')
            draw_text(font, 10, 400, f'SCALE: {scale:.2f}')

        pygame.display.flip()
        clock.tick(120)

    glDeleteLists(grid, 1)
    glDeleteLists(model_base, 1)
    glDeleteLists(model_tower, 1)
    glDeleteLists(model_bullet, 1)
    glDeleteLists(model_base_antena, 1)
    glDeleteLists(model_rotor_antena, 1)
    pygame.quit()

def main():
    parser = argparse.ArgumentParser(
    prog = "tank_demo_vb.py",
    conflict_handler = "resolve",
    description = "Tank demo 4",
    allow_abbrev = False
    )
    parser.add_argument('-alsg','--antialiasing',action='store_true',help='Activate antialiasing')
    parser.add_argument('-fl','--floor',action='store_true',help='Show floor')
    args = parser.parse_args()

    main_loop(args)



main()
