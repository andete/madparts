#version 120
attribute vec2 coord2d;
varying vec2 uv;
void main() {
  gl_Position = vec4(coord2d, 0.0, 1.0);
  uv = coord2d;
}
