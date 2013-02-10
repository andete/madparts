footprint = () ->

  size = 9
  half = size / 2
  line_size = half - 1.5
  line_width = 0.25
  num_pads = 32
  e = 0.8

  meta =
    name: 'TQFP32'
    id: 'id:e5bd48346acc4d549d678cb059be64ef'
    desc: 'TQFP example'

  name =
    type: 'text'
    name: 'NAME'
    
  value =
    type: 'text'
    name: 'VALUE'

  pad = 
    type: 'smd'
    shape: 'rect'
    dx: 1.67
    dy: 0.36
    ro: 50

  pads = quad pad, num_pads, e, size

  ls = line_size
  silk = lines line_width, [[-ls,ls], [ls,ls], [ls,-ls], [-ls,-ls], [-ls,ls]]

  pads[0].ro = 100

  dot = 
    type: 'silk'
    shape: 'circle'
    r: line_width
    x: -half
    y: half - 1

  combine [pads, silk, dot]
