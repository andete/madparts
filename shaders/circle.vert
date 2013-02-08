#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos;
void main() {
  gl_FrontColor = gl_Color;
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  pos = vec2(gl_Vertex);
}
