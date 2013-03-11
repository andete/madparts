#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos2;    // position
varying vec2 size2;   // size in x and y direction
varying float drill2; // drill diameter
varying vec2 drill_offset2;

void main() {
  gl_FragColor = vec4(0,0,0,0);
  float drill3 = drill2/2;
  
  // r: mininum size of straight side
  float q = sqrt(2.0)-1.0;
  float rx = size2.x * q;
  float ry = size2.y * q;
  float r = min(rx, ry);

  float shortest_size = min(size2.x, size2.y);
  float corner_size = (shortest_size - r) / 2;

  // a: minimum value where we want to cut off a corner
  float ax = (size2.x / 2) - corner_size;
  float ay = (size2.y / 2) - corner_size;

  // if we are in a corner zone:
  if (abs(pos2.x) > ax && abs(pos2.y) > ay) {
    // abs position within corner
    float x = abs(pos2.x) - ax;
    float y = abs(pos2.y) - ay;
    // are we inside the triangle ?
    if (x + y < corner_size) {
      gl_FragColor = gl_Color;
    }
  // else we're in a normal square zone:
  } else {
    float x2 = pos2.x-drill_offset2.x;
    float y2 = pos2.y-drill_offset2.y;
    if (x2*x2 + y2*y2 >= drill3*drill3) {
      gl_FragColor = gl_Color;
    }
  }
}
