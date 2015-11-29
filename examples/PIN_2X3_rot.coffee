#format 1.1
#name PIN 2X3_rot
#desc 2X3 pin pinheader

footprint = () ->

  d = 2.54
  drill = 1
  w = 0.15
  pad_r = (d-0.34)/2
  n = 6

  name = new Name (4*d/4+1)
  value = new Value (-4*d/4-1)
  
  # the basic pad
  pad = new OctagonPad pad_r, drill

  # create a nice octagon around the pad
  # # horizontal parts
  silk1 = new Line w
  silk1.x1 = d/2
  silk1.y1 = -d/4
  silk1.x2 = d/2
  silk1.y2 = d/4
  silk2 = rotate90 clone silk1
  silk3 = rotate90 clone silk2
  silk4 = rotate90 clone silk3 
  # # diagonal parts
  silk5 = new Line w
  silk5.y1 = d/4
  silk5.x1 = d/2
  silk5.y2 = d/2
  silk5.x2 = d/4
  silk6 = rotate90 clone silk5
  silk7 = rotate90 clone silk6
  silk8 = rotate90 clone silk7

  unit = [pad, silk1, silk2, silk3, silk4, silk5, silk6, silk7, silk8]

  units = rot_dual unit, n, d, d
  units[0].shape='disc'

  combine [name,value, units]
