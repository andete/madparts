# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

# TODO: rework approach

import string, copy
from functools import partial

from util.util import *

def valid(varname, g):
  def make_valid(c):
    if not c in (string.ascii_letters + string.digits):
      return "_%s_" % (g.next())
    else:
      return c
  return ''.join([make_valid(x) for x in varname])

def new_coffee_meta(meta):
  a = """\
#format 1.0
#name %s
#id %s
""" % (meta['name'], meta['id'])
  if meta['desc'] == None: return a
  for line in meta['desc'].splitlines():
    a = a + ("#desc %s\n" % (line))
  return a

def _add_if(x, a, varname, key, quote = False):
  if key in x:
    if type(x[key]) == type(1.1):
      if f_eq(x[key], 0.0):
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
  varname = valid("%s%s" % (prefix, name), g)
  a = """\
%s = new %s
""" % (varname, constructor)
  a = _add_if(x, a, varname, 'name', True)
  a = _add_if(x, a, varname, 'rot')
  a = _add_if(x, a, varname, 'ro')
  a = _add_if(x, a, varname, 'x')
  a = _add_if(x, a, varname, 'y')
  a = _add_if(x, a, varname, 'dx')
  a = _add_if(x, a, varname, 'dy')
  vl.append(varname)
  ll.append(a)
  return varname

def simple_smd_rect(g, x, vl, ll):
  _simple_rect('smd', 'Smd', x, g, vl, ll)

def simple_pad_rect(g, x, vl, ll):
  name = str(g.next())
  varname = valid("pad%s" % (name), g)
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
""" % (varname, dx, drill)
    else:
      a = """\
%s = new LongPad %s, %s
""" % (varname, dy, drill)
  else:
    a = """\
%s = new Pad
"""
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
  varname = valid("pad%s" % (name), g)
  a = """\
%s = new %s %s, %s
""" % (varname, constructor, x['r'], x['drill'])
  a = _add_if(x, a, varname, 'drill_dx')
  a = _add_if(x, a, varname, 'name')
  a = _add_if(x, a, varname, 'x')
  a = _add_if(x, a, varname, 'y')
  vl.append(varname)
  ll.append(a)

def simple_pad_disc(g, x, vl, ll):
  _simple_pad_disc_octagon(g, 'RoundPad', x, vl, ll)

def simple_pad_octagon(g, x):
  _simple_pad_disc_octagon(g, 'OctagonPad', x, vl, ll)

def _simple_circle(prefix, g, x):
  varname = "%s%s" % (prefix, g.next())
  a = """\
%s = new Circle %s
%s.x = %s
%s.y = %s
%s.r = %s
""" % (varname, x['w'], varname, x['x'],
       varname, x['y'], varname, x['r'])
  return (varname, a)

def simple_silk_circle(g, x, vl, ll):
  (varname, a) = _simple_circle('silk', g, x)
  vl.append(varname)
  ll.append(a)

def _simple_t_circle(t, g, x, vl, ll):
  (varname, a) = _simple_circle(t, g, x)
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
  return (varname, a)

def simple_silk_line(g, x, vl, ll):
  (varname, a) = _simple_line('silk', g, x)
  vl.append(varname)
  ll.append(a)

def simple_silk_rect(g, x, vl, ll):
  varname = "silk%s" % (g.next())
  a = """\
%s = new Rect
""" % (varname)
  a = _add_if(x, a, varname, 'x')
  a = _add_if(x, a, varname, 'y')
  a = _add_if(x, a, varname, 'dx')
  a = _add_if(x, a, varname, 'dy')
  vl.append(varname)
  ll.append(a)

def _simple_t_line(t, g, x):
  (varname, a) = _simple_line(t, g, x)
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
  vl.append(varname)
  ll.append(a)

def _simple_silk_label(g, x, vl, ll):
  varname = "label%s" % (g.next())
  a = """\
%s = new Label '%s'
%s.x = %s
%s.y = %s
%s.dy = %s
""" % (varname, x['value'], varname, x['x'], varname, x['y'],
       varname, x['dy'])
  vl.append(varname)
  ll.append(a)

def simple_silk_label(g, x, vl, ll):
  v = x['value']
  if not 'x' in x:
   x['x'] = 0.0
  if v == 'NAME':
    _simple_name_value('name', 'Name', g, x, vl, ll)
  elif v == 'VALUE':
    _simple_name_value('value', 'Value', g, x, vl, ll)
  else:
    _simple_silk_label(g, x, vl, ll)

def simple_special_single(g, x, vl, ll):
  direction = x['direction']
  if direction == 'x':
    f = 'alt_single'
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

def simple_special_dual(g, x, vl, ll):
  direction_is_x = x['direction'] == 'x'
  alt = x['alt'] == 'True'
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
    
def simple_special_mod(g, x, vl, ll):
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
    if type(v) == type(""):
      a = a + "l[%s].%s = '%s'\n" % (i, k, v)
    else:
      a = a + "l[%s].%s = %s\n" % (i, k, v)
  ll.append(a)

def simple_unknown(g, x, vl, ll):
  varname = "unknown%s" % (g.next())
  a = "%s = new Object\n" % (varname)
  for k in x.keys():
    a = a + "%s.%s = '%s'\n" % (varname, k, x[k])
  vl.append(varname)
  ll.append(a)

# add as needed...
simple_dispatch = {
 'smd_rect': simple_smd_rect,
 'pad_rect': simple_pad_rect,
 'pad_disc': simple_pad_disc,
 'pad_octagon': simple_pad_octagon,
 'silk_circle': simple_silk_circle,
 'silk_line': simple_silk_line,
 'silk_label': simple_silk_label,
 'silk_rect': simple_silk_rect,
 'docu_circle': partial(_simple_t_circle, 'docu'),
 'docu_line': partial(_simple_t_line, 'docu'),
 'docu_rect': partial(_simple_t_rect, 'docu'),
 'restrict_circle': partial(_simple_t_circle, 'restrict'),
 'restrict_line': partial(_simple_t_line, 'restrict'),
 'restrict_rect': partial(_simple_t_rect, 'restrict'),
 'stop_circle': partial(_simple_t_circle, 'stop'),
 'stop_line': partial(_simple_t_line, 'stop'),
 'stop_rect': partial(_simple_t_rect, 'stop'),
 'special_single': simple_special_single,
 'special_dual': simple_special_dual,
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
   'unknown': generate_ints(),
   'special': generate_ints(),
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
      simple_dispatch.get(key, simple_unknown)(g, x, varnames, lines)
  varnames.sort()
  combine = 'combine ['+ (','.join(varnames)) + ']\n'
  lines_joined = ''.join(lines)
  lines_joined = '  ' + lines_joined.replace('\n', '\n  ')
  return meta + "footprint = () ->\n" + lines_joined + combine
    
