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
  def check(x):
    if 'shape' in x and x['shape'] == 'rect':
      if 'x1' in x and 'x2' in x and 'y1' in x and 'y2' in x:
        x['x'] = (x['x1'] + x['x2'])/2
        x['y'] = (x['y1'] + x['y2'])/2
        x['dx'] = abs(x['x1'] - x['x2'])
        x['dy'] = abs(x['y1'] - x['y2'])
    return x
  return map(check, sinter)
