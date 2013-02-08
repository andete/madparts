#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos;
varying float radius;
void main() {
  float dist = radius * radius - pos.x * pos.x - pos.y * pos.y;
  if (dist > 0)
    gl_FragColor = gl_Color;
   else
    gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
   // alpha channel is not working unfortunately :(
}
