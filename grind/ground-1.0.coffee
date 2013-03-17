# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

### SECTION 1: general coffeescript utilities ###

# clone, from http://coffeescriptcookbook.com/chapters/classes_and_objects/cloning
clone = (obj) ->
  if not obj? or typeof obj isnt 'object'
    return obj

  if obj instanceof Date
    return new Date(obj.getTime()) 

  if obj instanceof RegExp
    flags = ''
    flags += 'g' if obj.global?
    flags += 'i' if obj.ignoreCase?
    flags += 'm' if obj.multiline?
    flags += 'y' if obj.sticky?
    return new RegExp(obj.source, flags) 

  newInstance = new obj.constructor()

  for key of obj
    newInstance[key] = clone obj[key]

  return newInstance

# partial application, from http://autotelicum.github.com/Smooth-CoffeeScript/SmoothCoffeeScript.html#entry-partial-application-0
partial = (func, a...) ->
  (b...) -> func a..., b...

# clone and mod an object
mod1 = (obj, key) -> 
  (val) ->
    b = clone(obj)
    b[key] = val
    return b

# generate a range of mods
range = (obj, key, l) ->
  l.map (mod1 obj, key)

steps = (n, dx) ->
  [1..n].map ((x) -> ((-(n+1)/2) + x) * dx)

modl = (l, kv...) ->
  l.map ((o) ->
    o[k] = v for [k,v] in kv
    o)
    
# a... treats a as a argument list
combine = (a) -> [].concat a...

### SECTION 2: type constructors ###

class Smd
  constructor: ->
    @type = 'smd'
    @shape = 'rect'
    @x = 0
    @y = 0
    @dx = 0
    @dy = 0
    
class Rect
  constructor: ->
    @type = 'silk'
    @shape = 'rect'
    @x = 0
    @y = 0
    @dx = 0
    @dy = 0

class Pad
  constructor: ->
    @type = 'pad'

class RoundPad extends Pad
  constructor: (@r, @drill) ->
    super
    @shape = 'disc'

class SquarePad extends Pad
  constructor: (dia, @drill) ->
    super
    @shape = 'rect'
    @dx = dia
    @dy = dia

class LongPad extends Pad
  constructor: (dia, @drill) ->
    super
    @shape = 'rect'
    @ro = 100
    @dx = 2*dia
    @dy = dia

class OctagonPad extends Pad
  constructor: (@r, @drill) ->
    super
    @shape = 'octagon'

class OffsetPad extends Pad
  constructor: (dia, @drill) ->
    super
    @shape = 'rect'
    @ro = 100
    @dx = 2*dia
    @dy = dia
    @drill_dx = -dia/2

class Disc
  constructor: (@r) ->
    @type = 'silk'
    @shape = 'disc'
    @x = 0
    @y = 0

class Circle
  constructor: (@w) ->
    @type = 'silk'
    @shape = 'circle'
    @r = 0
    @x = 0
    @y = 0

class Line
   constructor: (@w) ->
     @type = 'silk'
     @shape = 'line'
     @x1 = 0
     @y1 = 0
     @x2 = 0
     @y2 = 0

class Name
  constructor: (@y) ->
    @type = 'silk'
    @shape = 'label'
    @value = 'NAME'
    @x = 0

class Value
  constructor: (@y) ->
    @type = 'silk'
    @shape = 'label'
    @value = 'VALUE'
    @x = 0

class Label
  constructor: (@value) ->
    @type = 'silk'
    @shape = 'label'
    @x = 0
    @y = 0

### SECTION 4: handy utility functions ###

# adjust item to be rotated 90 degrees anti-clockwise around (0,0)
rotate90 = (item) ->
  if item.type == 'smd' or item.type == 'pad'
    if not item.rot?
      item.rot = 0
    item.rot -= 90
    if item.rot < 0
      item.rot += 360
  else if item.shape == 'line'
    ox1 = item.x1
    oy1 = item.y1
    ox2 = item.x2
    oy2 = item.y2
    item.x1 = -oy1
    item.y1 = ox1
    item.x2 = -oy2
    item.y2 = ox2
  else
    ox = item.x
    oy = item.y
    item.x = -oy
    item.y = ox
  item

rotate180 = (item) -> rotate90 rotate90 item

# adjust a shape in the y direction
adjust_y = (o, dy) ->
  if o.shape == 'line'
    o.y1 += dy
    o.y2 += dy
  else
    if not o.y?
      o.y = 0
    o.y += dy
  o

# adjust a shape in the x direction
adjust_x = (o, dx) ->
  if o.shape == 'line'
    o.x1 += dx
    o.x2 += dx
  else
    if not o.x?
      o.x = 0
    o.x += dx
  o

### SECTION 5: creating ranges of items ###

# create a single vertical range of 'num' units 'distance' apart
single = (unit, num, distance) ->
    y = (num-1) * distance /2
    units = [0...num].map((i) ->
      dy =  - y + i * distance
      unit.map ((item) ->
        item2 = clone item
        adjust_y item2, (-dy)
      )
    )
    combine units

# create a dual vertical range of 'num' units 'distance' apart in the range
# and 'between' apart between the two ranges
dual = (unit, num, distance, between) ->
  s1 = single unit, num, distance
  s2 = single unit, num, distance
  s1 = s1.map ((item) -> adjust_x (rotate180 item), -between/2)
  s2 = s2.map ((item) -> adjust_x item, between/2)
  combine [s1, s2.reverse()]

# create a dual vertical range of 'num' units 'distance' apart in the range
# and 'between' apart between the two ranges
# with alternating numbering like typically used for pin headers
# instead of the typical pin numbering found for chips
alt_dual = (unit, num, distance, between) ->
  s1 = single unit, num, distance
  s1 = s1.map ((item) ->
    i2 = clone item
    i1 = adjust_x (rotate180 item), -between/2
    i2 = adjust_x i2, between/2
    [i1,i2])
  combine s1


# TODO: quad with a unit, simular to single and dual below
quad = (pad, num, step, dist) ->
  adj = 0
  if pad.adj?
    adj = pad.adj
  n = num / 4
  d = dist / 2
  l1  = modl (range pad, 'y', (steps n,  -step)), ['x', -d-adj]
  l2  = modl (range pad, 'x', (steps n,  step)),  ['y', -d-adj], ['rot', 90]
  l3  = modl (range pad, 'y', (steps n,  step)),  ['x', d+adj], ['rot', 180]
  l4  = modl (range pad, 'x', (steps n,  -step)), ['y', d+adj], ['rot', 270]
  combine [l1, l2, l3, l4]

# create a sequence of lines from a list of coordinates
lines = (width, coordinates) ->
    from = coordinates[0]
    coordinates[1..].map ((to) ->
       line = new Line width
       line.x1 = from[0]
       line.y1 = from[1]
       line.x2 = to[0]
       line.y2 = to[1]
       from = to
       line
    )

silk_square = (half_line_size, line_width) ->
    ls = half_line_size
    lines line_width, [[-ls,ls], [ls,ls], [ls,-ls], [-ls,-ls], [-ls,ls]]
