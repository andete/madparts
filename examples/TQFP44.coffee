#format 1.1
#name TQFP44
#desc TQFP44 example
#desc this package is used by e.g. the Atmel ATMEGA1284P-AU

footprint = () ->

  size = 11
  half = size / 2
  half_line_size = half - 1.5
  line_width = 0.25
  num_pads = 44
  e = 0.8

  name = new Name (half + 1.5)
  value = new Value (-half - 1.5)

  pad = new Smd
  pad.dx = 1.67
  pad.dy = 0.36
  pad.ro = 50

  pads = quad pad, num_pads, e, size

  silk = silk_square half_line_size, line_width

  pads[1-1].ro = 100

  dot = new Disc (line_width)
  dot.x = -half 
  dot.y = half - 0.7

  combine [name, value, pads, silk, dot]
