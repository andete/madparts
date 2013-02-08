#version 120
varying vec2 pos;
void main() {
  gl_FrontColor = gl_Color;
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  pos = vec2(gl_Vertex);
}
