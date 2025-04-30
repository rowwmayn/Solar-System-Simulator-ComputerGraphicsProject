from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time

# Camera-related variables
camera_pos = (0, 500, 1500)
camera_target = (0, 0, 0)
camera_up = (0, 0, 1)
follow_mode = False
selected_planet = -1  # -1 for sun, 0-7 for planets

# Simulation control variables
paused = False
time_scale = 1.0
display_mode = 0  # 0: full system, 1: inner planets, 2: planet+moons only
show_trails = True
show_asteroid_belt = True
show_comet = True

# Field of view
fovY = 45

# Grid length
GRID_LENGTH = 3000

# Celestial objects data: (radius, orbit_radius, orbit_speed, rotation_speed, axial_tilt, color, moons)
# Sizes and distances are not to scale for visualization purposes
celestial_data = [
    # Sun
    {"name": "Sun", "radius": 150, "orbit_radius": 0, "orbit_speed": 0, "rotation_speed": 0.2, 
     "axial_tilt": 7.25, "color": (1.0, 0.7, 0.0), "moons": []},
    # Mercury
    {"name": "Mercury", "radius": 20, "orbit_radius": 250, "orbit_speed": 4.1, "rotation_speed": 0.1, 
     "axial_tilt": 0.03, "color": (0.7, 0.7, 0.7), "moons": []},
    # Venus
    {"name": "Venus", "radius": 35, "orbit_radius": 350, "orbit_speed": 1.6, "rotation_speed": 0.08, 
     "axial_tilt": 177.4, "color": (0.9, 0.7, 0.4), "moons": []},
    # Earth
    {"name": "Earth", "radius": 40, "orbit_radius": 500, "orbit_speed": 1.0, "rotation_speed": 1.0, 
     "axial_tilt": 23.5, "color": (0.0, 0.3, 0.8), "moons": [
         {"name": "Moon", "radius": 10, "orbit_radius": 60, "orbit_speed": 1.0, "rotation_speed": 0.1, 
          "axial_tilt": 5.14, "color": (0.8, 0.8, 0.8)}
     ]},
    # Mars
    {"name": "Mars", "radius": 30, "orbit_radius": 650, "orbit_speed": 0.5, "rotation_speed": 0.9, 
     "axial_tilt": 25.2, "color": (0.8, 0.3, 0.0), "moons": [
         {"name": "Phobos", "radius": 5, "orbit_radius": 45, "orbit_speed": 2.0, "rotation_speed": 0.3, 
          "axial_tilt": 0.0, "color": (0.6, 0.6, 0.6)},
         {"name": "Deimos", "radius": 3, "orbit_radius": 65, "orbit_speed": 1.0, "rotation_speed": 0.3, 
          "axial_tilt": 0.0, "color": (0.5, 0.5, 0.5)}
     ]},
    # Jupiter
    {"name": "Jupiter", "radius": 80, "orbit_radius": 900, "orbit_speed": 0.08, "rotation_speed": 2.0, 
     "axial_tilt": 3.13, "color": (0.9, 0.8, 0.6), "moons": [
         {"name": "Io", "radius": 8, "orbit_radius": 100, "orbit_speed": 1.8, "rotation_speed": 0.5, 
          "axial_tilt": 0.0, "color": (0.9, 0.8, 0.2)},
         {"name": "Europa", "radius": 7, "orbit_radius": 120, "orbit_speed": 1.4, "rotation_speed": 0.5, 
          "axial_tilt": 0.0, "color": (0.8, 0.8, 0.9)},
         {"name": "Ganymede", "radius": 10, "orbit_radius": 140, "orbit_speed": 0.7, "rotation_speed": 0.5, 
          "axial_tilt": 0.0, "color": (0.6, 0.6, 0.7)},
         {"name": "Callisto", "radius": 9, "orbit_radius": 180, "orbit_speed": 0.3, "rotation_speed": 0.5, 
          "axial_tilt": 0.0, "color": (0.5, 0.5, 0.5)}
     ]},
    # Saturn
    {"name": "Saturn", "radius": 70, "orbit_radius": 1200, "orbit_speed": 0.03, "rotation_speed": 1.9, 
     "axial_tilt": 26.7, "color": (0.9, 0.8, 0.5), "moons": [
         {"name": "Titan", "radius": 9, "orbit_radius": 120, "orbit_speed": 0.05, "rotation_speed": 0.5, 
          "axial_tilt": 0.0, "color": (0.8, 0.7, 0.5)}
     ]},
    # Uranus
    {"name": "Uranus", "radius": 50, "orbit_radius": 1500, "orbit_speed": 0.01, "rotation_speed": 1.4, 
     "axial_tilt": 97.8, "color": (0.5, 0.8, 0.9), "moons": []},
    # Neptune
    {"name": "Neptune", "radius": 45, "orbit_radius": 1800, "orbit_speed": 0.006, "rotation_speed": 1.5, 
     "axial_tilt": 28.3, "color": (0.1, 0.1, 0.8), "moons": []}
]

# Asteroid belt
asteroid_belt = {
    "inner_radius": 700,
    "outer_radius": 850,
    "count": 200,
    "positions": []
}

# Comet data
comet = {
    "radius": 10,
    "perihelion": 400,  # Closest approach to sun
    "aphelion": 2000,   # Furthest distance from sun
    "angle": 0,
    "speed": 0.5,
    "color": (0.9, 0.9, 1.0),
    "tail_length": 100
}

# Orbital trails
orbital_trails = []

# Initialize angles for orbits and rotations
orbit_angles = [0.0] * len(celestial_data)
rotation_angles = [0.0] * len(celestial_data)

# Initialize asteroid belt positions
def init_asteroid_belt():
    import random
    for _ in range(asteroid_belt["count"]):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(asteroid_belt["inner_radius"], asteroid_belt["outer_radius"])
        size = random.uniform(1, 5)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = random.uniform(-10, 10)
        asteroid_belt["positions"].append((x, y, z, size))

init_asteroid_belt()

# Initialize orbital trails
def init_orbital_trails():
    global orbital_trails
    orbital_trails = []
    for i in range(1, len(celestial_data)):
        trail = []
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            x = celestial_data[i]["orbit_radius"] * math.cos(rad)
            y = celestial_data[i]["orbit_radius"] * math.sin(rad)
            trail.append((x, y, 0))
        orbital_trails.append(trail)

init_orbital_trails()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_comet():
    if not show_comet:
        return
        
    # Update comet position
    angle_rad = math.radians(comet["angle"])
    
    # Calculate distance using elliptical orbit approximation
    e = (comet["aphelion"] - comet["perihelion"]) / (comet["aphelion"] + comet["perihelion"])
    distance = comet["perihelion"] * (1 + e) / (1 + e * math.cos(angle_rad))
    
    # Calculate position
    x = distance * math.cos(angle_rad)
    y = distance * math.sin(angle_rad)
    
    # Draw comet
    glPushMatrix()
    glTranslatef(x, y, 0)
    
    # Comet nucleus
    glColor3f(*comet["color"])
    gluSphere(gluNewQuadric(), comet["radius"], 20, 20)
    
    # Comet tail (pointing away from sun)
    tail_angle = math.atan2(y, x) + math.pi
    tail_x = comet["tail_length"] * math.cos(tail_angle)
    tail_y = comet["tail_length"] * math.sin(tail_angle)
    
    glBegin(GL_TRIANGLES)
    # Gradient tail from white to transparent blue
    glColor4f(0.9, 0.9, 1.0, 0.8)
    glVertex3f(0, 0, 0)
    
    glColor4f(0.7, 0.7, 0.9, 0.1)
    glVertex3f(tail_x * 0.3, tail_y * 0.3, comet["radius"] * 2)
    
    glColor4f(0.5, 0.5, 0.8, 0.0)
    glVertex3f(tail_x, tail_y, 0)
    glEnd()
    
    glPopMatrix()

def draw_orbital_trails():
    if not show_trails:
        return
        
    glLineWidth(1.0)
    
    # Draw orbital trails for planets
    for i, trail in enumerate(orbital_trails):
        planet_color = celestial_data[i+1]["color"]
        glColor3f(*planet_color)
        
        glBegin(GL_LINE_LOOP)
        for point in trail:
            glVertex3f(*point)
        glEnd()

def draw_asteroid_belt():
    if not show_asteroid_belt:
        return
        
    glPointSize(2.0)
    glBegin(GL_POINTS)
    
    for pos in asteroid_belt["positions"]:
        x, y, z, size = pos
        # Gray to brown colors
        gray = 0.5 + (size / 5) * 0.3
        glColor3f(gray, gray * 0.8, gray * 0.6)
        glVertex3f(x, y, z)
    
    glEnd()
    
    # Also draw a few larger asteroids
    for i in range(20):
        pos = asteroid_belt["positions"][i * 10]
        x, y, z, size = pos
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.6, 0.55, 0.5)  # Asteroid color
        gluSphere(gluNewQuadric(), size, 6, 6)
        glPopMatrix()

def draw_planet_with_moons(planet_data, orbit_angle, rotation_angle):
    orbit_radius = planet_data["orbit_radius"]
    radius = planet_data["radius"]
    color = planet_data["color"]
    axial_tilt = planet_data["axial_tilt"]
    
    # Save the current matrix state for the planet's position
    glPushMatrix()
    
    # Move to orbit position
    glRotatef(orbit_angle, 0, 0, 1)
    glTranslatef(orbit_radius, 0, 0)
    
    # Planet self-rotation with axial tilt
    glPushMatrix()
    glRotatef(axial_tilt, 0, 1, 0)  # Apply axial tilt
    glRotatef(rotation_angle, 0, 0, 1)  # Apply self-rotation
    
    # Draw planet
    glColor3f(*color)
    planet_quadric = gluNewQuadric()
    gluQuadricTexture(planet_quadric, GL_TRUE)
    gluSphere(planet_quadric, radius, 30, 30)
    
    # Draw day/night transition (simple hemisphere shading)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)  # Rotate to align with light direction (sun)
    
    # Draw darker hemisphere facing away from the sun
    glColor3f(color[0] * 0.5, color[1] * 0.5, color[2] * 0.5)
    gluQuadricDrawStyle(planet_quadric, GLU_FILL)
    gluCylinder(planet_quadric, radius, radius, 0.01, 30, 1)
    glPopMatrix()
    
    glPopMatrix()  # End of planet rotation
    
    # Draw moons
    for moon in planet_data["moons"]:
        moon_orbit_radius = moon["orbit_radius"]
        moon_radius = moon["radius"]
        moon_color = moon["color"]
        moon_orbit_speed = moon["orbit_speed"]
        moon_rotation_speed = moon["rotation_speed"]
        moon_axial_tilt = moon["axial_tilt"]
        
        # Calculate moon angle
        moon_orbit_angle = orbit_angle * moon_orbit_speed * 2
        moon_rotation_angle = orbit_angle * moon_rotation_speed * 3
        
        glPushMatrix()
        # Moon orbit
        glRotatef(moon_orbit_angle, 0, 0, 1)
        glTranslatef(moon_orbit_radius, 0, 0)
        
        # Moon rotation
        glRotatef(moon_axial_tilt, 0, 1, 0)
        glRotatef(moon_rotation_angle, 0, 0, 1)
        
        # Draw moon
        glColor3f(*moon_color)
        moon_quadric = gluNewQuadric()
        gluSphere(moon_quadric, moon_radius, 20, 20)
        glPopMatrix()
    
    glPopMatrix()  # End of planet position

def draw_shapes():
    # Draw sun at the center
    glPushMatrix()
    
    # Sun glow effect (larger transparent sphere)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 0.8, 0.3, 0.1)
    gluSphere(gluNewQuadric(), celestial_data[0]["radius"] * 1.3, 30, 30)
    glDisable(GL_BLEND)
    
    # Sun itself
    glRotatef(rotation_angles[0], 0, 0, 1)  # Sun rotation
    glColor3f(*celestial_data[0]["color"])
    sun_quadric = gluNewQuadric()
    gluSphere(sun_quadric, celestial_data[0]["radius"], 30, 30)
    glPopMatrix()
    
    # Draw orbital trails
    draw_orbital_trails()
    
    # Draw asteroid belt
    draw_asteroid_belt()
    
    # Draw comet
    draw_comet()
    
    # Draw each planet with its moons
    # Skip planets based on display mode
    if display_mode == 1:  # Inner planets only
        planet_range = range(1, 5)  # Mercury to Mars
    elif display_mode == 2:  # Selected planet with moons
        if selected_planet >= 0 and selected_planet < len(celestial_data):
            planet_range = [selected_planet]
        else:
            planet_range = range(1, len(celestial_data))
    else:  # Full system
        planet_range = range(1, len(celestial_data))
    
    for i in planet_range:
        draw_planet_with_moons(celestial_data[i], orbit_angles[i], rotation_angles[i])

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for simulation control.
    """
    global paused, time_scale, display_mode, show_trails, show_asteroid_belt, selected_planet, follow_mode, show_comet
    
    # Pause/Resume with P key
    if key == b'p' or key == b'P':
        paused = not paused
    
    # Time scale control with +/- keys
    if key == b'+':
        time_scale *= 1.5
    if key == b'-':
        time_scale /= 1.5
        if time_scale < 0.1:
            time_scale = 0.1
    
    # Toggle trails with O key
    if key == b'o' or key == b'O':
        show_trails = not show_trails
    
    # Toggle asteroid belt with B key
    if key == b'b' or key == b'B':
        show_asteroid_belt = not show_asteroid_belt
        
    # Toggle comet with C key
    if key == b'c' or key == b'C':
        show_comet = not show_comet
    
    # Camera zoom with W/S keys
    if key == b'w' or key == b'W':
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] * 0.9)
    if key == b's' or key == b'S':
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] * 1.1)
    
    # Toggle follow mode with F key
    if key == b'f' or key == b'F':
        follow_mode = not follow_mode
        if not follow_mode:
            selected_planet = -1  # Reset to sun view
    
    # Display mode toggle with M key
    if key == b'm' or key == b'M':
        display_mode = (display_mode + 1) % 3
    
    # Planet selection with number keys
    if key >= b'0' and key <= b'8':
        selected_planet = int(key) - 48  # ASCII to int
        if selected_planet > 0:
            follow_mode = True
        else:
            follow_mode = False  # Sun doesn't need follow


def specialKeyListener(key, x, y):
    """
    Handles special key inputs for camera control.
    """
    global camera_pos
    
    # Camera rotation around system
    if key == GLUT_KEY_LEFT:
        # Rotate camera left around z-axis
        angle = math.radians(2)
        x = camera_pos[0] * math.cos(angle) - camera_pos[1] * math.sin(angle)
        y = camera_pos[0] * math.sin(angle) + camera_pos[1] * math.cos(angle)
        camera_pos = (x, y, camera_pos[2])
    
    if key == GLUT_KEY_RIGHT:
        # Rotate camera right around z-axis
        angle = math.radians(-2)
        x = camera_pos[0] * math.cos(angle) - camera_pos[1] * math.sin(angle)
        y = camera_pos[0] * math.sin(angle) + camera_pos[1] * math.cos(angle)
        camera_pos = (x, y, camera_pos[2])
    
    # Camera up/down
    if key == GLUT_KEY_UP:
        # Move camera up (increase z)
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] - 30)
    
    if key == GLUT_KEY_DOWN:
        # Move camera down (decrease z)
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] + 30)
    
    # Camera zoom with Page Up/Down
    if key == GLUT_KEY_PAGE_UP:
        # Zoom in
        camera_pos = (camera_pos[0] * 0.9, camera_pos[1] * 0.9, camera_pos[2] * 0.9)
    
    if key == GLUT_KEY_PAGE_DOWN:
        # Zoom out
        camera_pos = (camera_pos[0] * 1.1, camera_pos[1] * 1.1, camera_pos[2] * 1.1)


def mouseListener(button, state, x, y):
    """
    Handles mouse inputs.
    """
    global selected_planet, follow_mode
    
    # Left mouse button selects/deselects planets
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Implementation would require ray casting which is complex
        # For now, we'll just toggle follow mode
        follow_mode = not follow_mode


def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 1.25, 10, 20000)  # Extended far clip for full solar system
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    if follow_mode and selected_planet >= 0 and selected_planet < len(celestial_data):
        # Calculate the selected planet's position
        planet = celestial_data[selected_planet]
        orbit_radius = planet["orbit_radius"]
        angle_rad = math.radians(orbit_angles[selected_planet])
        
        # Planet position
        planet_x = orbit_radius * math.cos(angle_rad)
        planet_y = orbit_radius * math.sin(angle_rad)
        planet_z = 0
        
        # Calculate camera position based on the planet
        look_distance = planet["radius"] * 5  # Distance from planet
        cam_x = planet_x - look_distance * math.cos(angle_rad)  # Camera position
        cam_y = planet_y - look_distance * math.sin(angle_rad)
        cam_z = look_distance * 2  # Camera height
        
        # Position camera to look at the planet
        gluLookAt(cam_x, cam_y, cam_z,  # Camera position
                  planet_x, planet_y, planet_z,  # Look-at target
                  0, 0, 1)  # Up vector (z-axis)
    else:
        # Standard camera position
        x, y, z = camera_pos
        # Position the camera and set its orientation
        gluLookAt(x, y, z,  # Camera position
                  0, 0, 0,  # Look-at target (sun)
                  0, 0, 1)  # Up vector (z-axis)


def idle():
    """
    Idle function that runs continuously to update planet positions.
    """
    global orbit_angles, rotation_angles, comet
    
    if not paused:
        # Update planet orbit and rotation angles
        for i in range(len(celestial_data)):
            # Update orbit angle
            orbit_angles[i] += celestial_data[i]["orbit_speed"] * time_scale
            if orbit_angles[i] >= 360:
                orbit_angles[i] -= 360
            
            # Update rotation angle
            rotation_angles[i] += celestial_data[i]["rotation_speed"] * time_scale
            if rotation_angles[i] >= 360:
                rotation_angles[i] -= 360
        
        # Update comet position
        comet["angle"] += comet["speed"] * time_scale
        if comet["angle"] >= 360:
            comet["angle"] -= 360
    
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()


def showScreen():
    """
    Display function to render the solar system scene.
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    
    # Enable Z-buffer test
    glEnable(GL_DEPTH_TEST)
    
    # Enable lighting effects for sun glow and comet tail
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Set viewport size
    glViewport(0, 0, 1000, 800)

    setupCamera()  # Configure camera perspective

    # Draw all celestial bodies and effects
    draw_shapes()
    
    # Disable depth test and blend for UI elements
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_BLEND)
    
    # Display simulation info
    draw_text(10, 770, f"Solar System Simulation")
    draw_text(10, 740, f"Time Scale: x{time_scale:.1f}")
    
    # Display status info
    status = "PAUSED" if paused else "RUNNING"
    draw_text(10, 710, f"Status: {status}")
    
    # Display selected planet
    if selected_planet == -1:
        planet_name = "Sun"
    else:
        planet_name = celestial_data[selected_planet]["name"]
    
    draw_text(10, 680, f"Selected: {planet_name}")
    
    # Display mode info
    mode_names = ["Full System", "Inner Planets", "Selected Planet"]
    draw_text(10, 650, f"Mode: {mode_names[display_mode]}")
    
    # Display controls
    draw_text(700, 770, "Controls:")
    draw_text(700, 740, "P: Pause/Resume")
    draw_text(700, 710, "+/-: Change speed")
    draw_text(700, 680, "Arrow keys: Move camera")
    draw_text(700, 650, "W/S: Zoom in/out")
    draw_text(700, 620, "0-8: Select object")
    draw_text(700, 590, "F: Toggle follow mode")
    draw_text(700, 560, "O: Toggle orbits")
    draw_text(700, 530, "M: Change display mode")
    
    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"Solar System Simulator")  # Create the window

    # Set background color to dark blue (space)
    glClearColor(0.0, 0.0, 0.1, 1.0)
    
    # Enable alpha blending for sun glow and comet tail
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)  # Register special key listener
    glutMouseFunc(mouseListener)  # Register mouse listener
    glutIdleFunc(idle)  # Register the idle function for continuous updates

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()