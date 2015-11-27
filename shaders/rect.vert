#version 120

// (c) 2013-2015 Joost Yervante Damad <joost@damad.be>
// License: GPL

// scale unit square to our rect size
// and move to it's origin

// input:
uniform vec2 size;  // size in x and y direction
uniform vec2 move;  // location
uniform vec2 round; // roundness of corners
uniform vec2 drill; // drill diameter
uniform vec2 drill_offset;

// output:
varying vec2 pos2;    // adjusted position
varying float round2; // roundness of corners
varying vec2 size2;   // size in x and y direction
varying vec2 drill2; // drill: radius
varying vec2 drill_offset2;

void main() {
  gl_FrontColor = gl_Color;
  vec4 vert = gl_Vertex;
  vert.x = vert.x * size.x;
  vert.y = vert.y * size.y;
  vec4 vert2 = vert;
  vert2.x += move.x;
  vert2.y += move.y;
  gl_Position = gl_ModelViewProjectionMatrix * vert2;
  pos2 = vec2(vert);
  round2 = round.x;
  drill2 = drill;
  size2 = size;
  drill_offset2 = drill_offset;
}
