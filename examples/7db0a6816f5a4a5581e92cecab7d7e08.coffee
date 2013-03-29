#format 1.0
#name JEDEC_MS-012-AA_SOIC
#id 7db0a6816f5a4a5581e92cecab7d7e08
footprint = () ->

  e = 1.27
  dx = 2.2
  dy = 0.6

  between = 5.2
  half = between/2
  n = 8
  line_width = 0.127
  out_y = n*e/4

  smd = new Smd
  smd.dx = dx
  smd.dy = dy

  pads = dual smd, n, e, between

  name = new Name out_y+e/2
  value = new Value -(out_y+e/2)

  # top horizontal line
  silk1 = new Line line_width
  silk1.x1 = -half
  silk1.y1 = out_y
  silk1.x2 = half
  silk1.y2 = out_y

  # bottom horizontal line
  silk2 = rotate180 clone silk1

  # indicator dot
  silk3 = new Disc
  silk3.x = -half
  silk3.y = out_y+e/2
  silk3.r = e/4

  # vertical line one
  silk4 = new Line line_width
  silk4.x1 = -(half-dx/2-line_width*2)
  silk4.y1 = out_y
  silk4.x2 = -(half-dx/2-line_width*2)
  silk4.y2 = -out_y

  # other vertical line
  silk5 = rotate180 clone silk4

  # little square
  silk6 = new Line line_width
  silk6.x1 = -half/4
  silk6.y1 = out_y-e/2
  silk6.x2 = -half/4
  silk6.y2 = out_y
  silk7 = new Line line_width
  silk7.x1 = -(half-dx/2-line_width*2)
  silk7.y1 = out_y-e/2
  silk7.x2 = -half/4
  silk7.y2 = out_y-e/2

  silks = [silk1, silk2, silk3, silk4, silk5, silk6, silk7]

  combine [name, silks, value, pads]
