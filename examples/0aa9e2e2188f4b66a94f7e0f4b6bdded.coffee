#format 1.2
#name Polygon
#id 0aa9e2e2188f4b66a94f7e0f4b6bdded
#desc a simple polygon example

footprint = () ->
  p = new Polygon 0.1
  p.type = 'test'
  p.start 0, 1
  p.add 1, 0, 90
  p.add 0, -1, 0
  p.add -1,0, 0
  p.add 0,1, 0

  a  = 45
  c = new Circle 0.1
  c.r = 2
  c.a1 = a
  c.a2 = a+180

  [p, c]
