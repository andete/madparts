# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

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

rot = (o) ->
   b = clone(o)
   b.dx = o.dy
   b.dy = o.dx
   b

rotl = (l) -> l.map rot

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

quad = (pad, num, step, dist) ->
  n = num / 4
  d = dist / 2
  l1  = modl (range pad, 'y', (steps n,  -step)), ['x', -d]
  l2  = modl (range pad, 'x', (steps n,  step)),  ['y', -d], ['rot', 90]
  l3  = modl (range pad, 'y', (steps n,  step)),  ['x', d], ['rot', 180]
  l4  = modl (range pad, 'x', (steps n,  -step)), ['y', d], ['rot', 270]
  combine [l1, l2, l3, l4]

make_name = (yi) ->
  a =
    type: 'label'
    value: 'NAME'
    y: yi
  a

make_value = (yi) ->
  a =
    type: 'label'
    value: 'VALUE'
    y: yi
  a
