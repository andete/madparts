footprint = () ->

  size = 9
  half = size / 2
  line_size = half - 1.5
  line_width = 0.25
  num_pads = 32
  e = 0.8

  meta =
    type: 'meta'
    name: 'TQFP32'
    id: 'e5bd48346acc4d549d678cb059be64ef'
    desc: 'TQFP32 example'

  # this package is used by e.g. the Atmel ATMEGA328P-AU

  name = new Name (half + 1.5)
  value = new Value (-half - 1.5)

  pad = new Smd
  pad.dx = 1.67
  pad.dy = 0.36
  pad.ro = 50

  pads = quad pad, num_pads, e, size

  ls = line_size
  silk = lines line_width, [[-ls,ls], [ls,ls], [ls,-ls], [-ls,-ls], [-ls,ls]]

  pads[0].ro = 100

  dot = new Dot(line_width)
  dot.x = -half
  dot.y = half - 1

  combine [meta, name, value, pads, silk, dot]
