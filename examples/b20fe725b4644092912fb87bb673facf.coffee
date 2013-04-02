#format 1.1
#name NUM_IV-9
#id b20fe725b4644092912fb87bb673facf
#desc Numitron IV-9 pinout

footprint = () ->
  line_width = 0.1
  pad_r_adj = 0.0

  name = new Name 6.5
  value = new Value -6.5

  # pad maker function
  make = (x,y) ->
    pad = new RoundPad 0.75+pad_r_adj, 1.0
    pad.x = x
    pad.y = y
    pad

  # construct a list of pads
  pads = [
    make 0, -3.675
    make 2.345, -2.79
    make 3.675, -0.655
    make 3.425, 1.5
    make 1.79, 3.155
    make -0.615, 3.675
    make -2.655, 2.425
    make -3.675, 0.27
    make -3.175, -1.885
  ]
  
  label = new Label 'IV-9'
  label.dy = 1

  silk1 = new Line line_width
  silk1.x1 = -2.0
  silk1.y1 = -5.0
  silk1.x2 = 2.0
  silk1.y2 = -5.0
  silk2 = new Line line_width
  silk2.x1 = -2.25
  silk2.y1 = -4.75
  silk2.x2 = 2.25
  silk2.y2 = -4.75
  silk3 = new Circle line_width
  silk3.x = 0.0
  silk3.y = 0.0
  silk3.r = 5.6335
  silk4 = new Circle line_width
  silk4.x = 0.0
  silk4.y = 0.0
  silk4.r = 2.8135-pad_r_adj
  silks = [silk1, silk2, silk3, silk4]

  combine [name,value,label,pads,silks]
