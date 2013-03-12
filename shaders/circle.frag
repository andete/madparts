#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos2;    // location
varying vec2 radius2; // outer radius
varying vec2 inner2;  // inner radius
varying float drill2; // drill: radius
varying vec2 drill_offset2;

void main() {
  gl_FragColor = vec4(0,0,0,0);
  float drill3 = drill2/2;
  float x = pos2.x / radius2.x;
  float y = pos2.y / radius2.y;
  float dist = x * x + y * y;
  float ix = pos2.x / inner2.x;
  float iy = pos2.y / inner2.y;
  float idist = ix * ix + iy * iy;
  if (dist <= 1 && idist >= 1) {
    float x2 = pos2.x-drill_offset2.x;
    float y2 = pos2.y-drill_offset2.y;
    if (x2*x2 + y2*y2 >= drill3*drill3) {
      gl_FragColor = gl_Color;
    }
  }
}
