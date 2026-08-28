# Solar System Simulation

A real-time **3D Solar System simulation** built with **Python, PyOpenGL, and GLUT**. The project visualizes the Sun, planets, selected moons, an asteroid belt, a moving comet, orbital trails, and an interactive asteroid collision demonstration.

## Features

- 3D visualization of the Solar System
- Sun with a simple glow effect
- Eight planets with configurable:
  - Radius
  - Orbital distance
  - Orbital speed
  - Rotation speed
  - Axial tilt
  - Color
- Planet day/night shading approximation
- Selected moons:
  - Earth's Moon
  - Mars' Phobos and Deimos
  - Jupiter's Io, Europa, and Ganymede
- Procedurally initialized asteroid belt with 200 asteroids
- Elliptical comet orbit with a visible tail
- Orbital trails for planets
- Planet selection using number keys
- Free camera with rotation and zoom controls
- Camera follow mode for selected planets
- Adjustable simulation time scale
- Pause/resume functionality
- Inner-planets-only viewing mode
- Asteroid collision demonstration with an explosion animation
- On-screen simulation status and controls
- Reset functionality

## Technologies

- **Python 3**
- **PyOpenGL**
- **GLUT / OpenGL Utility Toolkit**
- **OpenGL**
- **GLU**
- **math** (Python standard library)

## How It Works

The simulation represents celestial bodies using configurable data structures. Planet information is stored as:

```text
[radius, distance from sun, orbit speed, rotation speed, axial tilt, color]
```

Moon information is stored as:

```text
[parent planet, radius, distance from planet, orbit speed, rotation speed, color]
```

The animation loop continuously updates orbital and rotational angles and redraws the scene.

### Planet Motion

Each planet's orbital and rotational angles are updated according to its configured speed and the current simulation time scale.

### Moons

Moons are drawn relative to their parent planet. Their individual orbital and rotational angles are updated every simulation frame.

### Asteroid Belt

The asteroid belt contains 200 low-polygon spheres. Their positions are initialized around the Sun with small variations in distance, size, and speed.

### Comet

The comet follows an eccentric orbit. Its position is calculated from the orbit parameters, and its speed changes based on its current distance from the Sun. A transparent triangular fan is used to represent the comet's tail.

### Collision Demonstration

The project includes a demonstration mode where a rogue asteroid travels toward Earth. A collision is detected when the distance between the asteroid and the target planet becomes smaller than the sum of their radii. Once a collision occurs, the asteroid is replaced by an expanding explosion effect for a short duration.

## Camera System

The simulation supports two camera modes:

### Free Camera

The camera can be rotated around the Solar System and zoomed in or out.

### Follow Mode

After selecting a planet, follow mode positions the camera relative to that planet and continuously tracks its orbital position.

## Controls

| Key | Action |
|---|---|
| `1-9` | Select Sun / planets |
| `Arrow Keys` | Rotate camera |
| `W` | Zoom in |
| `S` | Zoom out |
| `Page Up` | Zoom in |
| `Page Down` | Zoom out |
| `P` | Pause / resume simulation |
| `R` | Reset simulation |
| `F` | Toggle camera follow mode |
| `O` | Toggle orbital trails |
| `I` | Toggle inner-planets-only view |
| `C` | Toggle collision demonstration |
| `+` | Increase simulation speed |
| `-` | Decrease simulation speed |

## Rendering

The application uses OpenGL primitives to construct the scene:

- `gluSphere()` is used for celestial bodies.
- `GL_LINE_LOOP` is used for orbital trails and the selected-planet indicator.
- `GL_TRIANGLE_FAN` is used to create the comet tail.
- Double buffering is enabled to provide smooth animation.
- Depth buffering is enabled for 3D rendering.
- A perspective projection is used for the main scene.
- An orthographic projection is temporarily used for the on-screen UI text.

## Project Structure

```text
solar-system/
│
├── solar_system.py       # Main simulation source code
└── README.md              # Project documentation
```

> The source code provided for this project is contained in a single Python file.

## Installation

Install Python 3 and the required PyOpenGL packages:

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

Depending on your operating system, GLUT/freeglut may also need to be installed separately.

### Linux

On Debian/Ubuntu-based systems, GLUT can typically be installed with:

```bash
sudo apt install freeglut3-dev
```

## Running the Project

Run the Python file containing the simulation:

```bash
python solar_system.py
```

A `1000 × 800` OpenGL window titled **Solar System Simulation** will open.

## Important Implementation Details

### Animation Loop

GLUT's idle callback continuously calls the simulation update function and requests the scene to be redrawn:

```text
update_simulation()
        ↓
glutPostRedisplay()
        ↓
showScreen()
        ↓
draw_solar_system()
```

### Simulation State

The program maintains global state for:

- Camera position and rotation
- Simulation speed
- Pause state
- Selected planet
- Follow mode
- Orbital trails
- Inner-planet filtering
- Collision mode
- Orbital angles
- Rotational angles

### Reset

The reset function restores:

- Planet and moon angles
- Simulation speed
- Selected planet
- Camera follow mode
- Pause state
- Rogue asteroid position
- Collision state

## Learning Objectives

This project demonstrates practical use of:

- OpenGL 3D rendering
- PyOpenGL
- GLUT event handling
- Transformation matrices
- 3D camera positioning
- Object hierarchies
- Animation and simulation loops
- Keyboard input handling
- Procedural object generation
- Collision detection
- Basic orbital mathematics
- Transparency and simple visual effects
- UI text rendering inside an OpenGL application

## Limitations

This is a **visual simulation rather than a scientifically accurate astronomical model**. Planet sizes, orbital distances, speeds, and other parameters are intentionally scaled for visualization. The day/night effect is also implemented as a visual approximation rather than a physically based lighting system.

The project currently includes mouse-input handlers, but the left and right mouse actions are placeholders and do not perform selection or camera actions.

## Future Improvements

Potential improvements include:

- Realistic OpenGL lighting and shadows
- Texture mapping for planets
- More accurate astronomical scales
- Additional moons
- Saturn's rings
- Improved comet-tail rendering
- Real gravitational simulation
- Mouse-based planet selection
- Interactive planet information panels
- Better collision physics
- Sound effects
- Improved UI
- Adjustable rendering quality
- Support for fullscreen mode

## Credits

Developed as an OpenGL graphics/simulation project using Python and PyOpenGL.
