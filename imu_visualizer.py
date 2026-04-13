import serial
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

COM_PORT = 'COM3'
BAUD_RATE = 115200

def quat_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ])

def quat_conjugate(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])

def quaternion_to_matrix(q):
    # Verified column-major OpenGL matrix (songho.ca/opengl/gl_quaternion.html)
    w, x, y, z = q
    return [
        1-2*(y*y+z*z), 2*(x*y+z*w),   2*(x*z-y*w),   0,
        2*(x*y-z*w),   1-2*(x*x+z*z), 2*(y*z+x*w),   0,
        2*(x*z+y*w),   2*(y*z-x*w),   1-2*(x*x+y*y), 0,
        0,             0,             0,             1
    ]

def draw_box():
    vertices = [
        ( 1.5, 0.1, 0.8), (-1.5, 0.1, 0.8), (-1.5,-0.1, 0.8), ( 1.5,-0.1, 0.8),
        ( 1.5,-0.1,-0.8), ( 1.5, 0.1,-0.8), (-1.5, 0.1,-0.8), (-1.5,-0.1,-0.8)
    ]
    faces = [
        ([0,1,2,3], (0.0, 0.5, 1.0)),
        ([4,5,0,3], (1.0, 0.5, 0.0)),
        ([5,6,1,0], (0.0, 1.0, 0.5)),
        ([7,4,3,2], (1.0, 0.0, 0.5)),
        ([5,4,7,6], (0.5, 0.0, 1.0)),
        ([6,7,2,1], (0.5, 1.0, 0.0)),
    ]
    glBegin(GL_QUADS)
    for face, color in faces:
        glColor3fv(color)
        for v in face:
            glVertex3fv(vertices[v])
    glEnd()
    glColor3f(0, 0, 0)
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,5),(1,6),(2,7),(3,4)]
    glBegin(GL_LINES)
    for e in edges:
        for v in e:
            glVertex3fv(vertices[v])
    glEnd()

def draw_axes():
    glLineWidth(3)
    glBegin(GL_LINES)
    glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(2,0,0)
    glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,2,0)
    glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,2)
    glEnd()
    glLineWidth(1)

def main():
    # Tare stored in raw BNO frame (real, i, j, k)
    tare_raw = np.array([1.0, 0.0, 0.0, 0.0])
    current_raw = np.array([1.0, 0.0, 0.0, 0.0])

    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("TrueSight IMU — SPACE=tare  ESC=quit")
    gluPerspective(45, 800/600, 0.1, 50.0)
    glTranslatef(0, 0, -5)
    glEnable(GL_DEPTH_TEST)

    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print("Connected. Place BNO flat, press SPACE to tare.")

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                ser.close(); pygame.quit(); return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    ser.close(); pygame.quit(); return
                if event.key == K_SPACE:
                    # Tare in raw BNO frame — no remapping yet
                    tare_raw = current_raw.copy()
                    print("Tared.")

        try:
            # Drain buffer — discard all but the most recent line
            while ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
            parts = line.split(',')
            if len(parts) >= 4:
                i    = float(parts[0])
                j    = float(parts[1])
                k    = float(parts[2])
                real = float(parts[3])
                current_raw = np.array([real, i, j, k])
        except:
            pass

        # Step 1: compute relative rotation entirely in BNO body frame
        rel = quat_multiply(quat_conjugate(tare_raw), current_raw)
        # rel[0]=real, rel[1]=i(bodyX), rel[2]=j(bodyY), rel[3]=k(bodyZ/up)

        # Step 2: remap BNO body frame axes to OpenGL axes
        # BNO body Z (up, rel[3]) → OpenGL Y (up)
        # BNO body X (rel[1])     → OpenGL X (pitch forward/back)
        # BNO body Y (rel[2])     → OpenGL Z (roll sideways)
        # Signs: start with physically expected directions
        display_q = np.array([
            rel[0],   # w unchanged
            rel[1],   # BNO X → OpenGL X (pitch) — negate if forward is mirrored
            -rel[3],   # BNO Z → OpenGL Y (yaw)   — negate if spin is mirrored
            rel[2]   # BNO Y → OpenGL Z (roll)  — negate if sideways is mirrored
        ])

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1, 0.1, 0.1, 1)
        glPushMatrix()
        glMultMatrixf(quaternion_to_matrix(display_q))
        draw_box()
        glPopMatrix()
        draw_axes()
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()