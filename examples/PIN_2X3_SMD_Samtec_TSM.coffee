#format 1.1
#name PIN 2X3 SMD Samtec TSM
#id d7b5175613384e6f977e7df3eedf184d
#parent d01beefd36ad45d7b724129e9dc8bfd4
#desc 2x3 pin pinheader SMD
footprint = () ->

  d = 2.54
  n = 6
  dx = 3.68
  between = d/2+dx

  name = new Name (n*d/4+1)
  value = new Value (-n*d/4-1)
  
  smd = new Smd
  smd.dx = dx
  smd.dy = d/2
  smd.ro = 25

  units = alt_dual smd, n, d, between
 
  units[0].ro = 100
  combine [name,value, units]