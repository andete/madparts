#format 1.1
#name 0603
#id 10644a0b9a3a4f2a8a8b0add2ba7ce21
#parent dc93599ddebd4bf8a02e4beef8a09b8b
#desc Generic 0603 footprint

footprint = () ->
  smd = new Smd
  smd.dx = 1.1
  smd.dy = 1.0
  l = rot_single [smd], 2, 1.7

  name = new Name 1.4
  value = new Value -1.4

  kx = 1.6
  ky = 0.75
  keepout1 = new Line 0.1
  keepout1.x1 = -kx
  keepout1.y1 = ky
  keepout1.x2 = kx
  keepout1.y2 = ky
  keepout1.type = 'keepout'
  keepout2 = new Line 0.1
  keepout2.x1 = kx
  keepout2.y1 = ky
  keepout2.x2 = kx
  keepout2.y2 = -ky
  keepout2.type = 'keepout'
  keepout3 = mirror_x clone keepout1
  keepout4 = mirror_y clone keepout2

  keepout = [keepout1, keepout2, keepout3, keepout4]

  silk = clone_modl keepout, 'type', 'silk'

  docu1 = new Line 0.1
  docu1.x1 = -0.35
  docu1.y1 = 0.45
  docu1.x2 = 0.35
  docu1.y2 = 0.45
  docu1.type = 'docu'
  docu2 = mirror_x clone docu1
  docu3 = new Rect
  docu3.dx = 0.5
  docu3.dy = 1
  docu3.x = -0.6
  docu3.type = 'docu'
  docu4 = mirror_y clone docu3
  docu4.type = 'docu'

  docu = [docu1, docu2, docu3, docu4]
  
  combine [name ,value, l,  docu, keepout, silk]