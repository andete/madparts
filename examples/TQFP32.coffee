#format 2.0
#name TQFP32
#desc TQFP32 example
#desc this package is used by e.g. the Atmel ATMEGA328P-AU

footprint = () ->

  size = 9
  half = size / 2
  half_line_size = half - 1.5
  line_width = 0.25
  num_pads = 32
  e = 0.8
  pad_len_adj = 0.5

  name = new Name (half + 1.5 + pad_len_adj)
  value = new Value (-half - 1.5 - pad_len_adj)

  pad = new Smd
  pad.dx = 1.67 + pad_len_adj
  pad.dy = 0.36
  pad.ro = 50

  pads = quad [pad], num_pads, e, size + pad_len_adj/2

  silk = silk_square half_line_size, line_width

  # make pad 1 round
  pads[1-1].ro = 100

  # draw a little dot near pin 1
  dot = new Disc line_width
  dot.x = -half
  dot.y = half - 1
 
  # draw a cute circle in the middle
  dut = new Circle line_width
  dut.r = 1

  combine [name, value, pads, silk, dot, dut]
