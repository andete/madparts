#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos;
void main() {
  float radius = 0.5;
  float dist = radius * radius - pos.x * pos.x - pos.y * pos.y;
  if (dist > 0)
    gl_FragColor = gl_Color;
}
