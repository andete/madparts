#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos;
varying float round2;
varying vec2 scale2;

void main() {
  float rx = (scale2.x / 2) * round2;
  float ry = (scale2.y / 2) * round2;
  float r = min(rx, ry); // we want round corners for now
  float ax = (scale2.x / 2) - r;
  float ay = (scale2.y / 2) - r;
  if (abs(pos.x) > ax && abs(pos.y) > ay) {
    // corcle zone
    float x = (abs(pos.x) - ax) / r;
    float y = (abs(pos.y) - ay) / r;
    float dist = x * x + y * y;
    if (dist <= 1)
      gl_FragColor = gl_Color;
  } else {
    // square zone
    gl_FragColor = gl_Color;
  }
}
