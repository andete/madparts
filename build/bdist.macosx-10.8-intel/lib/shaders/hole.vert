#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

// input
uniform vec2 move;   // location
uniform vec2 radius; // radius

// output
varying vec2 pos2;    // adjusted position
varying vec2 radius2; // radius

void main() {
  gl_FrontColor = gl_Color;
  vec4 vert = gl_Vertex;
  vert.x = vert.x * radius.x * 2;
  vert.y = vert.y * radius.y * 2;
  vec4 vert2 = vert;
  vert2.x +=move.x;
  vert2.y +=move.y;
  gl_Position = gl_ModelViewProjectionMatrix * vert2;
  pos2 = vec2(vert);
  radius2 = radius;
}
