from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math,random

# Camera variables
camera_pos = (0, 0, 1500)
camera_distance = 1500
camera_rotation = [0, 0]
fovY = 60
GRID_LENGTH = 4000

# Simulation variables
simulation_time = 0.0  # Tracks total elapsed time in secon
paused = False
time_scale = 1.0
selected_planet = 0
follow_mode = False
show_trails = True
inner_planets_only = False

#planet facts
planet_facts = [
    [  # Sun
        "The Sun contains 99.86% of the mass in the solar system",
        "Surface temperature: 5,500°C",
        "Core temperature: 15 million°C",
        "Diameter: 1.4 million km (109x Earth)",
        "The Sun is actually white, not yellow"
    ],
    [  # Mercury
        "Closest planet to the Sun",
        "Temperature range: -173°C to 427°C",
        "No atmosphere, no moons",
        "Day length: 59 Earth days",
        "Year length: 88 Earth days"
    ],
    [  # Venus
        "Hottest planet (462°C surface)",
        "Toxic atmosphere of carbon dioxide",
        "Rotates backwards compared to other planets",
        "Similar size to Earth (95% of Earth's diameter)",
        "Day is longer than its year (243 vs 225 Earth days)"
    ],
    [  # Earth
        "Only known planet with liquid water and life",
        "Atmosphere: 78% nitrogen, 21% oxygen",
        "Distance from Sun: 149.6 million km",
        "One moon, 24-hour day",
        "Magnetic field protects from solar radiation"
    ],
    [  # Mars
        "Known as the Red Planet",
        "Has the largest volcano in the solar system",
        "Two small moons: Phobos and Deimos",
        "Evidence of ancient water flows",
        "Day length: 24.6 Earth hours"
    ],
    [  # Jupiter
        "Largest planet in our solar system",
        "More than twice as massive as all other planets combined",
        "Great Red Spot: storm raging for 400+ years",
        "Has at least 79 moons",
        "Day length: 9.93 Earth hours"
    ],
    [  # Saturn
        "Famous for its spectacular ring system",
        "Least dense planet (would float in water)",
        "Has 82+ moons including Titan",
        "Composed mainly of hydrogen and helium",
        "Winds up to 1,800 km/h at equator"
    ],
    [  # Uranus
        "Rotates on its side (axial tilt of 98°)",
        "Appears blue-green due to methane",
        "Coldest planetary atmosphere (-224°C)",
        "27 known moons",
        "Takes 84 Earth years to orbit the Sun"
    ],
    [  # Neptune
        "Windiest planet (winds up to 2,100 km/h)",
        "Discovered by mathematical predictions",
        "The Great Dark Spot is a storm system",
        "14 known moons",
        "Takes 165 Earth years to orbit the Sun"
    ]
]

def draw_planet_facts(planet_idx):    
    if 0 <= planet_idx < len(planet_facts):
        
        names = ["Sun", "Mercury", "Venus", "Earth", "Mars", 
                "Jupiter", "Saturn", "Uranus", "Neptune"]
        draw_text(780, 770, f"{names[planet_idx]} Facts", GLUT_BITMAP_HELVETICA_18)
        
        #background panel
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        #Semi-transparent panel
        glColor3f(0.1, 0.1, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(750, 750)
        glVertex2f(990, 750)
        glVertex2f(990, 600)
        glVertex2f(750, 600)
        glEnd()
        
        #Restore matrix
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        #facts
        facts = planet_facts[planet_idx]
        y_pos = 730
        for fact in facts:
            draw_text(760, y_pos, "• " + fact, GLUT_BITMAP_HELVETICA_12)
            y_pos -= 25

# Planet data
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

# Moon data
moon_data = [
    [3, 15, 100, 10.0, 1.0, (0.8, 0.8, 0.8)],  # Earth's moon
    [4, 8, 70, 8.0, 0.8, (0.7, 0.7, 0.7)],     # Mars' moon Phobos
    [4, 5, 90, 6.0, 0.6, (0.6, 0.6, 0.6)],     # Mars' moon Deimos
    [5, 12, 170, 9.0, 0.5, (0.9, 0.9, 0.9)],   # Jupiter's moon Io
    [5, 10, 200, 7.0, 0.4, (0.7, 0.7, 0.7)],   # Jupiter's moon Europa
    [5, 15, 240, 5.0, 0.3, (0.8, 0.8, 0.8)]    # Jupiter's moon Ganymede
]

#Asteroid and collision variables
asteroid_count = 200
asteroid_data = []
comet_position = [0, 0, 0]
comet_orbit_angle = 0
comet_speed = 1.5
comet_orbit_radius_max = 2500
comet_orbit_radius_min = 400
comet_eccentricity = 0.8
comet_size = 20
collision_mode = False
rogue_asteroid_position = [-3000, 0, 0]
rogue_asteroid_velocity = [15, 0, 0]
rogue_asteroid_size = 30
collision_happened = False
collision_time = 0
collision_target = 3  #Earth by default
explosion_particles = []   # list of tuples: (x,y,z, vx,vy,vz, birth_time)

# Animation state
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
    end_planet = 4 if inner_planets_only else len(planet_data)
    
    for p in range(start_planet - 1, end_planet - 1):
        r, g, b = planet_data[p + 1][5]
        glColor3f(r * 0.5, g * 0.5, b * 0.5)        
        
        glBegin(GL_LINES)
        points = trail_points[p]
        for i in range(len(points)):
            glVertex3f(points[i][0], points[i][1], 0)
            glVertex3f(points[(i + 1) % len(points)][0], points[(i + 1) % len(points)][1], 0)
        glEnd()

def draw_sphere(radius, slices, stacks):
    gluSphere(gluNewQuadric(), radius, slices, stacks)

def draw_planet(planet_idx, radius, rotation_angle, axial_tilt):
    glPushMatrix()
    glRotatef(axial_tilt, 0, 1, 0)
    glRotatef(rotation_angle, 0, 0, 1)
    glColor3fv(planet_data[planet_idx][5])
    gluSphere(gluNewQuadric(), radius, 32, 32)
    
    # Gas giant bands (Jupiter/Saturn)
    if planet_idx in (5, 6):
        bands = 6 if planet_idx == 5 else 4
        for b in range(bands):
            band_radius = radius * (1.0 + 0.02 * ((b + 1) / float(bands + 1)))
            base = planet_data[planet_idx][5]
            shade = 0.8 if (b % 2 == 0) else 1.0
            glColor3f(min(base[0]*shade,1), min(base[1]*shade,1), min(base[2]*shade,1))
            gluSphere(gluNewQuadric(), band_radius, 32, 32)
    
    #rings for Saturn
    if planet_idx == 6:  # Saturn
        inner_radius = radius * 1.3
        outer_radius = radius * 2.2
        ring_count = 20
        
        glPushMatrix()
        
        #a series of concentric circles for the rings
        for i in range(ring_count):
            r = inner_radius + (outer_radius - inner_radius) * i / (ring_count - 1)
            
            #Alternate ring colors
            shade = 0.7 if i % 2 == 0 else 0.9
            base = planet_data[planet_idx][5]
            glColor3f(min(base[0]*shade, 1), min(base[1]*shade, 1), min(base[2]*shade, 1))
            
            #ring as a circle of points
            glBegin(GL_POINTS)
            segments = 100
            for j in range(segments):
                angle = 2.0 * math.pi * j / segments
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                glVertex3f(x, y, 0)
            glEnd()
            
            glBegin(GL_LINES)
            for j in range(segments):
                angle1 = 2.0 * math.pi * j / segments
                angle2 = 2.0 * math.pi * ((j + 1) % segments) / segments
                x1 = r * math.cos(angle1)
                y1 = r * math.sin(angle1)
                x2 = r * math.cos(angle2)
                y2 = r * math.sin(angle2)
                glVertex3f(x1, y1, 0)
                glVertex3f(x2, y2, 0)
            glEnd()
        
        #cross lines to create a grid effect in rings
        glBegin(GL_LINES)
        cross_lines = 16
        for i in range(cross_lines):
            angle = math.pi * i / cross_lines
            x_inner = inner_radius * math.cos(angle)
            y_inner = inner_radius * math.sin(angle)
            x_outer = outer_radius * math.cos(angle)
            y_outer = outer_radius * math.sin(angle)
            glVertex3f(x_inner, y_inner, 0)
            glVertex3f(x_outer, y_outer, 0)
        glEnd()
        
        glPopMatrix()
    
    #rings for Uranus (tilted)
    if planet_idx == 7:  # Uranus
        inner_radius = radius * 1.2
        outer_radius = radius * 1.8
        ring_count = 10
        
        #saving the current matrix state before additional rotation
        glPushMatrix()
        
        #rings of Uranus are nearly perpendicular to its orbit
        glRotatef(90, 1, 0, 0)  #Rotate to position rings perpendicular
        
        for i in range(ring_count):
            r = inner_radius + (outer_radius - inner_radius) * i / (ring_count - 1)
            
            # Uranus has fainter rings
            shade = 0.3 + 0.1 * (i % 3)
            glColor3f(shade, shade, shade)
            
            #points for ring texture
            glBegin(GL_POINTS)
            segments = 80
            for j in range(segments):
                angle = 2.0 * math.pi * j / segments
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                glVertex3f(x, y, 0)
            glEnd()
            
            #basic ring outline using GL_LINES instead of GL_LINE_LOOP
            glBegin(GL_LINES)
            for j in range(segments):
                angle1 = 2.0 * math.pi * j / segments
                angle2 = 2.0 * math.pi * ((j + 1) % segments) / segments
                x1 = r * math.cos(angle1)
                y1 = r * math.sin(angle1)
                x2 = r * math.cos(angle2)
                y2 = r * math.sin(angle2)
                glVertex3f(x1, y1, 0)
                glVertex3f(x2, y2, 0)
            glEnd()
        
        #Restore matrix state after drawing rings
        glPopMatrix()
    
    #rings for Neptune
    if planet_idx == 8:  # Neptune
        inner_radius = radius * 1.1
        outer_radius = radius * 1.5
        ring_count = 7
        
        #rings of Neptune are not as tilted as Uranus
        glPushMatrix()
        glRotatef(30, 1, 0, 0)  # Slight tilt
        
        for i in range(ring_count):
            r = inner_radius + (outer_radius - inner_radius) * i / (ring_count - 1)
            
            #very faint rings
            shade = 0.2
            glColor3f(shade, shade, shade)
            
            glBegin(GL_POINTS)
            segments = 60
            for j in range(segments):
                angle = 2.0 * math.pi * j / segments
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                if i == 0 or i == ring_count-1 or j % 3 == 0:  # Sparser points for interior rings
                    glVertex3f(x, y, 0)
            glEnd()
            
            if i == 0 or i == ring_count-1 or i == ring_count//2:
                glBegin(GL_LINES)
                for j in range(segments):
                    angle1 = 2.0 * math.pi * j / segments
                    angle2 = 2.0 * math.pi * ((j + 1) % segments) / segments
                    x1 = r * math.cos(angle1)
                    y1 = r * math.sin(angle1)
                    x2 = r * math.cos(angle2)
                    y2 = r * math.sin(angle2)
                    glVertex3f(x1, y1, 0)
                    glVertex3f(x2, y2, 0)
                glEnd()
        
        #few arcs to represent Neptune's incomplete rings
        glBegin(GL_LINES)
        for i in range(5):
            r = inner_radius + (outer_radius - inner_radius) * (0.3 + 0.5 * (i / 5.0))
            start_angle = math.pi * 0.2 * i
            for j in range(20):
                angle1 = start_angle + j * 0.05
                angle2 = angle1 + 0.05
                x1 = r * math.cos(angle1)
                y1 = r * math.sin(angle1)
                x2 = r * math.cos(angle2)
                y2 = r * math.sin(angle2)
                glVertex3f(x1, y1, 0)
                glVertex3f(x2, y2, 0)
        glEnd()
        
        glPopMatrix()
    
    glPopMatrix()

def draw_planet_system(planet_idx, orbit_angle, rotation_angle):
    radius = planet_data[planet_idx][0]
    distance = planet_data[planet_idx][1]
    axial_tilt = planet_data[planet_idx][4]
    
    glPushMatrix()
    
    glRotatef(orbit_angle, 0, 0, 1)
    glTranslatef(distance, 0, 0)
    
    if planet_idx > 0:
        draw_planet(planet_idx, radius, rotation_angle, axial_tilt)
    
    # Selection indicator
    if selected_planet == planet_idx and not follow_mode:
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        for i in range(36):
            angle1 = math.radians(i * 10)
            angle2 = math.radians(((i + 1) % 36) * 10)
            x1 = (radius + 20) * math.cos(angle1)
            y1 = (radius + 20) * math.sin(angle1)
            x2 = (radius + 20) * math.cos(angle2)
            y2 = (radius + 20) * math.sin(angle2)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y2, 0)
        glEnd()
    
    #moons
    for i, moon in enumerate(moon_data):
        if moon[0] == planet_idx:
           
            glPushMatrix()
            
            #Position the moon in its orbit around the planet
            glRotatef(moon_orbit_angles[i], 0, 0, 1)
            glTranslatef(moon[2], 0, 0)
            
            glColor3fv(moon[5])
            glRotatef(moon_rotation_angles[i], 0, 0, 1)
            gluSphere(gluNewQuadric(), moon[1], 10, 10)
        
            glPopMatrix()
    
    #Restore matrix to solar system origin
    glPopMatrix()

def draw_sun():
    glColor3fv(planet_data[0][5])
    gluSphere(gluNewQuadric(), planet_data[0][0], 30, 30)

def draw_asteroids():
    if inner_planets_only: return
    glColor3f(0.6, 0.6, 0.6)
    for asteroid in asteroid_data:
        glPushMatrix()
        glRotatef(asteroid[0] * 180/math.pi, 0, 0, 1)
        glTranslatef(asteroid[1], 0, 0)
        gluSphere(gluNewQuadric(), asteroid[2], 4, 4)
        glPopMatrix()

def draw_comet():
    if inner_planets_only: return
    r = comet_orbit_radius_min / (1 - comet_eccentricity * math.cos(comet_orbit_angle))
    x = r * math.cos(comet_orbit_angle)
    y = r * math.sin(comet_orbit_angle)
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.8, 0.8, 1.0)
    gluSphere(gluNewQuadric(), comet_size, 10, 10)
    glPopMatrix()

def draw_rogue_asteroid():
    global simulation_time
    if collision_mode and not collision_happened:
        glColor3f(0.5, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(rogue_asteroid_position[0],
                     rogue_asteroid_position[1], 0)
        draw_sphere(rogue_asteroid_size, 12, 12)
        glPopMatrix()

    elif collision_happened:
        
        survivors = []
        for x, y, z, vx, vy, vz, birth in explosion_particles:
            t = simulation_time - birth  # Calculate age directly
            if t < 1.0:
                px = x + vx * t
                py = y + vy * t
                glColor3f(1.0, 0.0, 0.0)
                glPushMatrix()
                glTranslatef(px, py, 0)
                draw_sphere(rogue_asteroid_size * 0.1, 8, 8)
                glPopMatrix()
                survivors.append((x, y, z, vx, vy, vz, birth))
        explosion_particles[:] = survivors


def draw_planet_system(planet_idx, orbit_angle, rotation_angle):
    radius = planet_data[planet_idx][0]
    distance = planet_data[planet_idx][1]
    axial_tilt = planet_data[planet_idx][4]
    
    glPushMatrix()
    glRotatef(orbit_angle, 0, 0, 1)
    glTranslatef(distance, 0, 0)
    
    if planet_idx > 0:
        draw_planet(planet_idx, radius, rotation_angle, axial_tilt)
    
    if selected_planet == planet_idx and not follow_mode:
        glColor3f(1, 1, 1)
       
        glBegin(GL_LINES)
        for i in range(36):
            angle1 = math.radians(i * 10)
            angle2 = math.radians(((i + 1) % 36) * 10)
            x1 = (radius + 20) * math.cos(angle1)
            y1 = (radius + 20) * math.sin(angle1)
            x2 = (radius + 20) * math.cos(angle2)
            y2 = (radius + 20) * math.sin(angle2)
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y2, 0)
        glEnd()
    
    # Moons
    for i, moon in enumerate(moon_data):
        if moon[0] == planet_idx:
            glPushMatrix()
            glRotatef(moon_orbit_angles[i], 0, 0, 1)
            glTranslatef(moon[2], 0, 0)
            glColor3fv(moon[5])
            glRotatef(moon_rotation_angles[i], 0, 0, 1)
            gluSphere(gluNewQuadric(), moon[1], 10, 10)
            glPopMatrix()
    
    glPopMatrix()

def draw_solar_system():
    draw_trails()
    draw_sun()
    draw_comet()

    #asteroids belt
    if not inner_planets_only:
        glColor3f(0.3,0.3,0.3)
        for asteroid in sorted(asteroid_data, key=lambda a: -a[1]):
            glPushMatrix()
            glRotatef(asteroid[0] * 180.0/math.pi, 0, 0, 1)
            glTranslatef(asteroid[1], 0, 0)
            gluSphere(gluNewQuadric(), asteroid[2], 4, 4)
            glPopMatrix()

    #planets (outer → inner)
    end_planet = 4 if inner_planets_only else len(planet_data)
    for i in range(end_planet-1, 0, -1):
        draw_planet_system(i, orbit_angles[i], rotation_angles[i])

    # rogue asteroid or explosion on top
    draw_rogue_asteroid()


def draw_planet_label(planet_idx):
    names = ["Sun", "Mercury", "Venus", "Earth", "Mars", 
             "Jupiter", "Saturn", "Uranus", "Neptune"]
    if 0 <= planet_idx < len(names):
        draw_text(10, 720, f"Selected: {names[planet_idx]}")

def draw_simulation_controls():
    draw_text(10, 770, f"Time Scale: {time_scale:.1f}x{' (PAUSED)' if paused else ''}")
    draw_text(10, 690, "Camera: Follow Mode" if follow_mode else "Camera: Free Mode")
    draw_text(10, 630, "View: Inner Planets Only" if inner_planets_only else "View: Full Solar System")
    draw_text(10, 600, "Trails: " + ("ON" if show_trails else "OFF"))
    draw_text(10, 80, "Controls:")
    draw_text(10, 60, "Arrow keys: Rotate camera  |  W/S: Zoom  |  P: Pause  |  R: Reset")
    draw_text(10, 40, "1-9: Select planet  |  F: Follow mode  |  O: Toggle trails  |  +/-: Time scale")
    draw_text(10, 20, "C: Toggle collision demo  |  I: Inner planets only")
    
    
    draw_planet_facts(selected_planet)

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 10, 10000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if follow_mode and selected_planet > 0:
        planet = planet_data[selected_planet]
        planet_angle = math.radians(orbit_angles[selected_planet])
        planet_x = planet[1] * math.cos(planet_angle)
        planet_y = planet[1] * math.sin(planet_angle)
        
        #camera position based on distance and rotation
        cam_x = planet_x + camera_distance * math.cos(math.radians(camera_rotation[0])) * math.cos(math.radians(camera_rotation[1]))
        cam_y = planet_y + camera_distance * math.sin(math.radians(camera_rotation[0])) * math.cos(math.radians(camera_rotation[1]))
        cam_z = camera_distance * math.sin(math.radians(camera_rotation[1]))
        
        gluLookAt(cam_x, cam_y, cam_z, planet_x, planet_y, 0, 0, 0, 1)
    else:
        # Free camera mode with proper distance-based calculation
        cam_x = camera_distance * math.cos(math.radians(camera_rotation[1])) * math.cos(math.radians(camera_rotation[0]))
        cam_y = camera_distance * math.cos(math.radians(camera_rotation[1])) * math.sin(math.radians(camera_rotation[0]))
        cam_z = camera_distance * math.sin(math.radians(camera_rotation[1]))
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)

def update_simulation():
    global comet_orbit_angle, collision_happened, collision_time, explosion_particles, rogue_asteroid_position,simulation_time
    
    if paused: return
    else:
        simulation_time += 0.016 * time_scale  # Approximate 60 FPS delta time
    
    #Update angles
    for i in range(1, len(planet_data)):
        orbit_angles[i] = (orbit_angles[i] + planet_data[i][2] * time_scale) % 360
        rotation_angles[i] = (rotation_angles[i] + planet_data[i][3] * time_scale) % 360
    
    rotation_angles[0] = (rotation_angles[0] + planet_data[0][3] * time_scale) % 360
    
    for i in range(len(moon_data)):
        moon_orbit_angles[i] = (moon_orbit_angles[i] + moon_data[i][3] * time_scale) % 360
        moon_rotation_angles[i] = (moon_rotation_angles[i] + moon_data[i][4] * time_scale) % 360
    
    #Update asteroid angles
    for asteroid in asteroid_data:
        asteroid[0] = (asteroid[0] + 0.001 * asteroid[3] * time_scale) % (2 * math.pi)
    
    #Update comet
    r = comet_orbit_radius_min / (1 - comet_eccentricity * math.cos(comet_orbit_angle))
    comet_orbit_angle = (comet_orbit_angle + 0.005 * comet_speed * (comet_orbit_radius_max/r)**2 * time_scale) % (2*math.pi)
    
    #Update collision
        # move rogue asteroid & test for hit
    if collision_mode and not collision_happened:
        #Update asteroid position
        rogue_asteroid_position[0] += rogue_asteroid_velocity[0] * time_scale
        rogue_asteroid_position[1] += rogue_asteroid_velocity[1] * time_scale

        # Check collision with ALL planets
        for i in range(0, len(planet_data)):
            planet = planet_data[i]
            ang = math.radians(orbit_angles[i])
            px = planet[1] * math.cos(ang)
            py = planet[1] * math.sin(ang)
            distance = math.hypot(
                rogue_asteroid_position[0] - px,
                rogue_asteroid_position[1] - py
            )
            
            if distance < planet[0] + rogue_asteroid_size:
                collision_happened = True
                collision_time = simulation_time                
                
                #red explosion particles
                explosion_particles.clear()
                for _ in range(20):
                    θ = random.random() * 2 * math.pi
                    speed = random.uniform(50, 150)
                    explosion_particles.append((
                        px, py, 0,
                        math.cos(θ)*speed, 
                        math.sin(θ)*speed,
                        0,
                        simulation_time
                    ))
                break  #Stop after first collision

def reset_simulation():
    global orbit_angles, rotation_angles, moon_orbit_angles, moon_rotation_angles
    global time_scale, selected_planet, follow_mode, paused, collision_happened
    orbit_angles = [0]*len(planet_data)
    rotation_angles = [0]*len(planet_data)
    moon_orbit_angles = [0]*len(moon_data)
    moon_rotation_angles = [0]*len(moon_data)
    time_scale = 1.0
    selected_planet = 0
    follow_mode = False
    paused = False
    collision_happened = False
    rogue_asteroid_position = [-3000, 0, 0]

def keyboardListener(key, x, y):
    global paused, time_scale, selected_planet, follow_mode, show_trails, inner_planets_only, collision_mode, camera_distance, collision_happened, rogue_asteroid_position, rogue_asteroid_velocity
    
    if key == b'p': paused = not paused
    if key == b'r': reset_simulation()
    if key == b'f': follow_mode = not follow_mode
    if key == b'o': show_trails = not show_trails
    if key == b'i': inner_planets_only = not inner_planets_only
    if key == b'c':
       #Reset asteroid to initial state
        collision_mode = True
        collision_happened = False
        explosion_particles.clear()
        rogue_asteroid_position = [-3000, 0, 0]  #Start at left
        rogue_asteroid_velocity = [15, 0, 0]
    if key >= b'1' and key <= b'9':
        selected_planet = min(int(key)-int(b'1'), len(planet_data)-1)
    #Fixed time scale controls
    if key in (b'+', b'='):
        time_scale = min(1.0, round(time_scale + 0.1, 1))
    elif key == b'-':
        time_scale = max(0.1, round(time_scale - 0.1, 1))
    
    if key >= b'1' and key <= b'9':
        selected_planet = int(key) - int(b'1')
        if selected_planet >= len(planet_data):
            selected_planet = len(planet_data) - 1
        camera_rotation = [0, 0]
        follow_mode = True
        camera_distance = planet_data[selected_planet][1] * 0.4
    
    if key == b'w': camera_distance = max(500, camera_distance * 0.9)
    if key == b's': camera_distance = min(5000, camera_distance * 1.1)

def specialKeyListener(key, x, y):
    global camera_rotation
    if key == GLUT_KEY_LEFT: camera_rotation[0] -= 5
    elif key == GLUT_KEY_RIGHT: camera_rotation[0] += 5
    elif key == GLUT_KEY_UP: camera_rotation[1] = min(80, camera_rotation[1]+5)
    elif key == GLUT_KEY_DOWN: camera_rotation[1] = max(-80, camera_rotation[1]-5)
    elif key == GLUT_KEY_PAGE_UP: camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2]*0.9)
    elif key == GLUT_KEY_PAGE_DOWN: camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2]*1.1)

def mouseListener(button, state, x, y):
    pass

def idle():
    update_simulation()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_solar_system()
    draw_planet_label(selected_planet)
    draw_simulation_controls()
    glutSwapBuffers()

def init():
    init_asteroids()
    init_trails()
    reset_simulation()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
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