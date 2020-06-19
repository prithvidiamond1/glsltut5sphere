#version 330 core

// output variables are required as variables like gl_FragColor is deprecated in core context

uniform vec3 lightcolor;
// uniform vec3 lightpos;
// uniform vec3 viewpos;

in vec3 normal;
in vec3 fragpos;
in vec3 lightpos;
in vec3 viewpos;

out vec4 FragColor;

// Calculating ambient color
float ambience = 0.1;
vec3 ambientcolor = ambience*lightcolor;
vec3 objectcolor = vec3(1.0, 0.0, 0.0);

// Calculating diffuse color
vec3 norm = normalize(normal);
vec3 lightdir = normalize(lightpos-fragpos);

float diffuse = max(dot(norm, lightdir), 0.0);
vec3 diffusecolor = diffuse*lightcolor;

// Calculataing specular color
float spec_intensity = 0.5;
vec3 viewdir = normalize(viewpos-fragpos);
vec3 reflectdir = reflect(-lightdir, norm);

float shininess = 32;
float specular = pow(max(dot(viewdir, reflectdir), 0.0), shininess);
vec3 specularcolor = spec_intensity*specular*lightcolor;

void main() {
    FragColor = vec4((ambientcolor+diffusecolor+specularcolor)*objectcolor, 1.0);
}