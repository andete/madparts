#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos;
varying vec2 radius;
void main() {
  float x = pos.x / radius.x;
  float y = pos.y / radius.y;
  float dist = x * x + y * y;
  if (dist <= 1)
    gl_FragColor = gl_Color;
}
