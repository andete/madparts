#format 1.1
#name PIN 1X4 SMD Samtec TSM
#id d01beefd36ad45d7b724129e9dc8bfd4
#parent 8e50c735f8324b00a18c9b34840053de
#desc 4 pin pinheader
footprint = () ->

  d = 2.54
  n = 4
  dy = 3.43
  height = 6.35
  offset = height/2-dy/2

  name = new Name (height/2+1)
  value = new Value (-height/2-1)
  
  smd = new Smd
  smd.dx = d/2
  smd.dy = dy

  units = rot_single smd, n, d

  for unit in units
    if unit.name % 2 == 0
     unit.y = -offset
    else
     unit.y = offset
  
  units[0].ro = 100
  
     

  combine [name,value, units]