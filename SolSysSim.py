from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Camera-related variables
camera_pos = (0, 0, 1500)  # Position camera further back
camera_rotation = [0, 0]   # Camera rotation angles
zoom_level = 1.0           # Camera zoom level

# Solar system simulation variables
paused = False             # Pause state
time_scale = 1.0           # Simulation speed
selected_planet = 0        # Currently selected planet (0 = Sun)
follow_mode = False        # Camera follows selected planet
show_trails = True         # Show orbital trails
inner_planets_only = False # Show only inner planets

fovY = 60                  # Field of view
GRID_LENGTH = 2000         # Length of grid lines
rand_var = 423

# Planet data - [radius, distance from sun, orbit speed, rotation speed, axial tilt, color, moons]
planet_data = [
    [150, 0, 0, 0.2, 0, (1.0, 0.8, 0.0)],  # Sun
    [25, 300, 4.8, 0.5, 0, (0.8, 0.6, 0.6)],  # Mercury
    [45, 500, 3.5, 0.3, 4, (0.9, 0.9, 0.7)],  # Venus
    [50, 700, 3.0, 1.0, 23.5, (0.3, 0.5, 1.0)],  # Earth
    [40, 900, 2.4, 0.9, 25, (0.8, 0.4, 0.3)],  # Mars
    [120, 1200, 1.3, 0.4, 3, (0.9, 0.8, 0.6)],  # Jupiter
    [100, 1500, 0.9, 0.5, 27, (0.9, 0.8, 0.5)],  # Saturn
    [80, 1800, 0.7, 0.6, 98, (0.6, 0.8, 0.9)],  # Uranus
    [80, 2100, 0.5, 0.5, 30, (0.4, 0.6, 0.9)]   # Neptune
]

# Moon data - [parent planet index, radius, distance from planet, orbit speed, rotation speed, color]
moon_data = [
    [3, 15, 100, 10.0, 1.0, (0.8, 0.8, 0.8)],  # Earth's moon
    [4, 8, 70, 8.0, 0.8, (0.7, 0.7, 0.7)],     # Mars' moon Phobos
    [4, 5, 90, 6.0, 0.6, (0.6, 0.6, 0.6)],     # Mars' moon Deimos
    [5, 12, 170, 9.0, 0.5, (0.9, 0.9, 0.9)],   # Jupiter's moon Io
    [5, 10, 200, 7.0, 0.4, (0.7, 0.7, 0.7)],   # Jupiter's moon Europa
    [5, 15, 240, 5.0, 0.3, (0.8, 0.8, 0.8)]    # Jupiter's moon Ganymede
]

# Asteroid belt data
asteroid_count = 200
asteroid_data = []  # Will be populated in init_asteroids()

# Comet data
comet_position = [0, 0, 0]
comet_orbit_angle = 0
comet_speed = 1.5
comet_orbit_radius_max = 2500
comet_orbit_radius_min = 400
comet_eccentricity = 0.8
comet_size = 20
comet_tail_length = 200

# Rogue asteroid (for collision demo)
collision_mode = False
rogue_asteroid_position = [-3000, 0, 0]
rogue_asteroid_velocity = [15, 0, 0]
rogue_asteroid_size = 30
collision_happened = False
collision_time = 0
collision_target = 3  # Earth by default

# Orbital trail data
trail_segments = 100
trail_points = []

# Animation angles
orbit_angles = [0] * len(planet_data)
rotation_angles = [0] * len(planet_data)
moon_orbit_angles = [0] * len(moon_data)
moon_rotation_angles = [0] * len(moon_data)

def init_asteroids():
    """Initialize asteroid belt data with random positions and sizes"""
    global asteroid_data
    asteroid_data = []
    for i in range(asteroid_count):
        # Random angle and distance variations
        angle = 2.0 * math.pi * (i / asteroid_count)
        distance = 1050 + 50 * math.sin(i * 7.5)
        size = 5 + 10 * (i % 3) / 3.0
        speed = 1.0 + 0.5 * (i % 5) / 5.0
        asteroid_data.append([angle, distance, size, speed])

def init_trails():
    """Initialize orbital trail points"""
    global trail_points
    trail_points = []
    for p in range(1, len(planet_data)):  # Skip sun
        orbit_radius = planet_data[p][1]
        trail = []
        for i in range(trail_segments):
            angle = 2.0 * math.pi * i / trail_segments
            x = orbit_radius * math.cos(angle)
            y = orbit_radius * math.sin(angle)
            trail.append((x, y))
        trail_points.append(trail)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draw text at screen position (x,y)"""
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

def draw_trails():
    """Draw orbital trails for planets"""
    if not show_trails:
        return
        
    start_planet = 1
    end_planet = 4 if inner_planets_only else len(planet_data) - 1
    
    for p in range(start_planet - 1, end_planet):  # Adjust index for trail_points
        # Get planet color with reduced intensity
        r, g, b = planet_data[p + 1][5]
        glColor3f(r * 0.5, g * 0.5, b * 0.5)
        
        glBegin(GL_LINE_LOOP)
        for point in trail_points[p]:
            glVertex3f(point[0], point[1], 0)
        glEnd()

def draw_sphere(radius, slices, stacks):
    """Draw a sphere using gluSphere (no glEnable calls)"""
    quadric = gluNewQuadric()
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)

def draw_planet_with_day_night(planet_idx, radius, rotation_angle, axial_tilt):
    """Draw a planet with day/night shading"""
    day_color = planet_data[planet_idx][5]
    night_color = (day_color[0] * 0.3, day_color[1] * 0.3, day_color[2] * 0.3)
    
    # Main planet
    glColor3fv(day_color)
    glPushMatrix()
    glRotatef(axial_tilt, 0, 1, 0)  # Apply axial tilt
    glRotatef(rotation_angle, 0, 0, 1)  # Apply rotation
    
    # Draw the day side
    draw_sphere(radius, 20, 20)
    
    # Draw night side with darker color (simple approximation)
    glColor3fv(night_color)
    glRotatef(180, 0, 1, 0)
    draw_sphere(radius, 20, 20)
    
    glPopMatrix()

def draw_sun():
    """Draw the sun with glow effect"""
    # Main sun
    glColor3fv(planet_data[0][5])
    draw_sphere(planet_data[0][0], 30, 30)
    
    # Simple glow effect (concentric spheres with decreasing opacity)
    for i in range(3):
        glPushMatrix()
        glow_radius = planet_data[0][0] * (1.1 + i * 0.1)
        glColor4f(1.0, 0.7, 0.0, 0.3 - i * 0.1)
        draw_sphere(glow_radius, 20, 20)
        glPopMatrix()

def draw_planet_system(planet_idx, orbit_angle, rotation_angle):
    """Draw a planet and its moons"""
    # Get planet data
    radius = planet_data[planet_idx][0]
    distance = planet_data[planet_idx][1]
    axial_tilt = planet_data[planet_idx][2]
    
    # Position at the correct orbital distance
    glPushMatrix()
    glRotatef(orbit_angle, 0, 0, 1)
    glTranslatef(distance, 0, 0)
    
    # For planets (not Sun), draw with day/night effect
    if planet_idx > 0:
        draw_planet_with_day_night(planet_idx, radius, rotation_angle, planet_data[planet_idx][4])
    
    # If this is a selected planet, mark it with a selection indicator
    if selected_planet == planet_idx and not follow_mode:
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)  # Rotate to align with planet equator
        
        # Draw selection indicator (circle around planet)
        glBegin(GL_LINE_LOOP)
        for i in range(36):
            angle = i * 10 * math.pi / 180
            x = (radius + 20) * math.cos(angle)
            y = (radius + 20) * math.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()
        glPopMatrix()
    
    # Draw moons for this planet
    for i, moon in enumerate(moon_data):
        if moon[0] == planet_idx:
            # Get moon data
            moon_radius = moon[1]
            moon_distance = moon[2]
            moon_color = moon[5]
            
            # Draw moon orbit and moon
            glPushMatrix()
            glRotatef(moon_orbit_angles[i], 0, 0, 1)
            glTranslatef(moon_distance, 0, 0)
            
            # Draw moon
            glColor3fv(moon_color)
            glRotatef(moon_rotation_angles[i], 0, 0, 1)
            draw_sphere(moon_radius, 10, 10)
            glPopMatrix()
    
    glPopMatrix()

def draw_asteroids():
    """Draw asteroid belt"""
    if inner_planets_only:
        return
        
    glColor3f(0.6, 0.6, 0.6)
    
    for asteroid in asteroid_data:
        angle = asteroid[0]
        distance = asteroid[1]
        size = asteroid[2]
        
        glPushMatrix()
        glRotatef(angle * 180 / math.pi, 0, 0, 1)
        glTranslatef(distance, 0, 0)
        draw_sphere(size, 4, 4)  # Low poly for better performance
        glPopMatrix()

def draw_comet():
    """Draw comet with tail"""
    if inner_planets_only:
        return
        
    # Calculate comet position based on orbit parameters
    r = comet_orbit_radius_min / (1 - comet_eccentricity * math.cos(comet_orbit_angle))
    x = r * math.cos(comet_orbit_angle)
    y = r * math.sin(comet_orbit_angle)
    comet_position[0] = x
    comet_position[1] = y
    
    # Draw comet
    glPushMatrix()
    glTranslatef(x, y, 0)
    
    # Comet body
    glColor3f(0.8, 0.8, 1.0)
    draw_sphere(comet_size, 10, 10)
    
    # Comet tail (pointing away from sun)
    angle = math.atan2(y, x)
    tail_x = -math.cos(angle) * comet_tail_length
    tail_y = -math.sin(angle) * comet_tail_length
    
    glBegin(GL_TRIANGLE_FAN)
    glColor4f(0.8, 0.8, 1.0, 0.8)
    glVertex3f(0, 0, 0)
    glColor4f(0.8, 0.8, 1.0, 0.0)
    
    # Draw tail as a fan of triangles
    for i in range(11):
        angle_offset = (i - 5) * math.pi / 30
        offset_x = math.sin(angle_offset) * comet_size * 2
        offset_y = math.cos(angle_offset) * comet_size * 2
        glVertex3f(tail_x + offset_x, tail_y + offset_y, 0)
    glEnd()
    
    glPopMatrix()

def draw_rogue_asteroid():
    """Draw the rogue asteroid for collision demo"""
    if not collision_mode:
        return
        
    # Check if collision has occurred
    global collision_happened, collision_time
    if collision_happened:
        # If collision animation is done, reset
        if glutGet(GLUT_ELAPSED_TIME) - collision_time > 2000:
            collision_happened = False
            rogue_asteroid_position[0] = -3000
            rogue_asteroid_velocity[0] = 15
        else:
            # Draw explosion
            glPushMatrix()
            glTranslatef(rogue_asteroid_position[0], rogue_asteroid_position[1], 0)
            
            # Explosion size grows with time
            time_since = (glutGet(GLUT_ELAPSED_TIME) - collision_time) / 1000.0
            explosion_size = rogue_asteroid_size * (2.0 + time_since * 5)
            
            # Explosion color transitions from white to red to transparent
            alpha = 1.0 - time_since / 2.0
            if alpha < 0: alpha = 0
            
            glColor4f(1.0, 1.0 - time_since/2.0, 0.0, alpha)
            draw_sphere(explosion_size, 20, 20)
            glPopMatrix()
            return
    
    # Draw the asteroid
    glPushMatrix()
    glTranslatef(rogue_asteroid_position[0], rogue_asteroid_position[1], 0)
    glColor3f(0.5, 0.3, 0.3)
    draw_sphere(rogue_asteroid_size, 10, 10)
    glPopMatrix()

def draw_planet_label(planet_idx):
    """Draw label for the currently selected planet"""
    if planet_idx < 0 or planet_idx >= len(planet_data):
        return
        
    names = ["Sun", "Mercury", "Venus", "Earth", "Mars", 
             "Jupiter", "Saturn", "Uranus", "Neptune"]
    
    label = f"Selected: {names[planet_idx]}"
    draw_text(10, 720, label)

def draw_simulation_controls():
    """Draw simulation controls and status"""
    draw_text(10, 770, f"Time Scale: {time_scale:.1f}x" + (" (PAUSED)" if paused else ""))
    
    if follow_mode:
        draw_text(10, 690, "Camera: Follow Mode")
    else:
        draw_text(10, 690, "Camera: Free Mode")
        
    if collision_mode:
        draw_text(10, 660, "Collision Demo: ON")
    
    if inner_planets_only:
        draw_text(10, 630, "View: Inner Planets Only")
    else:
        draw_text(10, 630, "View: Full Solar System")
        
    draw_text(10, 600, "Trails: " + ("ON" if show_trails else "OFF"))
    
    # Help text
    draw_text(10, 80, "Controls:")
    draw_text(10, 60, "Arrow keys: Rotate camera  |  W/S: Zoom  |  P: Pause  |  R: Reset")
    draw_text(10, 40, "1-9: Select planet  |  F: Follow mode  |  O: Toggle trails  |  +/-: Time scale")
    draw_text(10, 20, "C: Toggle collision demo  |  I: Inner planets only")

def draw_solar_system():
    """Draw the complete solar system"""
    # Draw orbital trails
    draw_trails()
    
    # Draw the sun
    glPushMatrix()
    draw_sun()
    glPopMatrix()
    
    # Draw planets
    end_planet = 4 if inner_planets_only else len(planet_data)
    for i in range(1, end_planet):
        draw_planet_system(i, orbit_angles[i], rotation_angles[i])
    
    # Draw asteroid belt
    draw_asteroids()
    
    # Draw comet
    draw_comet()
    
    # Draw rogue asteroid
    draw_rogue_asteroid()

def keyboardListener(key, x, y):
    """Handles keyboard inputs"""
    global paused, time_scale, selected_planet, follow_mode, show_trails, inner_planets_only, collision_mode
    
    # Pause/Resume (P key)
    if key == b'p':
        paused = not paused
    
    # Reset simulation (R key)
    if key == b'r':
        reset_simulation()
    
    # Toggle follow mode (F key)
    if key == b'f':
        follow_mode = not follow_mode
    
    # Toggle orbital trails (O key)
    if key == b'o':
        show_trails = not show_trails
    
    # Toggle inner planets only (I key)
    if key == b'i':
        inner_planets_only = not inner_planets_only
    
    # Toggle collision demo (C key)
    if key == b'c':
        collision_mode = not collision_mode
        if collision_mode:
            # Reset the rogue asteroid
            rogue_asteroid_position[0] = -3000
            rogue_asteroid_position[1] = 0
            rogue_asteroid_velocity[0] = 15
            rogue_asteroid_velocity[1] = 0
            collision_happened = False
    
    # Increase time scale (+ key)
    if key == b'+':
        time_scale += 0.5
        if time_scale > 10.0:
            time_scale = 10.0
    
    # Decrease time scale (- key)
    if key == b'-':
        time_scale -= 0.5
        if time_scale < 0.5:
            time_scale = 0.5
    
    # Select planet (1-9 keys)
    if key >= b'1' and key <= b'9':
        selected_planet = int(key) - int(b'1')
        if selected_planet >= len(planet_data):
            selected_planet = len(planet_data) - 1
    
    # Zoom in (W key)
    if key == b'w':
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] * 0.9)
    
    # Zoom out (S key)
    if key == b's':
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] * 1.1)

def specialKeyListener(key, x, y):
    """Handles special key inputs (arrow keys)"""
    global camera_rotation
    
    # Rotate camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        camera_rotation[0] -= 5
    
    # Rotate camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        camera_rotation[0] += 5
    
    # Rotate camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_rotation[1] += 5
        if camera_rotation[1] > 80:
            camera_rotation[1] = 80
    
    # Rotate camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_rotation[1] -= 5
        if camera_rotation[1] < -80:
            camera_rotation[1] = -80
    
    # Zoom in (PAGE UP)
    if key == GLUT_KEY_PAGE_UP:
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] * 0.9)
    
    # Zoom out (PAGE DOWN)
    if key == GLUT_KEY_PAGE_DOWN:
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] * 1.1)

def mouseListener(button, state, x, y):
    """Handles mouse inputs"""
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Left mouse button could be used for selecting planets
        pass
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Right mouse button could toggle follow mode
        pass

def setupCamera():
    """Configures the camera's projection and view settings"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 10, 10000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Get the position of the selected planet for camera tracking
    if follow_mode and selected_planet > 0:
        planet_distance = planet_data[selected_planet][1]
        planet_angle = orbit_angles[selected_planet]
        
        # Calculate planet position
        planet_x = planet_distance * math.cos(math.radians(planet_angle))
        planet_y = planet_distance * math.sin(math.radians(planet_angle))
        
        # Position camera to look at the planet
        orbit_radius = planet_distance * 2
        cam_x = planet_x + orbit_radius * math.cos(math.radians(camera_rotation[0]))
        cam_y = planet_y + orbit_radius * math.sin(math.radians(camera_rotation[0]))
        cam_z = orbit_radius * math.sin(math.radians(camera_rotation[1]))
        
        gluLookAt(cam_x, cam_y, cam_z,  # Camera position
                  planet_x, planet_y, 0,  # Look-at target (planet)
                  0, 0, 1)  # Up vector (z-axis)
    else:
        # Regular free camera
        cam_x = camera_pos[2] * math.cos(math.radians(camera_rotation[1])) * math.cos(math.radians(camera_rotation[0]))
        cam_y = camera_pos[2] * math.cos(math.radians(camera_rotation[1])) * math.sin(math.radians(camera_rotation[0]))
        cam_z = camera_pos[2] * math.sin(math.radians(camera_rotation[1]))
        
        gluLookAt(cam_x, cam_y, cam_z,  # Camera position
                  0, 0, 0,  # Look-at target (origin)
                  0, 0, 1)  # Up vector (z-axis)

def update_simulation():
    """Update positions and angles for all celestial bodies"""
    if paused:
        return
    
    # Update planet orbits and rotations
    for i in range(1, len(planet_data)):  # Skip sun
        orbit_angles[i] += planet_data[i][2] * time_scale
        rotation_angles[i] += planet_data[i][3] * time_scale
        
        # Keep angles in range [0, 360]
        if orbit_angles[i] >= 360:
            orbit_angles[i] -= 360
        if rotation_angles[i] >= 360:
            rotation_angles[i] -= 360
    
    # Update sun's rotation
    rotation_angles[0] += planet_data[0][3] * time_scale
    if rotation_angles[0] >= 360:
        rotation_angles[0] -= 360
    
    # Update moon orbits and rotations
    for i in range(len(moon_data)):
        moon_orbit_angles[i] += moon_data[i][3] * time_scale
        moon_rotation_angles[i] += moon_data[i][4] * time_scale
        
        # Keep angles in range [0, 360]
        if moon_orbit_angles[i] >= 360:
            moon_orbit_angles[i] -= 360
        if moon_rotation_angles[i] >= 360:
            moon_rotation_angles[i] -= 360
    
    # Update asteroid angles
    for i in range(len(asteroid_data)):
        asteroid_data[i][0] += 0.001 * asteroid_data[i][3] * time_scale
        if asteroid_data[i][0] >= 2 * math.pi:
            asteroid_data[i][0] -= 2 * math.pi
    
    # Update comet position
    global comet_orbit_angle
    # Speed of comet varies with distance (Kepler's law)
    r = comet_orbit_radius_min / (1 - comet_eccentricity * math.cos(comet_orbit_angle))
    speed_factor = (comet_orbit_radius_max / r) ** 2  # Inverse square law
    comet_orbit_angle += 0.005 * comet_speed * speed_factor * time_scale
    if comet_orbit_angle >= 2 * math.pi:
        comet_orbit_angle -= 2 * math.pi
    
    # Update rogue asteroid position (collision demo)
    if collision_mode and not collision_happened:
        rogue_asteroid_position[0] += rogue_asteroid_velocity[0] * time_scale
        rogue_asteroid_position[1] += rogue_asteroid_velocity[1] * time_scale
        
        # Check for collision with target planet
        planet_distance = planet_data[collision_target][1]
        planet_angle = math.radians(orbit_angles[collision_target])
        planet_x = planet_distance * math.cos(planet_angle)
        planet_y = planet_distance * math.sin(planet_angle)
        
        dx = rogue_asteroid_position[0] - planet_x
        dy = rogue_asteroid_position[1] - planet_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < planet_data[collision_target][0] + rogue_asteroid_size:
            # Collision detected
            collision_happened = True
            collision_time = glutGet(GLUT_ELAPSED_TIME)

def reset_simulation():
    """Reset the simulation to initial state"""
    global orbit_angles, rotation_angles, moon_orbit_angles, moon_rotation_angles
    global time_scale, selected_planet, follow_mode, paused
    global rogue_asteroid_position, collision_happened
    
    # Reset angles
    orbit_angles = [0] * len(planet_data)
    rotation_angles = [0] * len(planet_data)
    moon_orbit_angles = [0] * len(moon_data)
    moon_rotation_angles = [0] * len(moon_data)
    
    # Reset camera and simulation settings
    time_scale = 1.0
    selected_planet = 0
    follow_mode = False
    paused = False
    
    # Reset collision demo
    rogue_asteroid_position[0] = -3000
    rogue_asteroid_position[1] = 0
    collision_happened = False

def idle():
    """Idle function that runs continuously"""
    update_simulation()
    glutPostRedisplay()

def showScreen():
    """Display function to render the game scene"""
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    # Draw the solar system
    draw_solar_system()
    
    # Draw UI elements
    draw_planet_label(selected_planet)
    draw_simulation_controls()
    
    # Swap buffers
    glutSwapBuffers()

def init():
    """Initialize solar system data"""
    init_asteroids()
    init_trails()
    reset_simulation()

# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Solar System Simulation")
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    init()
    glutMainLoop()

if __name__ == "__main__":
    main()t camera and simulation settings
    time_scale = 1.0
    selected_planet = 0
    follow_mode = False
    paused = False
    
    # Reset collision demo
    rogue_asteroid_position[0] = -3000
    rogue_asteroid_position[1] = 0
    collision_happened = False

def idle():
    """Idle function that runs continuously"""
    update_simulation()
    glutPostRedisplay()

def showScreen():
    """Display function to render the game scene"""
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    # Draw the solar system
    draw_solar_system()
    
    # Draw UI elements
    draw_planet_label(selected_planet)
    draw_simulation_controls()
    
    # Swap buffers
    glutSwapBuffers()

def init():
    """Initialize solar system data"""
    init_asteroids()
    init_trails()
    reset_simulation()

# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Solar System Simulation")
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    init()
    glutMainLoop()

if __name__ == "__main__":
    main()