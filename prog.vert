#version 330 core

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

uniform vec3 LightPos;
uniform vec3 ViewPos;

in vec3 position;

out vec3 normal;
out vec3 fragpos;
out vec3 lightpos;
out vec3 viewpos;

// varying variables need to be in/out in core context

mat4 mv = view*model;
mat4 pvm = projection*mv;
mat3 normal_model = mat3(transpose(inverse(mv)));

void main() {
    gl_Position = pvm*vec4(position, 1.0);
    fragpos = vec3(mv*vec4(position, 1.0));
    normal = normal_model*(vec3(0.0 ,0.0, 0.0) - position);
    lightpos = vec3(mv*vec4(LightPos, 1.0));
    viewpos = vec3(mv*vec4(ViewPos, 1.0));
}