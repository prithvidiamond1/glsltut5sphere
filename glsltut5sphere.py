
import numpy as np
import time

import moderngl
import glfw
from glfw import GLFW

import glm

enable_query = False

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
    if key == GLFW.GLFW_KEY_ESCAPE and action == GLFW.GLFW_PRESS:
        glfw.set_window_should_close(window, GLFW.GLFW_TRUE)

def window_resize(window, w, h):
    projection = np.array(glm.perspective(45.0, float(w/(h+0.00001)), 2.0, 100.0), 'f4')
    prog['projection'].write(projection)
    ctx.viewport = (0, 0, w, h)

glfw.set_key_callback(window, window_quit)
glfw.set_window_size_callback(window, window_resize)

glfw.swap_interval(1) # Toggles V-sync, 0 = Off, 1 = On, Which means it also unlocks/locks the framerate

prog = ctx.program(
    vertex_shader=open('prog.vert', 'r').read(),
    fragment_shader=open('prog.frag', 'r').read(),
)

def fragmenter(t_verts, next_verts=None, cycles=1):
    def midpoint(v1, v2):
        return ((v1[0]+v2[0])/2, (v1[1]+v2[1])/2, (v1[2]+v2[2])/2)
    
    if next_verts is None:
        next_verts = t_verts

    if cycles == 0:
        return t_verts

    new_verts = []
    no_verts = len(next_verts)

    for idx in range(no_verts):
        if idx == 0:
            m1 = midpoint(next_verts[no_verts-1], next_verts[idx])
            m2 = midpoint(next_verts[idx], next_verts[idx+1])
        elif idx == no_verts-1:
            m1 = midpoint(next_verts[idx-1], next_verts[idx])
            m2 = midpoint(next_verts[idx], next_verts[0])
        else:
            m1 = midpoint(next_verts[idx-1], next_verts[idx])
            m2 = midpoint(next_verts[idx], next_verts[idx+1])
        new_verts.extend([m2, m1, next_verts[idx], m2, m1])
    
    t_verts.extend(new_verts)
    return fragmenter(t_verts, new_verts, cycles-1)


sphere_vertices = [(0, (3**0.5)-0.5, 0), (-1, -0.5, 0), (1, -0.5, 0)]
sphere_vertices = np.array(fragmenter(sphere_vertices, cycles=3), 'f4')

vbo1 = ctx.buffer(sphere_vertices)

projection = np.array(glm.perspective(45.0, float(width/(height+0.00001)), 2.0, 100.0), 'f4')
view = np.eye(4, dtype='f4')
model = np.eye(4, dtype='f4')

view = glm.translate(view, np.array((0, -0.3, -2), 'f4'))
# model = glm.rotate(model, -10, np.array((0, 1, 0), 'f4'))

prog['projection'].write(projection)
prog['view'].write(view)
prog['model'].write(model)

vao = ctx.vertex_array(prog, ((vbo1, '3f', 'position'),))

ctx.enable(ctx.DEPTH_TEST) # for testing without culling

ctx.wireframe = True

# ctx.enable(ctx.DEPTH_TEST|ctx.CULL_FACE) # for testing with culling
# ctx.cull_face = 'back'
# ctx.front_face = 'ccw'

# Framerate measuring stuff
framerate_test = False

frames = 0
avg_frames, avg_count = 0, 1
init_time = start_time = time.time()

if enable_query:
    query = ctx.query(samples=True, time=True, primitives=True) # for quering info about no of samples, time elapsed and no of primitives

while not glfw.window_should_close(window):
    ctx.screen.use()
    ctx.screen.clear(0.0, 0.0, 0.0, 1.0)

    if enable_query:
        with query:
            vao.render(moderngl.TRIANGLES)
    else:
        vao.render(moderngl.TRIANGLES)

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

