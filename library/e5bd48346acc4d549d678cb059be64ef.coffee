#format 1.0
#name TQFP32
#id e5bd48346acc4d549d678cb059be64ef
#desc TQFP32 example
#desc this package is used by e.g. the Atmel ATMEGA328P-AU

footprint = () ->

  size = 9
  half = size / 2
  half_line_size = half - 1.5
  line_width = 0.25
  num_pads = 32
  e = 0.8
  pad_len_adj = 0.0

  name = new Name (half + 1.5 + pad_len_adj)
  value = new Value (-half - 1.5 - pad_len_adj)

  pad = new Smd

  pad.dx = 1.67 + pad_len_adj
  pad.dy = 0.36
  pad.ro = 50
  pad.adj = pad_len_adj/2
  #pad.drill = 0.1
  #pad.drill_dx = -0.5

  pads = quad pad, num_pads, e, size

  silk = silk_square half_line_size, line_width

  pads[0].ro = 100

  dot = new Dot line_width
  dot.x = -half
  dot.y = half - 1
  #dot.dx = 1
  #dot.shape = 'octagon'

  combine [name, value, pads, silk, dot]
