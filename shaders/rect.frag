#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos2;    // position
varying float round2; // roundness of corners
varying vec2 size2;   // size in x and y direction
varying vec2 drill2;  // drill: radius, offset in x

void main() {
  float rx = (size2.x / 2) * round2;
  float ry = (size2.y / 2) * round2;
  float r = min(rx, ry); // we want round corners for now
  float ax = (size2.x / 2) - r;
  float ay = (size2.y / 2) - r;

  // if we are in a corner zone:
  if (abs(pos2.x) > ax && abs(pos2.y) > ay) {
    float x = (abs(pos2.x) - ax) / r;
    float y = (abs(pos2.y) - ay) / r;
    float dist = x * x + y * y;
    if (dist <= 1) {
      gl_FragColor = gl_Color;
    }
  // else we're in a normal square zone:
  } else {
    float drill_r = drill2.x;
    float drill_dx = drill2.y;
    if ((pos2.x-drill_dx)*(pos2.x-drill_dx) + pos2.y*pos2.y >= drill_r*drill_r) {
      gl_FragColor = gl_Color;
    }
  }
}
