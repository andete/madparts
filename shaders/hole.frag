#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos2;    // location
varying vec2 radius2; // outer radius

void main() {
  gl_FragColor = vec4(0,0,0,0);
  float x = pos2.x / radius2.x;
  float y = pos2.y / radius2.y;
  float dist = x * x + y * y;
  float delta_dist = 1.0 - dist; // distance from circle edge
  float delta_xy = abs(abs(x)-abs(y)); // abs distance between abs x and abs y
  if (
       (delta_dist >= 0 && delta_dist < 0.1) || // circle edge
       (delta_xy < 0.05 && dist <= 1.0) // internal cross
      ) {
    gl_FragColor = gl_Color;
  }
}
