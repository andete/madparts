#version 120
varying vec2 uv;
void main() {
  float border = 0.01;
  float radius = 0.5;
  vec4 color0 = vec4(0.0, 0.0, 0.0, 1.0);
  vec4 color1 = vec4(1.0, 1.0, 1.0, 1.0);
  float dist = radius - sqrt(uv.x * uv.x + uv.y * uv.y);
  float t = 0.0;
  if (dist > border)
     t = 1.0;
  else if (dist > 0.0)
     t = dist / border;
  gl_FragColor = mix(color0, color1, t);
}
