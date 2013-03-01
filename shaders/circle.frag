#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos2;
varying vec2 radius2;
varying float drill2; // drill: radius
varying vec2 drill_offset2;

void main() {
  float x = pos2.x / radius2.x;
  float y = pos2.y / radius2.y;
  float dist = x * x + y * y;
  if (dist <= 1) {
    float x2 = pos2.x-drill_offset2.x;
    float y2 = pos2.y-drill_offset2.y;
    if (x2*x2 + y2*y2 >= drill2*drill2) {
      gl_FragColor = gl_Color;
    }
  }
}
