# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL
#
# functions that operate on the intermediate format

import copy

from util.util import *

def cleanup_js(inter):
  def _remove_constructor(item):
    if 'constructor' in item:
      del item['constructor']
    return item
  return filter(_remove_constructor, inter)

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

def prepare_for_display(inter, filter_out):
  inter = filter(lambda x: x['type'] not in filter_out, inter)
  h = {
    'silk': 4,
    'docu': 3,
    'smd': 2,
    'pad': 1,
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

  def unknown(shape):
    return (0,0,0,0)

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
       (xx1, xy1, xx2, xy2) = dispatch.get(x['shape'], unknown)(x)
       x1 = min(x1, xx1)
       y1 = min(y1, xy1)
       x2 = max(x2, xx2)
       y2 = max(y2, xy2)
  return (x1,y1,x2,y2)

def size(inter):
  if inter == None or inter == []:
    return (1,1)
  (x1,y1,x2,y2) = bounding_box(inter)
  dx = 2*max(abs(x2),abs(x1)) 
  dy = 2*max(abs(y2),abs(y1))
  return (dx, dy, x1, y1, x2, y2)

def sort_by_type(inter):
  h = {
    'silk': 1,
    'docu': 2,
    'smd': 3,
    'pad': 4,
    'restrict': 5,
    'stop': 6,
  }
  def _sort(x1, x2):
    t1 = h.get(x1['type'], 0)
    t2 = h.get(x2['type'], 0)
    return cmp(t1, t2)
  return sorted(inter, _sort)

def _count_num_values(pads, param):
  res = {}
  for pad in pads:
    v = pad[param]
    if not v in res:
      res[v] = 1
    else:
      res[v] = res[v] + 1
  i = len(res.keys())
  return (i, res)

def _equidistant(pads, direction):
  expected = abs(pads[1][direction] - pads[0][direction])
  prev = pads[1][direction]
  for item in pads[2:]:
    cur = item[direction]
    if f_neq(abs(cur - prev), expected):
      return False
    prev = cur
  return True

def _all_equal(pads, direction):
  first = pads[0][direction]
  return reduce(lambda a, p: a and f_eq(p[direction], first), pads, True)

def _sort_by_field(pads, field, reverse=False):
  def _sort_by(a, b):
    return cmp(a[field], b[field])
  return sorted(pads, cmp=_sort_by, reverse=reverse)

def _clone_pad(pad_in, remove):
  pad = copy.deepcopy(pad_in)
  for x in remove:
    if x in pad: del pad[x]
  if 'name' in pad: del pad['name']
  return pad

def _make_mods(skip, pad, pads):
  l = []
  for (item, i) in zip(pads, range(len(pads))):
    mod = {}
    #print "investigating", i, item
    for (k,v) in item.items():
      if k in skip: continue
      if k == 'name' and str(i+1) == v: continue
      #print 'testing', k, v
      if k not in pad:
        mod[k] = v
      elif pad[k] != v:
        mod[k] = v
    if mod != {}:
      mod['type'] = 'special'
      if 'shape' in mod:
        mod['real_shape'] = mod['shape']
      mod['shape'] = 'mod'
      mod['index'] = i
      #print "adding mod", mod
      l.append(mod)
  return l

def _check_single(orig_pads, horizontal):
  if horizontal:
    equal_direction = 'y'
    diff_direction = 'x'
    reverse = False
  else:
    equal_direction = 'x'
    diff_direction = 'y'
    reverse = True
  # sort pads by decreasing in other direction
  pads = _sort_by_field(orig_pads, diff_direction, reverse)
  # check if the distance is uniform
  if not _equidistant(pads, diff_direction):
    #print "not equidistant", diff_direction
    return orig_pads
  # check if all x coordinates are equal
  if not _all_equal(pads, equal_direction):
    #print "not all equal", equal_direction
    return orig_pads
  # create a pad based on the second pad
  # the first one might be special...
  pad = _clone_pad(pads[1], [diff_direction])
  pad_type = pad['type']
  # create a special pseudo entry
  special = {}
  special['type'] = 'special'
  special['shape'] = 'single'
  special['direction'] = diff_direction
  special['ref'] = pad_type
  special['num'] = len(pads)
  special['e'] = abs(pads[0][diff_direction] - pads[1][diff_direction])
  l = [pad, special]
  # check if there are mods needed
  mods = _make_mods([diff_direction], pad, pads)
  return l + mods

def _split_dual(pads, direction):
  r1 = []
  r2 = []
  for pad in pads:
    # we assume the dual rows are centered around (0,0)
    if pad[direction] < 0:
      r1.append(pad)
    else:
      r2.append(pad)
  return (r1, r2)

def _one_by_one_equal(r1, r2, direction):
  for (p1, p2) in zip(r1, r2):  
    if f_neq(p1[direction], p2[direction]):
      return False
  return True

def _check_dual_alt(r1, r2):
  i = 1
  for (p1, p2) in zip(r1, r2):
    n1 = int(p1['name'])
    n2 = int(p2['name'])
    print i, n1, n2
    if not (n1 == i and n2 == i+1):
      return False
    i = i + 2
  return True

def _check_dual(orig_pads, horizontal):
  if horizontal:
    split_direction = 'y'
    diff_direction = 'x'
    print 'dual horizontal?'
  else:
    split_direction = 'x'
    diff_direction = 'y'
    print 'dual vertical?'
  # split in two rows
  (r1, r2) = _split_dual(orig_pads, split_direction)
  # sort pads in 2 rows
  r1 = _sort_by_field(r1, diff_direction)
  r2 = _sort_by_field(r2, diff_direction)
  # check if the distance is uniform
  if not _equidistant(r1, diff_direction):
    print "r1 not equidistant", diff_direction
    return orig_pads
  if not _equidistant(r2, diff_direction):
    print "r2 not equidistant", diff_direction
    return orig_pads
  # check if all coordinates are equal in split_direction
  if not _all_equal(r1, split_direction):
    print "r1 not all equal", split_direction
    return orig_pads
  if not _all_equal(r2, split_direction):
    print "r2 not all equal", split_direction
    return orig_pads
  # check that the two rows are one by one equal
  if not _one_by_one_equal(r1, r2, diff_direction):
    print "r1,r2 not one by one equal", diff_direction
    return orig_pads
  # normal: 1 6 alt: 1 2
  #         2 5      3 4
  #         3 4      5 6
  # check if the pad order is normal or alt
  # if it is not pure alt we assume normal and if needed
  # set other names via mods
  is_alt = _check_dual_alt(r1, r2)
  between = abs(r1[0][split_direction] - r2[0][split_direction])
  # create a pad based on the second pad
  # the first one might be special...
  pad = _clone_pad(r1[1], ['x','y'])
  pad_type = pad['type']
  # create a special pseudo entry
  special = {}
  special['type'] = 'special'
  special['shape'] = 'dual'
  special['alt'] = is_alt
  special['direction'] = diff_direction
  special['ref'] = pad_type
  special['num'] = len(orig_pads)
  special['between'] = between
  special['e'] = abs(r1[0][diff_direction] - r1[1][diff_direction])
  if not is_alt:
    if diff_direction == 'y':
      sort_pads = r1 + r2
    else:
      r2.reverse()
    sort_pads = r1 + r2
  else:
    sort_pads = list_combine(map(lambda (a,b): [a,b], zip(r1, r2)))
  mods = _make_mods(['x','y'], pad, sort_pads)
  rot = 0
  if 'rot' in pad: rot = pad['rot']
  if diff_direction == 'x': 
    rot = rot - 90 # will be rotated again while drawing
  if rot < 0 : rot = rot + 360
  pad['rot'] = rot
  if rot == 0:
    del pad['rot']
  return [pad, special] + mods

def _split_quad(pads):
  minx = reduce(lambda a,x: min(a, x['x']) , pads, 0)
  maxx = reduce(lambda a,x: max(a, x['x']) , pads, 0)
  miny = reduce(lambda a,x: min(a, x['y']) , pads, 0)
  maxy = reduce(lambda a,x: max(a, x['y']) , pads, 0)
  h = {
    'minx': [],
    'maxx': [],
    'miny': [],
    'maxy': []
  }
  for pad in pads:
    if pad['x'] == minx: h['minx'].append(pad)
    if pad['x'] == maxx: h['maxx'].append(pad)
    if pad['y'] == miny: h['miny'].append(pad)
    if pad['y'] == maxy: h['maxy'].append(pad)
  h['minx'] = sorted(h['minx'], lambda a,b: cmp(a['y'], b['y']), reverse=True)
  h['maxx'] = sorted(h['maxx'], lambda a,b: cmp(a['y'], b['y']))
  h['miny'] = sorted(h['miny'], lambda a,b: cmp(a['x'], b['x']))
  h['maxy'] = sorted(h['maxy'], lambda a,b: cmp(a['x'], b['x']), reverse=True)
  return (h['minx'], h['miny'], h['maxx'], h['maxy']) 


def _check_quad(orig_pads):
  n = len(orig_pads)
  if not (n % 4 == 0):
    print 'quad: n not dividable by 4'
    return orig_pads
  (left_x, down_y, right_x, up_y) = _split_quad(orig_pads)
  if len(left_x) != n/4 or len(down_y) != n/4 or len(right_x) != n/4 or len(up_y) != n/4:
    print 'quad: some row is not n/4 length'
    return origpads
  dx = right_x[0]['x'] - left_x[0]['x']
  dy = up_y[0]['y'] - down_y[0]['y']
  if f_neq(dx, dy):
    print 'quad: distance not equal between x and y rows', dx, dy
    return orig_pads
  between = dx   
  if not _equidistant(left_x, 'y'):
    print 'quad: left row not equidistant'
    return orig_pads
  if not _equidistant(right_x, 'y'):
    print 'quad: right row not equidistant'
    return orig_pads
  if not _equidistant(up_y, 'x'):
    print 'quad: up row not equidistant'
    return orig_pads
  if not _equidistant(down_y, 'x'):
    print 'quad: down row not equidistant'
    return orig_pads
  # we have a quad!
  # create a pad based on the second pad
  # the first one might be special...
  pad = _clone_pad(left_x[1], ['x','y'])
  pad_type = pad['type']
  # create a special pseudo entry
  special = {}
  special['type'] = 'special'
  special['shape'] = 'quad'
  special['ref'] = pad_type
  special['num'] = len(orig_pads)
  special['between'] = between
  special['e'] = abs(left_x[0]['y'] - left_x[1]['y'])
  sort_pads = left_x + down_y + right_x + up_y
  mods = _make_mods(['x','y', 'rot'], pad, sort_pads)
  return [pad, special] + mods

def _find_pad_patterns(pads):
  n = len(pads)
  print n
  (x_diff, _z) = _count_num_values(pads, 'x')
  print 'x diff ', x_diff
  (y_diff, _z) = _count_num_values(pads, 'y')
  print 'y diff ', y_diff

  # possibly single row
  if x_diff == 1 and y_diff == n:
    return _check_single(pads, horizontal=False)
  if x_diff == n and y_diff == 1:
    return _check_single(pads, horizontal=True)

  # possibly dual row
  if x_diff == 2 and y_diff == n/2:
    return _check_dual(pads, horizontal=False)
  if x_diff == n/2 and y_diff == 2:
    return _check_dual(pads, horizontal=True)

  # possibly a quad
  if x_diff == (n/4)+2 and y_diff == (n/4)+2:
    return _check_quad(pads)
  return pads

def find_pad_patterns(inter):
  pads = filter(lambda x: x['type'] == 'pad', inter)
  no_pads = filter(lambda x: x['type'] != 'pad', inter)
  if len(pads) > 0:
    pads = _find_pad_patterns(pads)
    inter = pads + no_pads

  smds = filter(lambda x: x['type'] == 'smd', inter)
  no_smds = filter(lambda x: x['type'] != 'smd', inter)
  if len(smds) > 0:
    smds = _find_pad_patterns(smds)
    inter = smds + no_smds
  return inter
