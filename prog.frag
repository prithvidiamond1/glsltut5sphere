#version 330 core

// output variables are required as variables like gl_FragColor is deprecated in core context
out vec4 FragColor;

void main() {
    FragColor = vec4(1.0, 1.0, 1.0, 1.0);
}