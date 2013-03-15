# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL
#
# functions that operate on the intermediate format

def add_names(inter):
  def generate_ints():
    for i in xrange(1, 10000):
      yield i
  g = generate_ints()
  def _c(x):
    if 'type' in x:
      if x['type'] in ['smd', 'pad']:
        if not 'name' in x:
          x['name'] = str(g.next())
    else:
      x['type'] = 'silk' # default type
    return x
  return [_c(x) for x in inter]

def get_meta(inter):
  for shape in inter:
    if shape['type'] == 'meta':
      return shape
  return None

def prepare_for_display(inter):
  h = {
    'silk': 2,
    'docu': 1,
    'smd': 3,
    'pad': 4,
  }
  def _sort(x1, x2):
    t1 = h.get(x1['type'], 0)
    t2 = h.get(x2['type'], 0)
    return cmp(t1, t2)
  sinter = sorted(inter, _sort)
  def convert(x):
    if 'shape' in x and x['shape'] == 'rect':
      if 'x1' in x and 'x2' in x and 'y1' in x and 'y2' in x:
        x['x'] = (x['x1'] + x['x2'])/2
        x['y'] = (x['y1'] + x['y2'])/2
        x['dx'] = abs(x['x1'] - x['x2'])
        x['dy'] = abs(x['y1'] - x['y2'])
    return x
  return map(convert, sinter)

# this method has a bunch of code duplication of gldraw...
def bounding_box(inter):
  def oget(m, k, d):
    if k in m: return m[k]
    return d
  def fget(m, k, d = 0.0):
    return float(oget(m, k, d))
  def circle(shape):
    r = fget(shape, 'r')
    rx = fget(shape, 'rx', r)
    ry = fget(shape, 'ry', r)
    x = fget(shape,'x')
    y = fget(shape,'y')
    w = fget(shape,'w')
    x1 = x - rx - w/2
    x2 = x + rx + w/2
    y1 = y - ry - w/2
    y2 = y + ry + w/2
    return (x1, y1, x2, y2)

  def disc(shape):
    r = fget(shape, 'r')
    rx = fget(shape, 'rx', r)
    ry = fget(shape, 'ry', r)
    x = fget(shape,'x')
    y = fget(shape,'y')
    x1 = x - rx
    x2 = x + rx
    y1 = y - ry
    y2 = y + ry
    return (x1, y1, x2, y2)
    
  def label(shape):
    x = fget(shape,'x')
    y = fget(shape,'y')
    dy = fget(shape,'dy', 1.2)
    x1 = x
    x2 = x
    y1 = y - dy/2
    y2 = y + dy/2
    return (x1, y1, x2, y2)
    
  def line(shape):
    x1 = fget(shape, 'x1')
    y1 = fget(shape, 'y1')
    x2 = fget(shape, 'x2')
    y2 = fget(shape, 'y2')
    w = fget(shape, 'w')
    x1a = min(x1, x2) - w/2
    x2a = max(x1, x2) + w/2
    y1a = min(y1, y2) - w/2
    y2a = max(y1, y2) + w/2
    return (x1a, y1a, x2a, y2a)

  def octagon(shape):
    r = fget(shape, 'r', 0.0)
    dx = fget(shape, 'dx', r*2)
    dy = fget(shape, 'dy', r*2)
    x = fget(shape,'x')
    y = fget(shape,'y')
    x1 = x - dx/2
    x2 = x + dx/2
    y1 = y - dy/2
    y2 = y + dy/2
    return (x1, y1, x2, y2)

  def rect(shape):
    x = fget(shape, 'x')
    y = fget(shape, 'y')
    dx = fget(shape, 'dx')
    dy = fget(shape, 'dy')
    x1 = x - dx/2
    x2 = x + dx/2
    y1 = y - dy/2
    y2 = y + dy/2
    return (x1, y1, x2, y2)

  x1 = 0
  y1 = 0
  x2 = 0
  y2 = 0
  dispatch = {
    'circle': circle,
    'disc': disc,
    'label': label,
    'line': line,
    'octagon': octagon,
    'rect': rect,
  }
  if inter == None or inter == []: return (-1,-1,1,1)
  for x in inter:
    if 'shape' in x:
       (xx1, xy1, xx2, xy2) = dispatch[x['shape']](x)
       x1 = min(x1, xx1)
       y1 = min(y1, xy1)
       x2 = max(x2, xx2)
       y2 = max(y2, xy2)
  return (x1,y1,x2,y2)

def size(inter):
  if inter == None or inter == []:
    return (1,1)
  (x1,y1,x2,y2) = bounding_box(inter)
  return (abs(x2-x1), abs(y2-y1))
