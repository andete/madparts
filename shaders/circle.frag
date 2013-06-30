#version 120

// (c) 2013 Joost Yervante Damad <joost@damad.be>
// License: GPL

varying vec2 pos2;    // location
varying vec2 radius2; // outer radius
varying vec2 inner2;  // inner radius
varying float drill2; // drill: radius
varying vec2 drill_offset2;
varying vec2 angles2;

void main() {
  // default to transparent
  gl_FragColor = vec4(0,0,0,0);


  float unit_x = pos2.x / radius2.x;
  float unit_y = pos2.y / radius2.y;


  float unit_dist_sq = unit_x * unit_x + unit_y * unit_y;

  float unit_ix = pos2.x / inner2.x;
  float unit_iy = pos2.y / inner2.y;

  float unit_idist_sq = unit_ix * unit_ix + unit_iy * unit_iy;

  if (unit_dist_sq <= 1 && unit_idist_sq >= 1) {

    float drill_x = pos2.x - drill_offset2.x;
    float drill_y = pos2.y - drill_offset2.y;

    float drill_dist_sq = drill_x * drill_x + drill_y * drill_y;

    float drill_r = drill2/2;
    float drill_r_sq = drill_r * drill_r;

    if (drill_dist_sq >= drill_r_sq) {
      if (abs(angles2.x - angles2.y) < 0.008) {
        gl_FragColor = gl_Color;
      } else {
        float pi = 3.141592653589793;
        float s =  sqrt(unit_dist_sq);
        float a_cos = unit_x / s;
        float a_sin = unit_y / s;
        float a1 = acos(a_cos); // 0 -> pi degrees
        float a2 = asin(a_sin); // -pi/2 -> pi/2 degrees
        // use sinus to see if we're above or below the x-axis
        if (a2 < 0.0) {
          a1 = 2*pi - a1;
        }
        float min_a = min(angles2.x, angles2.y);
        float max_a = max(angles2.x, angles2.y);
        if (min_a <= a1 && a1 <= max_a) {
          gl_FragColor = gl_Color;
        }
      } 
    }
  }
}
