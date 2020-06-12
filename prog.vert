#version 330 core

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

in vec3 position;

// varying variables need to be in/out in core context

mat4 pvm = projection*view*model;

void main() {
    gl_Position = pvm*vec4(position, 1.0);
}