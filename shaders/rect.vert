#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

// scale unit square to our rect size
// and move to it's origin

uniform vec2 scale;
uniform vec2 move;
void main() {
  gl_FrontColor = gl_Color;
  vec4 vert = gl_Vertex;
  vert.x = vert.x * scale.x + move.x;
  vert.y = vert.y * scale.y + move.y;
  gl_Position = gl_ModelViewProjectionMatrix * vert;
}
