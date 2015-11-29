#format 1.1
#name PIN 1X4 SMD Samtec TSM
#desc 4 pin pinheader
footprint = () ->

  d = 2.54
  n = 4
  dy = 3.43
  height = 6.35
  offset = height/2-dy/2

  name = new Name (height-1)
  value = new Value (-height+1)
  
  smd = new Smd
  smd.dy = d/2
  smd.dx = dy
  smd.ro = 25

  units = single smd, n, d

  for unit in units
    if unit.name % 2 == 0
     unit.x = -offset
    else
     unit.x = offset
  
  units[0].ro = 100 
  combine [name,value, units]
