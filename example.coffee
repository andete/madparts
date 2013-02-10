footprint = () ->

  meta =
    name: "TQFP32"
    id: "id:e5bd48346acc4d549d678cb059be64ef"
    desc: "TQFP example"

  pad = 
    type: 'smd'
    shape: 'rect'
    dx: 1.67
    dy: 0.36
    ro: 50

  pads = quad pad, 32, 0.8, 9

  silk = lines [-3,3], [3,3], [3,-3], [-3,-3], [-3,3]

  pads[0].ro = 100

  dot = 
    type: 'silk'
    shape: 'circle'
    r: 0.25
    x: -4.5
    y: 3.5

  combine [pads, silk, dot]
