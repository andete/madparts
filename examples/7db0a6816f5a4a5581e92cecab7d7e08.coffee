#format 1.0
#name JEDEC_MS-012-AA_manual
#id 7db0a6816f5a4a5581e92cecab7d7e08
footprint = () ->

  name = new Name 3.5814
  name.x = -0.2794
  value = new Value -3.5052
  value.x = -0.381

  silk1 = new Line 0.127
  silk1.x1 = -1.95
  silk1.y1 = 2.54
  silk1.x2 = 1.95
  silk1.y2 = 2.54
  silk10 = new Line 0.127
  silk10.x1 = -0.635
  silk10.y1 = 1.905
  silk10.x2 = -0.635
  silk10.y2 = 2.54
  silk2 = new Line 0.127
  silk2.x1 = 1.95
  silk2.y1 = -2.54
  silk2.x2 = -1.95
  silk2.y2 = -2.54
  silk3 = new Circle 0.127
  silk3.x = -2.54
  silk3.y = 3.175
  silk3.r = 0.3635
  silk6 = new Line 0.127
  silk6.x1 = -1.27
  silk6.y1 = 2.54
  silk6.x2 = -1.27
  silk6.y2 = 1.905
  silk7 = new Line 0.127
  silk7.x1 = -1.27
  silk7.y1 = 1.905
  silk7.x2 = -1.27
  silk7.y2 = -2.54
  silk8 = new Line 0.127
  silk8.x1 = 1.27
  silk8.y1 = 2.54
  silk8.x2 = 1.27
  silk8.y2 = -2.54
  silk9 = new Line 0.127
  silk9.x1 = -1.27
  silk9.y1 = 1.905
  silk9.x2 = -0.635
  silk9.y2 = 1.905

  smd = new Smd
  smd.dx = 2.2
  smd.dy = 0.6

  pads = dual smd, 8, 1.27, 5.2

  combine [name,silk1,silk10,silk2,silk3,silk6,silk7,silk8,silk9,value, pads]
