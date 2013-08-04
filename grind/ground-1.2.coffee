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

clone_modl = (l, k, v) ->
    l.map ((o) ->
      o2 = clone o
      o2[k] = v
      o2)

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

reverse = (x) -> x.reverse()

make_sure_is_array = (unit) ->
  if not (unit instanceof Array)
    [unit]
  else
    unit

generate_names = (l, i=0) ->
  for smd in l
    if smd['type'] in ['smd', 'pad']
      smd.name = (i+1)
      i = i + 1
  l

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

class RectPad extends Pad
  constructor: (@dx, @dy, @drill) ->
    super
    @shape = 'rect'
    
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

class Hole
  constructor: (@drill) ->
    @type = 'hole'
    @shape = 'hole'
    @x = 0
    @y = 0
            
class Vertex
  constructor: (@x1, @y1, @x2, @y2, @curve=0) ->
    @shape = 'vertex'

class Line extends Vertex
  constructor: (@w) ->
    super
    @type = 'silk'
    @x1 = 0
    @y1 = 0
    @x2 = 0
    @y2 = 0

class Arc extends Vertex
  constructor: (@w) ->
    super
    @type = 'silk'
    @x1 = 0
    @y1 = 0
    @x2 = 0
    @y2 = 0
    @curve = 0

class Polygon
  constructor: (@w) ->
    @type = 'silk'
    @shape = 'polygon'
    @v = []
    
    @start = (x1, y1) ->
      @lastx = x1
      @lasty = y1
    
    @add = (x1, y1, curve=0) ->
      vertex = new Vertex @lastx, @lasty, x1, y1, curve
      @v = @v.concat([vertex])
      @lastx = x1
      @lasty = y1

    @end = (curve) ->
      x1 = @v[0].x1
      y1 = @v[0].y1
      vertex = new Vertex @lastx,@lasty, x1, y1, curve
      @v = @v.concat([vertex])

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

rotate90pad = (item) ->
  if not item.rot?
    item.rot = 0
  item.rot -= 90
  if item.rot < 0
    item.rot += 360
  item

rotate90_1 = (item) ->
  if item.type == 'smd' or item.type == 'pad'
    rotate90pad item
  else if item.shape == 'line' or item.shape == 'vertex'
    ox1 = item.x1
    oy1 = item.y1
    ox2 = item.x2
    oy2 = item.y2
    item.x1 = -oy1
    item.y1 = ox1
    item.x2 = -oy2
    item.y2 = ox2
  else if item.shape == 'polygon'
    item.v.map rotate90_1
  else
    if not item.x?
      item.x = 0
    if not item.y?
      item.y = 0
    ox = item.x
    oy = item.y
    item.x = -oy
    item.y = ox
  item

# adjust item to be rotated 90 degrees anti-clockwise around (0,0)
rotate90 = (item) ->
  if item instanceof Array
    item.map rotate90_1
  else
    rotate90_1 item

rotate180 = (item) -> rotate90 (rotate90 item)
rotate180pad = (item) -> rotate90pad (rotate90pad item)

rotate270 = (item) -> rotate90 (rotate180 item)
rotate270pad = (item) -> rotate90pad (rotate180pad item)

mirror1_y = (item) ->
  if item.type == 'smd' or item.type == 'pad'
    rotate180pad item
  else if item.shape == 'line' or item.shape == 'vertex'
    item.x1 = -item.x1
    item.x2 = -item.x2
    item.curve = -item.curve
  else if item.shape == 'polygon'
    item.v.map mirror1_y
  else
    if not item.x?
      item.x = 0
    item.x = -item.x
  item

mirror_y = (item) ->
  if item instanceof Array
    item.map mirror1_y
  else
    mirror1_y item

mirror1_x = (item) ->
  if item.type == 'smd' or item.type == 'pad'
    rotate180pad item
  else if item.shape == 'line' or item.shape == 'vertex'
    item.y1 = -item.y1
    item.y2 = -item.y2
    item.curve = -item.curve
  else if item.shape == 'polygon'
    item.v.map mirror1_x
  else
    if not item.y?
      item.y = 0
    item.y = -item.y
  item
 
mirror_x = (item) ->
  if item instanceof Array
    item.map mirror1_x
  else
    mirror1_x item

# adjust a shape in the y direction
adjust1_y = (dy, o) ->
  if o.shape == 'line' or o.shape == 'vertex'
    o.y1 += dy
    o.y2 += dy
  else if o.shape == 'polygon'
    o.v.map (partial adjust1_y, dy)
  else
    if not o.y?
      o.y = 0
    o.y += dy
  o

adjust_y = (o, dy) ->
  if o instanceof Array
    o.map (partial adjust1_y, dy)
  else
    adjust1_y dy, o

# adjust a shape in the x direction
adjust1_x = (dx, o) ->
  if o.shape == 'line' or o.shape == 'vertex'
    o.x1 += dx
    o.x2 += dx
  else if o.shape == 'polygon'
   o.v.map (partial adjust1_x, dx)
  else
    if not o.x?
      o.x = 0
    o.x += dx
  o

adjust_x = (o, dx) ->
  if o instanceof Array
    o.map (partial adjust1_x, dx)
  else
    adjust1_x dx, o

adjust = (o, dx, dy) ->
  adjust_y (adjust_x o, dx), dy

### SECTION 5: creating ranges of items ###

# create a single vertical range of 'num' units 'distance' apart
single = (unit, num, distance) ->
  unit = make_sure_is_array unit
  y = (num-1) * distance /2
  units = [0...num].map((i) ->
    dy =  - y + i * distance
    unit.map ((item) ->
      item2 = clone item
      adjust_y item2, (-dy)
    )
  )
  generate_names (combine units)

# create a horizontal range of 'num' units 'distance' apart
rot_single = (unit, num, distance) ->
  unit = make_sure_is_array unit
  x = (num-1) * distance /2
  units = [0...num].map((i) ->
    dx =  - x + i * distance
    unit.map ((item) ->
      item2 = clone item
      adjust_x item2, dx
    )
  )
  generate_names (combine units)

# create a dual vertical range of 'num' units 'distance' apart in the range
# and 'between' apart between the two ranges
dual = (unit, num, distance, between) ->
  num = Math.floor(num / 2)
  unit = make_sure_is_array unit
  s1 = single unit, num, distance
  s1 = s1.map ((item) -> adjust_x (rotate180pad item), -between/2)
  s2 = s1.map ((item) -> rotate180 (clone item))
  generate_names (combine [s1, s2])

# create a dual vertical range of 'num' units 'distance' apart in the range
# and 'between' apart between the two ranges
# with alternating numbering like typically used for pin headers
# instead of the typical pin numbering found for chips
alt_dual = (unit, num, distance, between) ->
  num = Math.floor(num / 2)
  unit = make_sure_is_array unit
  s1 = single unit, num, distance
  s1 = s1.map ((item) ->
    i1 = adjust_x (rotate180pad item), -between/2
    i2 = mirror_y (clone i1)
    [i1,i2])
  generate_names (combine s1)

# create a dual horizontal range of 'num' units 'distance' apart in the range
# and 'between' apart between the two ranges
rot_dual = (unit, num, distance, between) ->
  num = Math.floor(num / 2)
  unit = make_sure_is_array unit
  s1 = rot_single unit, num, distance
  s1 = s1.map ((item) -> adjust_y (rotate90pad item), -between/2)
  s2 = s1.map ((item) -> rotate180 (clone item))
  generate_names (combine [s1, s2])

# create a dual horizontal range of 'num' units 'distance' apart in the range
# and 'between' apart between the two ranges
# with alternating numbering like typically used for pin headers
# instead of the typical pin numbering found for chips
alt_rot_dual = (unit, num, distance, between) ->
  num = Math.floor(num / 2)
  unit = make_sure_is_array unit
  s1 = rot_single unit, num, distance
  s1 = s1.map ((item) ->
    i1 = adjust_y (rotate90pad item), -between/2
    i2 = mirror_x (clone i1)
    [i1,i2])
  generate_names (combine s1)

# create a quad of 'num' units 'distance' apart in the range
# and 'between' apart between the opposide sides
quad = (unit, num, distance, between) ->
  unit = make_sure_is_array unit
  n = Math.floor(num / 4)
  b = between / 2
  s1 = single unit, n, distance
  s1 = s1.map ((item) -> adjust_x (rotate180pad item), -between/2)
  s2 = s1.map ((item) -> rotate90 (clone item))
  s3 = s2.map ((item) -> rotate90 (clone item))
  s4 = s3.map ((item) -> rotate90 (clone item))
  generate_names (combine [s1,s2,s3,s4])

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

make_rect = (dx, dy, line_width, type) ->
    x2 = dx/2
    y2 = dy/2
    l = lines line_width, [[-x2,-y2],[x2,-y2],[x2,y2],[-x2,y2],[-x2,-y2]]
    l.map ((o) ->
        o.type = type
        o)
