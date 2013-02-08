#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

uniform vec2 move;
uniform vec2 radiusin;

varying vec2 pos;
varying vec2 radius;
void main() {
  gl_FrontColor = gl_Color;
  vec4 vert = gl_Vertex;
  vert.x = vert.x * radiusin.x * 2;
  vert.y = vert.y * radiusin.y * 2;
  vec4 vert2 = vert;
  vert2.x +=move.x;
  vert2.y +=move.y;
  gl_Position = gl_ModelViewProjectionMatrix * vert2;
  pos = vec2(vert);
  radius = radiusin;
}
