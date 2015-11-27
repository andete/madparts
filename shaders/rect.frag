#version 120

// (c) 2013-2015 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos2;    // position
varying float round2; // roundness of corners
varying vec2 size2;   // size in x and y direction
varying vec2 drill2; // drill diameter
varying vec2 drill_offset2;

void main() {
  gl_FragColor = vec4(0,0,0,0);
  float drill3_x = drill2.x/2;
  float drill3_y = drill2.y/2;
  float rx = (size2.x / 2) * round2;
  float ry = (size2.y / 2) * round2;
  float r = min(rx, ry); // we only support round corners for now
  float ax = (size2.x / 2) - r;
  float ay = (size2.y / 2) - r;

  // if we are in a corner zone:
  if (abs(pos2.x) > ax && abs(pos2.y) > ay) {
    float x = (abs(pos2.x) - ax) / r;
    float y = (abs(pos2.y) - ay) / r;
    float dist = x * x + y * y;
    if (dist <= 1) {
      float x2 = (pos2.x-drill_offset2.x)/drill3_x;
      float y2 = (pos2.y-drill_offset2.y)/drill3_y;
      if (x2*x2 +y2*y2 >= 1) {
        gl_FragColor = gl_Color;
      }
    }
  // else we're in a normal square zone:
  } else {
    float x2 = (pos2.x-drill_offset2.x)/drill3_x;
    float y2 = (pos2.y-drill_offset2.y)/drill3_y;
    if (x2*x2 +y2*y2 >= 1) {
      gl_FragColor = gl_Color;
    }
  }
}
