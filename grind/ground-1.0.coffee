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

### SECTION 3: handy utility functions ###

rotate90 = (o) ->
  b = clone(o)
  if b.shape == 'line'
    b.x1 = -o.y1
    b.y1 = o.x1
    b.x2 = -o.y2
    b.y2 = o.x2
  else
    b.x = -o.y
    b.y = o.x
  b

# a... treats a as a argument list
combine = (a) -> [].concat a...

# this is just temporarely
lines = (wi, a) ->
    b = a[0]
    a[1..].map ((c) ->
       line =
         type: 'silk'
         shape: 'line'
         x1: b[0]
         y1: b[1]
         x2: c[0]
         y2: c[1]
         w: wi
       b = c
       line
    )

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

silk_square = (half_line_size, line_width) ->
    ls = half_line_size
    lines line_width, [[-ls,ls], [ls,ls], [ls,-ls], [-ls,-ls], [-ls,ls]]

adjust_y = (o, dy) ->
  if o.shape == 'line'
    o.y1 += dy
    o.y2 += dy
  else
    if not o.y?
      o.y = 0
    o.y += dy
  o

adjust_x = (o, dx) ->
  if o.shape == 'line'
    o.x1 += dx
    o.x2 += dx
  else
    if not o.x?
      o.x = 0
    o.x += dx
  o

single = (unit, n, d) ->
    y = (n-1) * d /2
    adapt = (o, dy) ->
      o2 = clone o
      adjust_y o2, (-dy)
    units = [0...n].map((x) ->
        unit.map((o) ->
          adapt(o, - y + x * d)))
    combine units

# TODO: allow alternating numbering for dual
dual = (unit, n, d, e) ->
  s1 = single unit, n, d
  s2 = single unit, n, d
  s1 = s1.map ((o) -> adjust_x o, -e/2)
  s2 = s2.map ((o) -> adjust_x o, e/2)
  combine [s1, s2.reverse()]
