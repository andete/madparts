#format 1.2
#name Polygon
#id 0aa9e2e2188f4b66a94f7e0f4b6bdded
#desc a simple polygon example

footprint = () ->
  p = new Polygon 0.1
  p.type = 'docu'
  p.start 0, 1
  p.add -1, 0, 180
  p.add 0, -1, 180
  p.add 1, 0, -10
  p.end -10

  p2 = new Polygon 0.05
  p2.type = 'docu'
  p2.start 1, 0
  p2.add 3, 2, 40
  p2.add 4,0, -45
  p2.add 3,-2,-40
  p2.end 40

  p3 = new Polygon 0.1
  p3.start -1,-1
  p3.add -1, 1
  p3.add 0, 1
  p3.add 1, 0, -90
  p3.end -70
  rotate90 p3, -1
  adjust_y p3, -3

  p4 = new Polygon 0.05
  p4.start 1,1
  p4.add 1,0
  p4.add 0,1
  p4.end 0
  adjust p4, 0.1, 0.2

  angle  = 45
  c = new Circle 0.2
  c.r = 2
  c.a1 = angle
  c.a2 = angle+180

  a = new Arc 0.075
  a.x1 = 2
  a.y1 = -1
  a.x2 = 1
  a.y2 = -0.5
  a.curve = 30

  [p, c, p2, p3, p4, a]
