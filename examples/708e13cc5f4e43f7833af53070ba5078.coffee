#format 1.0
#name PIN 1X2
#id 708e13cc5f4e43f7833af53070ba5078
#desc 2 pin pinheader
footprint = () ->

  d = 2.54
  drill = 1
  w = 0.15
  pad_r = (d-0.24)/2
  n = 1

  name = new Name (d/2+0.5)
  value = new Value (-d/2-0.5)
  
  pad = new Pad
  pad.r = pad_r
  pad.shape = 'disc'
  pad.drill = drill

  silk1 = new Line w
  silk1.x1 = d/2
  silk1.y1 = -d/4
  silk1.x2 = d/2
  silk1.y2 = d/4
  silk2 = rotate90 silk1
  silk3 = rotate90 silk2
  silk4 = rotate90 silk3

  silk5 = new Line w
  silk5.y1 = d/4
  silk5.x1 = d/2
  silk5.y2 = d/2
  silk5.x2 = d/4
  silk6 = rotate90 silk5
  silk7 = rotate90 silk6
  silk8 = rotate90 silk7

  unit = [pad, silk1, silk2, silk3, silk4, silk5, silk6, silk7, silk8]

  combine [name,value, unit]
