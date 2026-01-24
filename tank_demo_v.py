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
    v, e, f = load_object(path)
    glBegin(GL_LINES)
    for a, b in e:
        glVertex3f(*v[a])
        glVertex3f(*v[b])
    glEnd()
    if path != 'C:\\Users\\Usuario\\Documents\\repositorios\\tank_controller\\tanque\\bullet.obj':
        glBegin(GL_QUADS)
        glColor3f(0.1, 0.1, 0.1)
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


# ================= MAIN =================
def main():
    show_controls()
    pygame.init()
    display = (800, 600)

    font = pygame.font.SysFont('arial',15)

    # ========================== ANTIALIASING =========================
    #pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    #pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 6)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    #glEnable(GL_MULTISAMPLE)
    #glEnable(GL_LINE_SMOOTH)
    #glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    # =================================================================

    gluPerspective(45, display[0] / display[1], 0.1, 90)
    glTranslatef(0, 0, -10)
    #glRotatef(35, 1, 0, 0)
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
    x = y = z = 0.0000                # desplazamiento del mundo
    grid_mov_x = grid_mov_z = 0.0000
    stop_rate_x = stop_rate_z = 0.0000
    last_cam_pos_x = last_cam_pos_z = 0.0
    ortographic = False
    
    hide_info = False

    act_anim = False
    dest_scale = 0.81
    dest_rot_x = 1.0 #-88.5
    act_anim2 = False
    dest_rot_y = -152.0
    #dest_rot_x = -28.0
    act_anim3 = False
    act_anim4 = False
    dest_y_tower = 62.0


    model_angle = 180
    y_tower = 0.0
    rot_x = 35.0 #0.0
    ROT_X_SPEED = 0.5 #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    rot_y = 0.0
    stop_camera = False
    scale = 1.00
    direction = 'front'

    bullets = []
    bullet_speed = 0.5 #0.2

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False

            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    running = False

                elif e.key == K_1 and (e.mod & KMOD_ALT):
                    glLoadIdentity()
                    gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
                    glTranslatef(0.0, 0.0, -10.0)
                    rot_x = 90############################
                    scale = 0.39
                    dest_scale = 0.81
                    act_anim = True
                    dest_rot_x = 1.0
                    #glRotatef(90.0, 1.0, 0.0, 0.0)

                elif e.key == K_2 and (e.mod & KMOD_ALT):
                    act_anim2 = True

                elif e.key == K_3 and (e.mod & KMOD_ALT):
                    act_anim3 = True
                    dest_rot_x = 6.3
                
                elif e.key == K_4 and (e.mod & KMOD_ALT):
                    act_anim4 = True

                #elif  e.key == K_p and (e.mod & KMOD_ALT):
                    #ortographic = not ortographic
                    #if ortographic:
                        #setup_view_ortho(display)
                    #else:
                        #setup_view_perspective(display)'''

                elif e.key == K_UP:
                    grid_mov_z = 0.0500
                    grid_mov_x = 0.0000
                    model_angle = 180
                    direction = 'front'
                    stop_rate_x = stop_rate_z = 0.0000

                elif e.key == K_DOWN:
                    grid_mov_z = -0.0500 #-0.10000
                    grid_mov_x = 0.0000
                    model_angle = 0
                    direction = 'back'
                    stop_rate_x = stop_rate_z = 0.0000

                elif e.key == K_LEFT:
                    grid_mov_x = 0.0500
                    grid_mov_z = 0.0000
                    model_angle = -90
                    direction = 'left'
                    stop_rate_x = stop_rate_z = 0.0000

                elif e.key == K_RIGHT:
                    grid_mov_x = -0.05000
                    grid_mov_z = 0.0000
                    model_angle = 90
                    direction = 'right'
                    stop_rate_x = stop_rate_z = 0.0000

                elif e.key == K_b:
                    y_tower = 0.0

                elif e.key == K_v:
                    y_tower = 180

                elif e.key == K_c:
                    #grid_mov_x = grid_mov_z = 0.0
                    if direction == 'front' or direction == 'back':
                        stop_rate_z = 0.0001
                    elif direction == 'right' or direction == 'left':
                        stop_rate_x = 0.0001

                elif e.key == K_j:
                    hide_info = not hide_info

                elif e.key == K_s:
                    stop_camera = not stop_camera

                elif e.key == K_l:
                       x = y = z = 0.0
                       stop_rate_x = stop_rate_z = 0.0000
                       grid_mov_x = grid_mov_z = 0.0
                       model_angle = 180
                       y_tower = 0.0
                       rot_x = 0.0
                       rot_y = 0.0
                       scale = 1.0
                       direction = 'front'
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
            rot_y += 1.0
        elif keys[K_r]:
            rot_y -= 1.0

        if keys[K_f]:
            #rot_x = 0.5
            #glRotatef(rot_x, 1.0, 0.0, 0.0)
            rot_x += ROT_X_SPEED
        elif keys[K_g]:
            #rot_x = -0.5
            #glRotatef(rot_x, 1.0, 0.0, 0.0)
            rot_x -= ROT_X_SPEED

        if keys[K_p]:
            y += 0.1
        elif keys[K_o]:
            y -= 0.1


        if direction == 'front' or direction == 'right':
            if keys[pygame.K_n]:
                y_tower += 1.0#1.1
            elif keys[pygame.K_m]:
                y_tower -= 1.0#1.1
        elif direction == 'back' or direction == 'left':
            if keys[pygame.K_n]:
                y_tower -= 1.0#1.1
            elif keys[pygame.K_m]:
                y_tower += 1.0#1.1

        if keys[K_z]:
            scale += 0.02
        elif keys[K_x]:
            scale -= 0.02

        # ===== ACTUALIZACIÓN =====
        
        #--------------animaciones--------------#
        if act_anim:
            if scale < dest_scale:
                scale += 0.01
            elif rot_x > dest_rot_x:
                rot_x -= 1.0
            else:
                act_anim = False

        if act_anim2:
            if rot_y > dest_rot_y:
                rot_y -= 1.0
            else:
                act_anim2 = False

        if act_anim3:
            if rot_x < dest_rot_x:
                rot_x += 0.1
            else:
                act_anim3 = False

        if act_anim4:
            if y_tower < dest_y_tower:
                y_tower += 1.0
            else:
                act_anim4 = False
        
        #----------------------------------------#

        #FRENADA PROGRESIVA####################################

        if direction == 'front' or direction == 'back':
            if grid_mov_z > 0.0000 and direction == 'front':
                grid_mov_z -= stop_rate_z

            if grid_mov_z < 0.0000 and direction == 'back':
                grid_mov_z += stop_rate_z
        else:
            if grid_mov_x > 0.0000 and direction == 'left':
                grid_mov_x -= stop_rate_x

            if grid_mov_x < 0.0000 and direction == 'right':
                grid_mov_x += stop_rate_x

        #######################################################

        x += grid_mov_x
        z += grid_mov_z
        
        if not stop_camera:
            last_cam_pos_x = x
            last_cam_pos_z = z

        # ===== LIMITAR MOVIMIEMTO DENTRO DEL GRID =====
        if x - 2 < (-grid_size - 0.1) or x + 2 > (grid_size + 0.1):
            grid_mov_x = 0.0
            if direction == 'left':
                x -= 0.1
            elif direction == 'right':
                x += 0.1
        elif z - 2 < (-grid_size - 0.1) or z + 2 > (grid_size + 0.1):
            grid_mov_z = 0.0
            if direction == 'front':
                z -= 0.1
            elif direction == 'back':
                z += 0.1

        for b in bullets:
            b["pos"][0] += b["dir"][0] * bullet_speed
            b["pos"][2] += b["dir"][2] * bullet_speed

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
        glLineWidth(2.0)
        glColor3f(0.0,1.0,0.0)
        glTranslatef(-x, 0.2, -z)
        glRotatef(model_angle, 0, 1, 0)

        glPushMatrix()
        glRotatef(y_tower, 0, 1, 0)
        glCallList(model_tower)
        glPopMatrix()
        
        glColor3f(0.0,1.0,0.0)
        glCallList(model_base)
        glPopMatrix()

        # ===== BALAS (MUNDO REAL) =====
        for b in bullets:
            glPushMatrix()
            glColor3f(1.0,0.0,0.0)
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
            draw_text(font, 10, 485, f'SRX: {stop_rate_x:.4f}')
            draw_text(font, 10, 468, f'SRZ: {stop_rate_z:.4f}')
            draw_text(font, 10, 451, f'GRID MOV X: {grid_mov_x:.4f}')
            draw_text(font, 10, 434, f'GRID MOVZ: {grid_mov_z:.4f}')
            draw_text(font, 10, 417, f'ROT X: {rot_x:.4f}')
            draw_text(font, 10, 400, f'ROT Y: {rot_y}')
            draw_text(font, 10, 383, f'TOWER ROT: {y_tower:.4f}')
            draw_text(font, 10, 366, f'SCALE: {scale:.2f}')    

        pygame.display.flip()
        pygame.time.wait(10)
    
    glDeleteLists(grid, 1)
    glDeleteLists(model_base, 1)
    glDeleteLists(model_tower, 1)
    glDeleteLists(model_bullet, 1)
    pygame.quit()


main()
