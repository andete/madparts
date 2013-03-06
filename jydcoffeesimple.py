# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import string

from jydutil import *

def valid(varname, g):
  def make_valid(c):
    if not c in (string.ascii_letters + string.digits):
      return "_%s_" % (g.next())
    else:
      return c
  return ''.join([make_valid(x) for x in varname])

def new_coffee_meta(meta):
  a = """
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
    if not quote:
      a = a + "%s.%s = %s\n" % (varname, key, x[key])
    else:
      a = a + "%s.%s = '%s'\n" % (varname, key, x[key])
  return a

def _simple_rect(prefix, constructor, x, g):
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
  a = _add_if(x, a, varname, 'x1')
  a = _add_if(x, a, varname, 'y1')
  a = _add_if(x, a, varname, 'x2')
  a = _add_if(x, a, varname, 'y2')
  return (varname, a)

def simple_smd_rect(g, x):
  return _simple_rect('smd', 'Smd', x, g)

def simple_pad_rect(g, x):
  (varname, a) = _simple_rect('rpad', 'Pad', x, g)
  a = a + "%s.shape = 'rect'\n" % (varname)
  a = a + "%s.drill = %s\n" % (varname, x['drill'])
  a = _add_if(x, a, varname, 'drill_dx')
  return (varname, a)

def simple_docu_rect(g, x):
  (varname, a) = _simple_rect('rect', 'Rect', x, g)
  a = a + ("%s.type = 'docu'\n" % (varname))
  return (varname, a)

def _simple_pad_circle_octagon(prefix, x):
  varname = valid("%s%s" % (prefix, x['name']), g)
  a = """\
%s = new Pad
%s.name = '%s'
%s.shape = '%s'
%s.x = %s
%s.y = %s
%s.r = %s
%s.drill = %s
""" % (varname, varname, x['name'],
       varname, x['shape'], varname, x['x'],
       varname, x['y'], varname, x['r'], varname, x['drill'])
  a = _add_if(x, a, varname, 'drill_dx')
  return (varname, a)

def simple_pad_circle(g, x):
  return _simple_pad_circle_octagon('cpad', x)

def simple_pad_octagon(g, x):
  return _simple_pad_circle_octagon('opad', x)

def simple_silk_circle(g, x):
  varname = "silk%s" % (g.next())
  a = """\
%s = new Circle %s
%s.x = %s
%s.y = %s
%s.r = %s
""" % (varname, x['w'], varname, x['x'],
       varname, x['y'], varname, x['r'])
  return (varname, a)

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

def simple_silk_line(g, x):
  return _simple_line('silk', g, x)

def simple_docu_line(g, x):
  (varname, a) = _simple_line('docu', g, x)
  a = a + ("%s.type = 'docu'\n" % (varname))
  return (varname, a)

def _simple_name_value(prefix, constructor, g, x):
  varname = "%s%s" % (prefix, g.next())
  a = """\
%s = new %s %s
%s.x = %s
""" % (varname, constructor, x['y'], varname, x['x'])
  return (varname, a)

def _simple_silk_label(g, x):
  varname = "label%s" % (g.next())
  a = """\
%s = new Label '%s'
%s.x = %s
%s.y = %s
%s.dy = %s
""" % (varname, x['value'], varname, x['x'], varname, x['y'],
       varname, x['dy'])
  return (varname, a)

def simple_silk_label(g, x):
  v = x['value']
  if not 'x' in x:
   x['x'] = 0.0
  if v == 'NAME':
    return _simple_name_value('name', 'Name', g, x)
  elif v == 'VALUE':
    return _simple_name_value('value', 'Value', g, x)
  else:
    return _simple_silk_label(g, x)
    


def simple_unknown(g, x):
  varname = "unknown%s" % (g.next())
  a = "%s = new Object\n" % (varname)
  for k in x.keys():
    a = a + "%s.%s = '%s'\n" % (varname, k, x[k])
  return (varname, a)

# add as needed...
simple_dispatch = {
 'smd_rect': simple_smd_rect,
 'pad_rect': simple_pad_rect,
 'pad_circle': simple_pad_circle,
 'pad_octagon': simple_pad_octagon,
 'silk_circle': simple_silk_circle,
 'silk_line': simple_silk_line,
 'silk_label': simple_silk_label,
 'docu_line': simple_docu_line,
 'docu_rect': simple_docu_rect,
}

def generate_coffee(inter):
  g = generate_ints()
  l = []
  meta = None
  for x in inter:
    t = x['type']
    if t == 'meta': meta = new_coffee_meta(x)
    else:
      shape = x['shape']
      key = "%s_%s" % (t, shape)
      result = simple_dispatch.get(key, simple_unknown)(g, x)
      l.append(result)
  l = sorted(l, lambda (n1,s1),(n2,s2): cmp(n1,n2))
  lines = map(lambda (n,s): s, l)
  varnames = map(lambda (n,s): n, l)
  combine = '['+ (','.join(varnames)) + ']\n'
  lines_joined = ''.join(lines)
  lines_joined = '  ' + lines_joined.replace('\n', '\n  ')
  return meta + "footprint = () ->\n" + lines_joined + combine
    
