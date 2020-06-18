
import numpy as np
import time

import moderngl
import glfw
from glfw import GLFW

import glm

enable_query = False

x_rotate = False
y_rotate = False
z_rotate = False

glfw.init()

# setting context flags
glfw.window_hint(glfw.CONTEXT_CREATION_API, glfw.NATIVE_CONTEXT_API)
glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
glfw.window_hint(glfw.RESIZABLE, True)
glfw.window_hint(glfw.DOUBLEBUFFER, True)
glfw.window_hint(glfw.DEPTH_BITS, 24)
glfw.window_hint(glfw.SAMPLES, 8)  # For MSAA*x where x is the integer > 0

width, height = 1280, 720
window = glfw.create_window(width, height, 'GLSLtut', None, None)

glfw.make_context_current(window)

ctx = moderngl.create_context(require=330)

def window_quit(window, key, scancode, action, mods):
    global x_rotate, y_rotate, z_rotate
    if key == GLFW.GLFW_KEY_ESCAPE and action == GLFW.GLFW_PRESS:
        glfw.set_window_should_close(window, GLFW.GLFW_TRUE)
    if key == GLFW.GLFW_KEY_X and action == GLFW.GLFW_PRESS:
        x_rotate = not x_rotate
    if key == GLFW.GLFW_KEY_Y and action == GLFW.GLFW_PRESS:
        y_rotate = not y_rotate
    if key == GLFW.GLFW_KEY_Z and action == GLFW.GLFW_PRESS:
        z_rotate = not z_rotate

def window_resize(window, w, h):
    projection = np.array(glm.perspective(45.0, float(w/(h+0.00001)), 2.0, 100.0), 'f4')
    prog['projection'].write(projection)
    ctx.viewport = (0, 0, w, h)

glfw.set_key_callback(window, window_quit)
glfw.set_window_size_callback(window, window_resize)

glfw.swap_interval(0) # Toggles V-sync, 0 = Off, 1 = On, Which means it also unlocks/locks the framerate

prog = ctx.program(
    vertex_shader=open('prog.vert', 'r').read(),
    fragment_shader=open('prog.frag', 'r').read(),
)

def fragmenter(vertices, cycles): # Recursive variant of fragmenter
    def midpoint(v1, v2):
        return ((v1[0]+v2[0])/2, (v1[1]+v2[1])/2, (v1[2]+v2[2])/2)

    for current_cycle in range(cycles):
        new_vertices = []

        for triangle in zip(*(iter(vertices),) * 3):  # make groups of 3 vertices
            v1 = midpoint(triangle[0], triangle[1])
            v2 = midpoint(triangle[1], triangle[2])
            v3 = midpoint(triangle[2], triangle[0])

            new_vertices.extend([v2, v1, v3, v1, triangle[0], v3, v2, triangle[1], v1, triangle[2], v2, v3])

        vertices = new_vertices

    return vertices

t1_vertices = [[0, (2**0.5), 0], [1, 0, 1], [-1, 0, 1]]
t2_vertices = [[0, (2**0.5), 0], [-1, 0, 1], [-1, 0, -1]]
t3_vertices = [[0, (2**0.5), 0], [1, 0, -1], [1, 0, 1]]
t4_vertices = [[0, (2**0.5), 0], [-1, 0, -1], [1, 0, -1]]

t5_vertices = [[0, -(2**0.5), 0], [-1, 0, 1], [1, 0, 1]]
t6_vertices = [[0, -(2**0.5), 0], [-1, 0, -1], [-1, 0, 1]]
t7_vertices = [[0, -(2**0.5), 0], [1, 0, 1], [1, 0, -1]]
t8_vertices = [[0, -(2**0.5), 0], [1, 0, -1], [-1, 0, -1]]

trans_verts = t1_vertices+t2_vertices+t3_vertices+t4_vertices+t5_vertices+t6_vertices+t7_vertices+t8_vertices

center = (0, 0, 0)

light_pos = (-2, -2, -2)
light_color = (1.0, 1.0, 1.0)

view_pos = center

prog['lightcolor'] = light_color
prog['lightpos'] = light_pos
prog['viewpos'] = view_pos

sphere_vertices = np.array(fragmenter(trans_verts, cycles=5), 'f4')

def normalizer(verts, center, radius):
    def normalize(v1, v2, length):
        def distance(v1, v2):
            return ((v2[0]-v1[0])**2+(v2[1]-v1[1])**2+(v2[2]-v1[2])**2)**0.5

        dx = v2[0] - v1[0]
        dy = v2[1] - v1[1]
        dz = v2[2] - v1[2]
        dx = dx*length/distance(v1, v2)
        dy = dy*length/distance(v1, v2)
        dz = dz*length/distance(v1, v2)
        
        return (v1[0]+dx, v1[1]+dy, v1[2]+dz)

    n_verts = []
    for vert in verts:
        n_verts.append(normalize(center, vert, radius))
    
    return n_verts

sphere_vertices = np.array(normalizer(sphere_vertices, center, 2), 'f4')

vbo = ctx.buffer(sphere_vertices)

projection = np.array(glm.perspective(45.0, float(width/(height+0.00001)), 2.0, 100.0), 'f4')
# view = np.eye(4, dtype='f4')
model = np.eye(4, dtype='f4')

swivel_radius = 5
campos = np.array((0, 0, swivel_radius), 'f4')
camtarget = np.array(center, 'f4')
camup = np.array((0, 1, 0), 'f4')

view = glm.lookAt(campos, camtarget, camup)

prog['projection'].write(projection)
prog['view'].write(view)
prog['model'].write(model)

vao = ctx.vertex_array(prog, ((vbo, '3f', 'position'),))

# ctx.enable(ctx.DEPTH_TEST) # for testing without culling

# ctx.wireframe = True

ctx.enable(ctx.DEPTH_TEST|ctx.CULL_FACE) # for testing with culling
ctx.cull_face = 'back'
ctx.front_face = 'ccw'

# Framerate measuring stuff
framerate_test = True

frames = 0
avg_frames, avg_count = 0, 1
init_time = start_time = time.time()

if enable_query:
    query = ctx.query(samples=True, time=True, primitives=True) # for quering info about no of samples, time elapsed and no of primitives

x_theta = y_theta = z_theta = r_time = 0

def render_scene():
    global model, view
    global x_theta, y_theta, z_theta, r_time

    r_time += 0.02

    if x_rotate:
        x_theta = 0.02
    elif not x_rotate:
        x_theta = 0
    
    if y_rotate:
        y_theta = 0.02
    elif not y_rotate:
        y_theta = 0
    
    if z_rotate:
        z_theta = 0.02
    elif not z_rotate:
        z_theta = 0

    model = glm.rotate(model, x_theta, np.array([1, 0, 0], 'f4'))
    model = glm.rotate(model, y_theta, np.array([0, 1, 0], 'f4'))
    model = glm.rotate(model, z_theta, np.array([0, 0, 1], 'f4'))
    prog['model'].write(model)

    cam_x = np.sin(r_time)*swivel_radius
    cam_z = np.cos(r_time)*swivel_radius
    view = glm.lookAt(np.array((cam_x, 0, cam_z), 'f4'), camtarget, camup)
    prog['view'].write(view)

    vao.render(moderngl.TRIANGLES)

while not glfw.window_should_close(window):
    ctx.screen.use()
    ctx.screen.clear(0.0, 0.0, 0.0, 1.0)

    if enable_query:
        with query:
            render_scene()
    else:
        render_scene()

    glfw.swap_buffers(window)
    glfw.poll_events()

    if framerate_test:
        frames += 1
        if time.time()-start_time >= 1:
            avg_frames = ((avg_count-1)*avg_frames + frames)*avg_count
            frames = 0
            start_time = time.time()
        if time.time()-init_time >= 60:
            print('Average Framerate =', avg_frames)
            if enable_query:
                print('samples =', query.samples)
                print('elapsed =', query.elapsed)
                print('primitives =', query.primitives)
            glfw.set_window_should_close(window, GLFW.GLFW_TRUE)

glfw.destroy_window(window)

