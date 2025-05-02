from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Camera variables (from template)
camera_distance = 1500
camera_pos = (0, 1500, 1500)
fovY = 60
GRID_LENGTH = 4000

# Simulation variables
paused = False
time_scale = 1.0
selected_planet = 0
follow_mode = False
show_trails = True
inner_planets_only = False
camera_rotation = [0, 0]

# Planet destruction variables
explosion_particles = []
destroyed_planets = []
attack_asteroid = None
explosion_lifetime = 100  # How long explosions last
attack_animation = 0  # Animation counter for attacks

# Celestial body data (colors adjusted for better visibility)
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

moon_data = [
    [3, 15, 100, 10.0, 1.0, (0.8, 0.8, 0.8)],  # Earth's moon
    [4, 8, 70, 8.0, 0.8, (0.7, 0.7, 0.7)],     # Mars' moon Phobos
    [4, 5, 90, 6.0, 0.6, (0.6, 0.6, 0.6)],     # Mars' moon Deimos
    [5, 12, 170, 9.0, 0.5, (0.9, 0.9, 0.9)],   # Jupiter's moon Io
    [5, 10, 200, 7.0, 0.4, (0.7, 0.7, 0.7)],   # Jupiter's moon Europa
    [5, 15, 240, 5.0, 0.3, (0.8, 0.8, 0.8)]    # Jupiter's moon Ganymede
]

asteroid_count = 200
asteroid_data = []
comet_position = [0, 0, 0]
comet_orbit_angle = 0
comet_speed = 1.5
comet_orbit_radius_max = 2500
comet_orbit_radius_min = 400
comet_eccentricity = 0.8
comet_size = 20
comet_tail_length = 200
trail_segments = 100
trail_points = []
orbit_angles = [0] * len(planet_data)
rotation_angles = [0] * len(planet_data)
moon_orbit_angles = [0] * len(moon_data)
moon_rotation_angles = [0] * len(moon_data)

def init_asteroids():
    global asteroid_data
    asteroid_data = []
    for i in range(asteroid_count):
        angle = 2.0 * math.pi * (i / asteroid_count)
        distance = 1050 + 50 * math.sin(i * 7.5)
        size = 5 + 10 * (i % 3) / 3.0
        speed = 1.0 + 0.5 * (i % 5) / 5.0
        asteroid_data.append([angle, distance, size, speed])

def init_trails():
    global trail_points
    trail_points = []
    for p in range(1, len(planet_data)):
        orbit_radius = planet_data[p][1]
        trail = []
        for i in range(trail_segments):
            angle = 2.0 * math.pi * i / trail_segments
            x = orbit_radius * math.cos(angle)
            y = orbit_radius * math.sin(angle)
            trail.append((x, y))
        trail_points.append(trail)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
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
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_trails():
    if not show_trails: return
    
    start_planet = 1
    end_planet = 4 if inner_planets_only else len(planet_data) - 1
    
    for p in range(start_planet - 1, end_planet):
        # Skip if the planet is destroyed
        if p + 1 in destroyed_planets:
            continue
            
        r, g, b = planet_data[p + 1][5]
        glColor3f(r * 0.5, g * 0.5, b * 0.5)
        glBegin(GL_LINE_LOOP) 
        for point in trail_points[p]:
            glVertex3f(point[0], point[1], 0)
        glEnd()

def draw_sphere(radius, slices, stacks):
    gluSphere(gluNewQuadric(), radius, slices, stacks)

def draw_planet(planet_idx, radius, rotation_angle, axial_tilt):
    glPushMatrix()
    glRotatef(axial_tilt, 0, 1, 0)
    glRotatef(rotation_angle, 0, 0, 1)
    glColor3fv(planet_data[planet_idx][5])
    draw_sphere(radius, 20, 20)
    glPopMatrix()

def draw_sun():
    glColor3f(*planet_data[0][5])
    draw_sphere(planet_data[0][0], 30, 30)

def draw_planet_system(planet_idx, orbit_angle, rotation_angle):
    # Skip if the planet is destroyed
    if planet_idx in destroyed_planets:
        return
        
    radius = planet_data[planet_idx][0]
    distance = planet_data[planet_idx][1]
    axial_tilt = planet_data[planet_idx][4]
    
    glPushMatrix()
    glRotatef(orbit_angle, 0, 0, 1)
    glTranslatef(distance, 0, 0)
    
    if planet_idx > 0:
        draw_planet(planet_idx, radius, rotation_angle, axial_tilt)
    
    if selected_planet == planet_idx and not follow_mode:
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        gluDisk(gluNewQuadric(), radius + 20, radius + 25, 36, 1)
        glPopMatrix()
    
    for i, moon in enumerate(moon_data):
        if moon[0] == planet_idx:
            moon_radius = moon[1]
            moon_distance = moon[2]
            moon_color = moon[5]
            
            glPushMatrix()
            glRotatef(moon_orbit_angles[i], 0, 0, 1)
            glTranslatef(moon_distance, 0, 0)
            glColor3fv(moon_color)
            glRotatef(moon_rotation_angles[i], 0, 0, 1)
            draw_sphere(moon_radius, 10, 10)
            glPopMatrix()
    
    glPopMatrix()

def draw_asteroids():
    if inner_planets_only: return
    
    glColor3f(0.6, 0.6, 0.6)
    for asteroid in asteroid_data:
        angle = asteroid[0]
        distance = asteroid[1]
        size = asteroid[2]
        
        glPushMatrix()
        glRotatef(angle * 180 / math.pi, 0, 0, 1)
        glTranslatef(distance, 0, 0)
        draw_sphere(size, 4, 4)
        glPopMatrix()
        
    # Draw the attacking asteroid if active
    if attack_asteroid:
        target_idx, start_pos, end_pos, progress = attack_asteroid
        
        # Calculate current position using linear interpolation
        current_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
        current_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
        
        glPushMatrix()
        glTranslatef(current_x, current_y, 0)
        
        # Make the attacking asteroid red and larger
        glColor3f(1.0, 0.2, 0.0)
        draw_sphere(30, 8, 8)
        
        # Draw a tail behind the asteroid
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.5, 0.0)
        glVertex3f(0, 0, 0)
        glColor3f(1.0, 0.3, 0.0)
        direction_x = start_pos[0] - end_pos[0]
        direction_y = start_pos[1] - end_pos[1]
        length = math.sqrt(direction_x**2 + direction_y**2)
        normalized_x = direction_x / length * 100
        normalized_y = direction_y / length * 100
        
        glVertex3f(normalized_x - normalized_y*0.5, normalized_y + normalized_x*0.5, 0)
        glColor3f(1.0, 0.1, 0.0)
        glVertex3f(normalized_x + normalized_y*0.5, normalized_y - normalized_x*0.5, 0)
        glEnd()
        
        glPopMatrix()

def draw_explosion_particles():
    for particle in explosion_particles:
        pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, size, life, color = particle
        
        alpha = min(1.0, life / explosion_lifetime)
        
        glPushMatrix()
        glTranslatef(pos_x, pos_y, pos_z)
        glColor4f(color[0], color[1], color[2], alpha)
        draw_sphere(size, 4, 4)
        glPopMatrix()

def draw_comet():
    if inner_planets_only: return
    
    r = comet_orbit_radius_min / (1 - comet_eccentricity * math.cos(comet_orbit_angle))
    x = r * math.cos(comet_orbit_angle)
    y = r * math.sin(comet_orbit_angle)
    comet_position[0] = x
    comet_position[1] = y
    
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.8, 0.8, 1.0)
    draw_sphere(comet_size, 10, 10)
    glPopMatrix()

def draw_planet_label(planet_idx):
    names = ["Sun", "Mercury", "Venus", "Earth", "Mars", 
             "Jupiter", "Saturn", "Uranus", "Neptune"]
    if 0 <= planet_idx < len(names):
        if planet_idx in destroyed_planets:
            draw_text(10, 720, f"Selected: {names[planet_idx]} (DESTROYED)")
        else:
            draw_text(10, 720, f"Selected: {names[planet_idx]}")

def draw_simulation_controls():
    draw_text(10, 770, f"Time Scale: {time_scale:.1f}x" + (" (PAUSED)" if paused else ""))
    draw_text(10, 690, "Camera: Follow Mode" if follow_mode else "Camera: Free Mode")
    draw_text(10, 630, "View: Inner Planets Only" if inner_planets_only else "View: Full Solar System")
    draw_text(10, 600, "Trails: " + ("ON" if show_trails else "OFF"))
    
    if len(destroyed_planets) > 0:
        destroyed_names = []
        for idx in destroyed_planets:
            if idx > 0 and idx < len(planet_data):
                planet_names = ["Sun", "Mercury", "Venus", "Earth", "Mars", 
                               "Jupiter", "Saturn", "Uranus", "Neptune"]
                destroyed_names.append(planet_names[idx])
        
        draw_text(10, 570, f"Destroyed: {', '.join(destroyed_names)}")
    
    draw_text(10, 80, "Controls:")
    draw_text(10, 60, "Arrow keys: Rotate camera  |  W/S: Zoom  |  P: Pause  |  R: Reset")
    draw_text(10, 40, "1-9: Select planet  |  F: Follow mode  |  O: Toggle trails  |  +/-: Time scale")
    draw_text(10, 20, "I: Inner planets only  |  U: Destroy random planet")

def draw_solar_system():
    draw_trails()
    glPushMatrix()
    draw_sun()
    glPopMatrix()
    
    end_planet = 4 if inner_planets_only else len(planet_data)
    for i in range(1, end_planet):
        draw_planet_system(i, orbit_angles[i], rotation_angles[i])
    
    draw_asteroids()
    draw_comet()
    draw_explosion_particles()

def create_explosion(position_x, position_y, planet_radius):
    global explosion_particles
    
    # Create particles
    num_particles = 50
    for i in range(num_particles):
        # Random direction
        angle_h = random.uniform(0, 2*math.pi)
        angle_v = random.uniform(-1, 1)
        
        # Calculate velocity vector
        speed = random.uniform(5, 15)
        vel_x = speed * math.cos(angle_h) * math.sqrt(1 - angle_v**2)
        vel_y = speed * math.sin(angle_h) * math.sqrt(1 - angle_v**2)
        vel_z = speed * angle_v
        
        # Randomize particle size
        size = random.uniform(planet_radius/5, planet_radius/2)
        
        # Set particle colors (yellow, orange, red)
        color_idx = random.randint(0, 2)
        colors = [(1.0, 0.9, 0.1), (1.0, 0.6, 0.0), (1.0, 0.2, 0.0)]
        
        # Add particle to list
        explosion_particles.append([position_x, position_y, 0, vel_x, vel_y, vel_z, size, explosion_lifetime, colors[color_idx]])

def launch_asteroid_attack():
    global attack_asteroid
    
    # Don't launch if already attacking
    if attack_asteroid is not None:
        return
        
    # Find valid targets (exclude Sun and already destroyed planets)
    valid_targets = [i for i in range(1, len(planet_data)) if i not in destroyed_planets]
    
    # Return if no valid targets
    if not valid_targets:
        return
        
    # Select random target
    target_idx = random.choice(valid_targets)
    
    # Calculate target position
    target_angle = math.radians(orbit_angles[target_idx])
    target_distance = planet_data[target_idx][1]
    target_x = target_distance * math.cos(target_angle)
    target_y = target_distance * math.sin(target_angle)
    
    # Starting position for asteroid (outside the view)
    start_angle = random.uniform(0, 2*math.pi)
    start_distance = max([p[1] for p in planet_data]) * 1.5
    start_x = start_distance * math.cos(start_angle)
    start_y = start_distance * math.sin(start_angle)
    
    # Create attack asteroid [target index, start position, end position, progress (0 to 1)]
    attack_asteroid = [target_idx, (start_x, start_y), (target_x, target_y), 0]

def keyboardListener(key, x, y):
    global paused, time_scale, selected_planet, follow_mode, show_trails, inner_planets_only, camera_distance
    
    if key == b'p': paused = not paused
    if key == b'r': 
        reset_simulation()
    if key == b'f': follow_mode = not follow_mode
    if key == b'o': show_trails = not show_trails
    if key == b'i': inner_planets_only = not inner_planets_only
    
    # Destroy a random planet with asteroid
    if key == b'u':
        launch_asteroid_attack()
    
    # Fixed time scale controls
    if key in (b'+', b'='):
        time_scale = min(10.0, round(time_scale + 0.1, 1))  # Fixed max value (was 1.0)
    elif key == b'-':
        time_scale = max(0.1, round(time_scale - 0.1, 1))
    
    if key >= b'1' and key <= b'9':
        planet_idx = int(key) - int(b'1')
        if planet_idx >= len(planet_data):
            planet_idx = len(planet_data) - 1
            
        # Don't select destroyed planets
        if planet_idx in destroyed_planets:
            return
            
        selected_planet = planet_idx
        camera_rotation = [0, 0]
        follow_mode = True
        camera_distance = planet_data[selected_planet][1] * 0.4
    
    if key == b'w': camera_distance = max(500, camera_distance * 0.9)
    if key == b's': camera_distance = min(5000, camera_distance * 1.1)

def reset_simulation():
    global orbit_angles, rotation_angles, moon_orbit_angles, moon_rotation_angles, time_scale
    global selected_planet, follow_mode, paused, destroyed_planets, explosion_particles, attack_asteroid
    global camera_rotation, camera_distance
    
    orbit_angles = [0] * len(planet_data)
    rotation_angles = [0] * len(planet_data)
    moon_orbit_angles = [0] * len(moon_data)
    moon_rotation_angles = [0] * len(moon_data)
    time_scale = 1.0
    selected_planet = 0
    follow_mode = False
    paused = False
    destroyed_planets = []
    explosion_particles = []
    attack_asteroid = None
    camera_rotation = [0, 0]
    camera_distance = 1500

def specialKeyListener(key, x, y):
    global camera_rotation
    rotate_amount = 2
    
    if key == GLUT_KEY_LEFT: 
        camera_rotation[0] = (camera_rotation[0] - rotate_amount) % 360
    elif key == GLUT_KEY_RIGHT: 
        camera_rotation[0] = (camera_rotation[0] + rotate_amount) % 360
    elif key == GLUT_KEY_UP: 
        camera_rotation[1] = min(80, camera_rotation[1] + rotate_amount)
    elif key == GLUT_KEY_DOWN: 
        camera_rotation[1] = max(-80, camera_rotation[1] - rotate_amount)
    
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    pass

def setupCamera():
    global follow_mode
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 50000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Check if selected planet is valid and not destroyed
    if follow_mode and 0 <= selected_planet < len(planet_data):
        # Don't follow destroyed planets - switch to free camera
        if selected_planet in destroyed_planets:
            follow_mode = False
            # Use free camera setup instead of recursively calling setupCamera
            rad_h = math.radians(camera_rotation[0])
            rad_v = math.radians(camera_rotation[1])
            eye_x = camera_distance * math.cos(rad_h) * math.cos(rad_v)
            eye_y = camera_distance * math.sin(rad_h) * math.cos(rad_v)
            eye_z = camera_distance * math.sin(rad_v)
            gluLookAt(eye_x, eye_y, eye_z, 0, 0, 0, 0, 0, 1)
            return
            
        planet = planet_data[selected_planet]
        orbit_angle = math.radians(orbit_angles[selected_planet])
        distance = planet[1]
        planet_x = distance * math.cos(orbit_angle)
        planet_y = distance * math.sin(orbit_angle)
        
        theta = math.radians(camera_rotation[0])
        phi = math.radians(camera_rotation[1])
        
        eye_x = planet_x + camera_distance * math.cos(theta) * math.cos(phi)
        eye_y = planet_y + camera_distance * math.sin(theta) * math.cos(phi)
        eye_z = camera_distance * math.sin(phi)
        
        gluLookAt(eye_x, eye_y, eye_z,
                  planet_x, planet_y, 0,
                  0, 0, 1)
    else:
        rad_h = math.radians(camera_rotation[0])
        rad_v = math.radians(camera_rotation[1])
        eye_x = camera_distance * math.cos(rad_h) * math.cos(rad_v)
        eye_y = camera_distance * math.sin(rad_h) * math.cos(rad_v)
        eye_z = camera_distance * math.sin(rad_v)
        gluLookAt(eye_x, eye_y, eye_z, 0, 0, 0, 0, 0, 1)

def update_explosion_particles():
    global explosion_particles
    
    for i in range(len(explosion_particles) - 1, -1, -1):
        particle = explosion_particles[i]
        pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, size, life, color = particle
        
        # Update position
        pos_x += vel_x
        pos_y += vel_y
        pos_z += vel_z
        
        # Update life
        life -= 1
        
        if life <= 0:
            explosion_particles.pop(i)
        else:
            explosion_particles[i] = [pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, size, life, color]

def update_asteroid_attack():
    global attack_asteroid, destroyed_planets, selected_planet, follow_mode
    
    if attack_asteroid is None:
        return
        
    target_idx, start_pos, end_pos, progress = attack_asteroid
    
    # Update progress
    progress += 0.02
    attack_asteroid[3] = progress
    
    # Check if asteroid reached target
    if progress >= 1.0:
        # Calculate position of planet for explosion
        orbit_angle = math.radians(orbit_angles[target_idx])
        orbit_radius = planet_data[target_idx][1]
        planet_x = orbit_radius * math.cos(orbit_angle)
        planet_y = orbit_radius * math.sin(orbit_angle)
        
        # Create explosion at planet position
        create_explosion(planet_x, planet_y, planet_data[target_idx][0])
        
        # Mark planet as destroyed
        if target_idx not in destroyed_planets:
            destroyed_planets.append(target_idx)
        
        # If the selected planet is destroyed, switch to free camera mode
        if selected_planet == target_idx:
            follow_mode = False
        
        # Remove asteroid
        attack_asteroid = None

def update_simulation():
    global comet_orbit_angle, orbit_angles, rotation_angles, moon_orbit_angles, moon_rotation_angles
    
    if paused: return
    
    # Update explosion particles
    update_explosion_particles()
    
    # Update asteroid attack
    update_asteroid_attack()
    
    # Update planet orbits and rotations
    for i in range(1, len(planet_data)):
        if i not in destroyed_planets:  # Only update planets that haven't been destroyed
            orbit_angles[i] = (orbit_angles[i] + planet_data[i][2] * time_scale) % 360
            rotation_angles[i] = (rotation_angles[i] + planet_data[i][3] * time_scale) % 360
    
    rotation_angles[0] = (rotation_angles[0] + planet_data[0][3] * time_scale) % 360
    
    # Update moons of remaining planets
    for i in range(len(moon_data)):
        parent_planet = moon_data[i][0]
        if parent_planet not in destroyed_planets:  # Only update moons if their parent planet exists
            moon_orbit_angles[i] = (moon_orbit_angles[i] + moon_data[i][3] * time_scale) % 360
            moon_rotation_angles[i] = (moon_rotation_angles[i] + moon_data[i][4] * time_scale) % 360
    
    # Update asteroids
    for asteroid in asteroid_data:
        asteroid[0] = (asteroid[0] + 0.001 * asteroid[3] * time_scale) % (2 * math.pi)
    
    # Update comet
    r = comet_orbit_radius_min / (1 - comet_eccentricity * math.cos(comet_orbit_angle))
    comet_orbit_angle = (comet_orbit_angle + 0.005 * comet_speed * (comet_orbit_radius_max / r) ** 2 * time_scale) % (2 * math.pi)

def idle():
    update_simulation()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    # Enable blending for explosion particles
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.2, 0.2)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(0, GRID_LENGTH, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(-GRID_LENGTH, 0, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(0, -GRID_LENGTH, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(GRID_LENGTH, 0, 0)
    glEnd()
    
    setupCamera()
    draw_solar_system()
    draw_planet_label(selected_planet)
    draw_simulation_controls()
    
    # Disable blending after drawing
    glDisable(GL_BLEND)
    
    glutSwapBuffers()

def init():
    init_asteroids()
    init_trails()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Solar System Simulation")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    init()
    glutMainLoop()

if __name__ == "__main__":
    main()