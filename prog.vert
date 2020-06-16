#version 330 core

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

in vec3 position;

out vec3 normal;
out vec3 fragpos;

// varying variables need to be in/out in core context

mat4 pvm = projection*view*model;
mat3 normal_model = mat3(transpose(inverse(model)));

void main() {
    gl_Position = pvm*vec4(position, 1.0);
    fragpos = vec3(model*vec4(position, 1.0));
    normal = normal_model*(vec3(0.0 ,0.0, 0.0) - position);
}