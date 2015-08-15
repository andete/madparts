# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

# TODO: rework approach

import string, copy
from functools import partial

from mutil.mutil import *

def valid(varname, g, vl):
  def make_valid(c):
    if not c in (string.ascii_letters + string.digits):
      return "_%s_" % (g.next())
    else:
      return c
  varname = ''.join([make_valid(x) for x in varname])
  retname = varname
  i = 2
  while (retname in vl):
    retname = "%s_%d"  % (varname, i)
    i += 1
  return retname

def new_coffee_meta(meta):
  a = """\
#format 2.0
#name %s
#id %s
""" % (meta['name'], meta['id'])
  if meta['desc'] == None: return a
  for line in meta['desc'].splitlines():
    a = a + ("#desc %s\n" % (line))
  return a

def _add_if(x, a, varname, key, quote = False):
  if key in x:
    if type(x[key]) == type(42.1):
      if f_eq(x[key], 0.0):
        return a
    if type(x[key]) == type(1):
      if x[key] == 0:
        return a
    if not quote:
      a = a + "%s.%s = %s\n" % (varname, key, x[key])
    else:
      a = a + "%s.%s = '%s'\n" % (varname, key, x[key])
  return a

def _simple_rect(prefix, constructor, x, g, vl, ll):
  if 'name' in x:
    name = x['name']
  else:
    name = str(g.next())
  varname = valid("%s%s" % (prefix, name), g, vl)
  a = """\
%s = new %s
""" % (varname, constructor)
  a = _add_if(x, a, varname, 'dx')
  a = _add_if(x, a, varname, 'dy')
  a = _add_if(x, a, varname, 'name', True)
  a = _add_if(x, a, varname, 'rot')
  a = _add_if(x, a, varname, 'ro')
  a = _add_if(x, a, varname, 'x')
  a = _add_if(x, a, varname, 'y')
  vl.append(varname)
  ll.append(a)
  return varname

def simple_smd_rect(t, g, x, vl, ll):
  _simple_rect('smd', 'Smd', x, g, vl, ll)

def simple_pad_rect(t, g, x, vl, ll):
  name = str(g.next())
  varname = valid("pad%s" % (name), g, vl)
  dx = x['dx']
  dy = x['dy']
  drill = x['drill']
  ro = 0
  if 'ro' in x:
    ro = x['ro']
  if dx == dy:
    a = """\
%s = new SquarePad %s, %s
""" % (varname, dx, drill)
    a = _add_if(x, a, varname, 'ro')
  elif dx == 2*dy and ro == 100:
    if 'drill_dx' in x and x['drill_dx'] == -dy/2:
      a = """\
%s = new OffsetPad %s, %s
""" % (varname, dy, drill)
    else:
      a = """\
%s = new LongPad %s, %s
""" % (varname, dy, drill)
  else:
    a = """\
%s = new RectPad %s, %s, %s
""" % (varname, dx, dy, drill)
    a = _add_if(x, a, varname, 'ro')

  a = _add_if(x, a, varname, 'name', True)
  a = _add_if(x, a, varname, 'rot')
  a = _add_if(x, a, varname, 'x')
  a = _add_if(x, a, varname, 'y')
  vl.append(varname)
  ll.append(a)
    
def _simple_t_rect(t, g, x, vl, ll):
  varname = _simple_rect(t, 'Rect', x, g, vl, ll)
  a = "%s.type = '%s'\n" % (varname, t)
  ll.append(a)

def _simple_pad_disc_octagon(g, constructor, x, vl, ll):
  name = str(g.next())
  varname = valid("pad%s" % (name), g, vl)
  a = """\
%s = new %s %s, %s
""" % (varname, constructor, x['r'], x['drill'])
  a = _add_if(x, a, varname, 'drill_dx')
  a = _add_if(x, a, varname, 'name', True)
  a = _add_if(x, a, varname, 'x')
  a = _add_if(x, a, varname, 'y')
  a = _add_if(x, a, varname, 'rot')
  vl.append(varname)
  ll.append(a)

def simple_pad_disc(t, g, x, vl, ll):
  _simple_pad_disc_octagon(g, 'RoundPad', x, vl, ll)

def simple_pad_octagon(t, g, x, vl, ll):
  _simple_pad_disc_octagon(g, 'OctagonPad', x, vl, ll)

def _simple_circle(prefix, g, x):
  varname = "%s%s" % (prefix, g.next())
  a = """\
%s = new Circle %s
%s.x = %s
%s.y = %s
""" % (varname, x['w'], varname, x['x'],
       varname, x['y'])
  a = _add_if(x, a, varname, 'r')
  a = _add_if(x, a, varname, 'rx')
  a = _add_if(x, a, varname, 'ry')
  return (varname, a)

def simple_circle(t, g, x, vl, ll):
  (varname, a) = _simple_circle(t, g, x)
  if t != 'silk':
    a = a + ("%s.type = '%s'\n" % (varname, t))
  vl.append(varname)
  ll.append(a)

def _simple_line(prefix, g, x):
  varname = "%s%s" % (prefix, g.next())
  a = """\
%s = new Line %s
%s.x1 = %s
%s.y1 = %s
%s.x2 = %s
%s.y2 = %s
""" % (varname, x['w'], varname, x['x1'],
       varname, x['y1'], varname, x['x2'],
       varname, x['y2'])
  a = _add_if(x, a, varname, 'curve')
  return (varname, a)

def simple_rect(t, g, x, vl, ll):
  varname = "%s%s" % (t, g.next())
  a = """\
%s = new Rect
""" % (varname)
  a = _add_if(x, a, varname, 'x')
  a = _add_if(x, a, varname, 'y')
  a = _add_if(x, a, varname, 'dx')
  a = _add_if(x, a, varname, 'dy')
  if t != 'silk':
    a = a + ("%s.type = '%s'\n" % (varname, t))
  vl.append(varname)
  ll.append(a)

def simple_line(t, g, x, vl, ll):
  (varname, a) = _simple_line(t, g, x)
  if t != 'silk':
    a = a + ("%s.type = '%s'\n" % (varname, t))
  vl.append(varname)
  ll.append(a)

"""
  p4 = new Polygon 0.1
  p4.start 1,1
  p4.add 1,0
  p4.add 0,1
  p4.end 0
"""
def simple_polygon(t, g, x, vl, ll):
  # TODO a rectangular polygon with w == 0 is actually a rect
  varname = "%s%s" % (t, g.next())
  a = """\
%s = new Polygon %s
""" % (varname, x['w'])
  vert = x['v']
  l = len(vert)
  if l > 0:
    a = a + ("%s.start %s, %s\n" % (varname, vert[0]['x1'], vert[0]['y1']))
    for v in vert[0:l-1]:
      c = ""
      if 'curve' in v:
        if v['curve'] != 0:
          c = ", %s" % (v['curve'])
      a = a + ("%s.add %s, %s%s\n" % (varname, v['x2'], v['y2'], c))
    c = "0.0"
    if 'curve' in vert[-1]:
      if vert[-1]['curve'] != 0:
        c = "%s" % (vert[-1]['curve'])
    a = a + ("%s.end %s\n" % (varname, c))
  if t != 'silk':
    a = a + ("%s.type = '%s'\n" % (varname, t))
  vl.append(varname)
  ll.append(a)

def _simple_name_value(prefix, constructor, g, x, vl, ll):
  y = 0
  if x.has_key('y'):
    y = x['y']
  varname = "%s%s" % (prefix, g.next())
  a = """\
%s = new %s %s
""" % (varname, constructor, y)
  a = _add_if(x, a, varname, 'x')
  return (varname, a)

def _simple_silk_label(g, x, vl, ll):
  varname = "label%s" % (g.next())
  a = """\
%s = new Label '%s'
%s.x = %s
%s.y = %s
%s.dy = %s
""" % (varname, x['value'], varname, x['x'], varname, x['y'],
       varname, x['dy'])
  return (varname, a)

def simple_label(t, g, x, vl, ll):
  v = x['value']
  if not 'x' in x:
   x['x'] = 0.0
  if v == 'NAME':
    (varname, a) = _simple_name_value('name', 'Name', g, x, vl, ll)
  elif v == 'VALUE':
    (varname, a) = _simple_name_value('value', 'Value', g, x, vl, ll)
  else:
    (varname, a) = _simple_silk_label(g, x, vl, ll)
  if t != 'silk':
    a = a + "%s.type = '%s'\n" % (varname, t)
  vl.append(varname)
  ll.append(a)

def simple_special_single(t, g, x, vl, ll):
  direction = x['direction']
  if direction == 'x':
    f = 'rot_single'
  else:
    f = 'single'
  # varname selection here is not perfect; should depend on actual naming
  var = "%s1" % (x['ref'])
  num = x['num']
  e = x['e']
  a = """\
l = %s [%s], %s, %s
""" % (f, var, num, e)
  vl.remove(var)
  vl.append('l')
  ll.append(a)

def simple_special_dual(t, g, x, vl, ll):
  direction_is_x = x['direction'] == 'x'
  alt = x['alt']
  f = 'dual'
  if direction_is_x: f = 'rot_dual'
  if alt: f = 'alt_%s' % (f)
  # varname selection here is not perfect; should depend on actual naming
  var = "%s1" % (x['ref'])
  num = x['num']
  e = x['e']
  between = x['between']
  a = """\
l = %s [%s], %s, %s, %s
""" % (f, var, num, e, between)
  vl.remove(var)
  vl.append('l')
  ll.append(a)

def simple_special_quad(t, g, x, vl, ll):
  # varname selection here is not perfect; should depend on actual naming
  var = "%s1" % (x['ref'])
  num = x['num']
  e = x['e']
  between = x['between']
  a = """\
l = quad [%s], %s, %s, %s
""" % (var, num, e, between)
  vl.remove(var)
  vl.append('l')
  ll.append(a)
    
def simple_special_mod(t, g, x, vl, ll):
  x2 = copy.deepcopy(x)
  i = x2['index']
  del x2['index']
  del x2['type']
  del x2['shape']
  if 'real_shape' in x2:
    x2['shape'] = x2['real_shape']
    del x2['real_shape']
  a = ""
  for (k,v) in x2.items():
    if type(v) == type("") or k == 'name':
      a = a + "l[%s].%s = '%s'\n" % (i, k, v)
    else:
      a = a + "l[%s].%s = %s\n" % (i, k, v)
  ll.append(a)

def simple_unknown(t, g, x, vl, ll):
  varname = "unknown%s" % (g.next())
  a = "%s = new Object\n" % (varname)
  for k in x.keys():
    a = a + "%s.%s = '%s'\n" % (varname, k, x[k])
  vl.append(varname)
  ll.append(a)

# add as needed...

basic_dispatch = {
  'circle': simple_circle,
  'line': simple_line,
  'vertex': simple_line,
  'label': simple_label,
  'rect': simple_rect,
  'polygon': simple_polygon,
}

special_dispatch = {
 'smd_rect': simple_smd_rect,

 'pad_rect': simple_pad_rect,
 'pad_disc': simple_pad_disc,
 'pad_octagon': simple_pad_octagon,

 'special_single': simple_special_single,
 'special_dual': simple_special_dual,
 'special_quad': simple_special_quad,
 'special_mod': simple_special_mod,
}

def generate_coffee(interim):
  generators = {
   'smd': generate_ints(),
   'pad': generate_ints(),
   'silk': generate_ints(),
   'docu': generate_ints(),
   'restrict': generate_ints(),
   'stop': generate_ints(),
   'keepout': generate_ints(),
   'vrestrict': generate_ints(),
   'glue': generate_ints(),
   'unknown': generate_ints(),
   'special': generate_ints(),
   'hole': generate_ints(),
  }
  varnames = []
  lines = []
  meta = None
  for x in interim:
    t = x['type']
    if t == 'meta': meta = new_coffee_meta(x)
    else:
      shape = x['shape']
      key = "%s_%s" % (t, shape)
      g = generators[t]
      if key in special_dispatch:
        special_dispatch.get(key)(t, g, x, varnames, lines)
      else:
        basic_dispatch.get(shape, simple_unknown)(t, g, x, varnames, lines)
  varnames.sort()
  combine = 'combine ['+ (','.join(varnames)) + ']\n'
  lines_joined = ''.join(lines)
  lines_joined = '  ' + lines_joined.replace('\n', '\n  ')
  return meta + "footprint = () ->\n" + lines_joined + combine
    
