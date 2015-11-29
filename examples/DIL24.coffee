#format 1.1
#name DIL24

footprint = () ->

  n = 24
  e = 2.54
  between = 7.62
  diameter = 1.2
  drill = 0.8
  line_width = 0.3
  outer_y = n*e/4
  half = between/2

  name = new Name outer_y+e/3
  value = new Value -outer_y-e/3

  pad = new LongPad diameter, drill
  l = dual [pad], n, e, between

  l[1-1].shape = 'disc'
  l[1-1].r = diameter*3/4

  silk1 = new Line line_width
  silk1.x1 = half-diameter-0.5
  silk1.y1 = outer_y
  silk1.x2 = half-diameter-0.5
  silk1.y2 = -outer_y

  silk2 = rotate180 clone silk1

  silk3 = new Line line_width
  silk3.y1 = outer_y
  silk3.x1 = half-diameter-0.5
  silk3.y2 = outer_y
  silk3.x2 = -half+diameter+0.5

  silk4 = rotate180 clone silk3

  silks = [silk1, silk2, silk3, silk4]

  combine [l,name,silks,value]
