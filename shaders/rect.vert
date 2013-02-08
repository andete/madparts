#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

// scale unit square to our rect size
// and move to it's origin

uniform vec2 scale;
uniform vec2 move;
uniform vec2 round;

varying vec2 pos;
varying float round2;
varying vec2 scale2;

void main() {
  gl_FrontColor = gl_Color;
  vec4 vert = gl_Vertex;
  vert.x = vert.x * scale.x;
  vert.y = vert.y * scale.y;
  vec4 vert2 = vert;
  vert2.x += move.x;
  vert2.y += move.y;
  gl_Position = gl_ModelViewProjectionMatrix * vert2;
  pos = vec2(vert);
  round2 = round.x;
  scale2 = scale;
}
