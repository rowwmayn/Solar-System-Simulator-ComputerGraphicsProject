from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time

# Camera and simulation variables
camera_pos = (0, 500, 1500)
camera_target = (0, 0, 0)
paused = False
time_scale = 1.0
selected_planet = -1
follow_mode = False
show_trails = True
display_mode = 0  # 0: full system, 1: inner planets

# Celestial data (simplified)
celestial_data = [
    # Sun
    {"name": "Sun", "radius": 150, "orbit_radius": 0, "orbit_speed": 0, 
     "rotation_speed": 0.2, "color": (1.0, 0.7, 0.0), "moons": []},
    # Mercury
    {"name": "Mercury", "radius": 20, "orbit_radius": 250, "orbit_speed": 4.1, 
     "rotation_speed": 0.1, "color": (0.7, 0.7, 0.7), "moons": []},
    # Venus
    {"name": "Venus", "radius": 35, "orbit_radius": 350, "orbit_speed": 1.6, 
     "rotation_speed": 0.08, "color": (0.9, 0.7, 0.4), "moons": []},
    # Earth
    {"name": "Earth", "radius": 40, "orbit_radius": 500, "orbit_speed": 1.0, 
     "rotation_speed": 1.0, "color": (0.0, 0.3, 0.8), "moons": []},
    # Mars
    {"name": "Mars", "radius": 30, "orbit_radius": 650, "orbit_speed": 0.5, 
     "rotation_speed": 0.9, "color": (0.8, 0.3, 0.0), "moons": []},
]

orbit_angles = [0.0] * len(celestial_data)
rotation_angles = [0.0] * len(celestial_data)

def draw_sphere(radius, slices=20, stacks=20):
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + (i / stacks))
        lat1 = math.pi * (-0.5 + ((i+1) / stacks))
        glBegin(GL_TRIANGLE_STRIP)
        for j in range(slices + 1):
            lng = 2 * math.pi * (j / slices)
            x0 = radius * math.cos(lng) * math.cos(lat0)
            y0 = radius * math.sin(lng) * math.cos(lat0)
            z0 = radius * math.sin(lat0)
            x1 = radius * math.cos(lng) * math.cos(lat1)
            y1 = radius * math.sin(lng) * math.cos(lat1)
            z1 = radius * math.sin(lat1)
            glVertex3f(x0, y0, z0)
            glVertex3f(x1, y1, z1)
        glEnd()

def draw_planet(planet, orbit_angle, rotation_angle):
    glPushMatrix()
    glRotatef(orbit_angle, 0, 0, 1)
    glTranslatef(planet["orbit_radius"], 0, 0)
    glRotatef(rotation_angle, 0, 0, 1)
    glColor3f(*planet["color"])
    draw_sphere(planet["radius"])
    glPopMatrix()

def draw_orbital_trail(planet):
    glBegin(GL_LINE_LOOP)
    glColor3f(*planet["color"])
    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        x = planet["orbit_radius"] * math.cos(rad)
        y = planet["orbit_radius"] * math.sin(rad)
        glVertex3f(x, y, 0)
    glEnd()

def draw_shapes():
    # Sun
    glPushMatrix()
    glColor3f(1.0, 0.7, 0.0)
    draw_sphere(celestial_data[0]["radius"])
    glPopMatrix()

    # Planets
    start = 1
    end = len(celestial_data)
    if display_mode == 1: end = 5  # Inner planets only
    
    for i in range(start, end):
        draw_planet(celestial_data[i], orbit_angles[i], rotation_angles[i])
        if show_trails:
            draw_orbital_trail(celestial_data[i])

def keyboardListener(key, x, y):
    global paused, time_scale, show_trails, selected_planet, follow_mode, display_mode
    key = key.decode("utf-8").lower()
    
    if key == 'p':
        paused = not paused
    elif key == '+':
        time_scale *= 1.5
    elif key == '-':
        time_scale = max(0.1, time_scale / 1.5)
    elif key == 'o':
        show_trails = not show_trails
    elif key == 'm':
        display_mode = (display_mode + 1) % 2
    elif key in ['0','1','2','3','4']:
        selected_planet = int(key)
        follow_mode = True if int(key) > 0 else False

def specialKeyListener(key, x, y):
    global camera_pos
    x, y, z = camera_pos
    angle = 2  # Rotation angle per keypress
    
    if key == GLUT_KEY_LEFT:
        camera_pos = (x * math.cos(math.radians(angle)) - y * math.sin(math.radians(angle)),
                       x * math.sin(math.radians(angle)) + y * math.cos(math.radians(angle)), z)
    elif key == GLUT_KEY_RIGHT:
        camera_pos = (x * math.cos(math.radians(-angle)) - y * math.sin(math.radians(-angle)),
                       x * math.sin(math.radians(-angle)) + y * math.cos(math.radians(-angle)), z)
    elif key == GLUT_KEY_UP:
        camera_pos = (x, y, z * 0.9)
    elif key == GLUT_KEY_DOWN:
        camera_pos = (x, y, z * 1.1)

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.25, 10, 20000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if follow_mode and selected_planet > 0:
        planet = celestial_data[selected_planet]
        angle_rad = math.radians(orbit_angles[selected_planet])
        px = planet["orbit_radius"] * math.cos(angle_rad)
        py = planet["orbit_radius"] * math.sin(angle_rad)
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2], px, py, 0, 0, 0, 1)
    else:
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2], 0, 0, 0, 0, 0, 1)

def idle():
    if not paused:
        for i in range(len(celestial_data)):
            orbit_angles[i] = (orbit_angles[i] + celestial_data[i]["orbit_speed"] * time_scale) % 360
            rotation_angles[i] = (rotation_angles[i] + celestial_data[i]["rotation_speed"] * time_scale) % 360
    glutPostRedisplay()

def draw_text(x, y, text):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setupCamera()
    draw_shapes()
    
    # UI Text
    draw_text(10, 770, f"Time Scale: x{time_scale:.1f}")
    draw_text(10, 740, "PAUSED" if paused else "RUNNING")
    draw_text(10, 710, f"Selected: {celestial_data[selected_planet]['name']}" if selected_planet >=0 else "Sun")
    draw_text(10, 680, f"Mode: {'Full System' if display_mode ==0 else 'Inner Planets'}")
    draw_text(700, 770, "Controls: Arrows=Move, P=Pause, O=Trails, M=Mode, 0-4=Select")
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"Solar System")
    glClearColor(0.0, 0.0, 0.1, 1.0)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
