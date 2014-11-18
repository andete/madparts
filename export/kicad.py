# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import glob, math, os.path, uuid

import sexpdata
from sexpdata import Symbol

from mutil.mutil import *
from inter import inter

def S(v):
  return Symbol(str(v))

def type_to_layer_name(layer):
  return {
    'smd': 'F.Cu', # these two are normally
    'pad': 'F.Cu', # not used like this
    'cu': 'F.Cu',  # generic non-pad/smd Cu
    'silk': 'F.SilkS',
    'name': 'F.SilkS',
    'value': 'Dwgs.User',
    'stop': 'F.Mask',
    'glue': 'F.Adhes',
    'docu': 'Dwgs.User',
    'hole': 'Edge.Cuts',
    }.get(layer)

def layer_name_to_type(name):
   return {
    'F.SilkS': 'silk',
    'Dwgs.User': 'docu',
    'F.Mask': 'stop',
    'F.Adhes': 'glue',
    'Edge.Cuts': 'hole',
   }.get(name)


def detect(fn):
  if os.path.isdir(fn) and '.pretty' in fn:
    return "3"
  try:
    l = sexpdata.load(open(fn, 'r'))
    if (l[0] == S('module')): return "3"
    return None
  except IOError:
    # allow new .kicad_mod files!
    if '.kicad_mod' in fn: return "3"
    return None
  except:
    return None

def _convert_sexp_symbol(d):
  if ("value" in dir(d)):
    return d.value()
  else:
    return d

def _convert_sexp_symbol_to_string(d):
  return str(_convert_sexp_symbol(d))

class Export:

  def __init__(self, fn):
    self.fn = fn

  def export_footprint(self, interim):
    meta = inter.get_meta(interim)
    name = eget(meta, 'name', 'Name not found')
    idx = eget(meta, 'id', 'Id not found')
    descr = oget(meta, 'desc', '')
    parent_idx = oget(meta, 'parent', None)
    l = [
      S('module'),
      name,
      [S('layer'), S('F.Cu')],
      [S('descr'), descr],
    ]
    
    
    def pad_line(x1,y1,x2,y2,width,layer):
      l = [S('fp_line')] 
      l.append([S('start'), x1,y1])
      l.append([S('end'), x2,y2])
      l.append([S('layer'), S(layer)])
      l.append([S('width'), width])
      return l

    def pad_lines(s,x1,y1,x2,y2,width):
      s.append(pad_line(x1,y1,x2,y2,width,'F.Cu'))
      s.append(pad_line(x1,y1,x2,y2,width,'F.Paste'))
      s.append(pad_line(x1,y1,x2,y2,width,'F.Mask'))

    def gen_lines(l,x,y,rot,radius,dx,dy):
      #4 corners
      xo = dx/2 - radius;
      yo = dy/2 - radius;

      rot = math.radians(rot)

      xp = math.cos(rot)*xo - math.sin(rot)*yo;
      yp = math.cos(rot)*yo +  math.sin(rot)*xo;
            
      x1 = x - xp;
      x2 = x + xp;
      y1 = y - yp;
      y2 = y + yp;

      pad_lines(l,x1,y1,x2,y1,radius*2)
      pad_lines(l,x2,y1,x2,y2,radius*2)
      pad_lines(l,x2,y2,x1,y2,radius*2)
      pad_lines(l,x1,y2,x1,y1,radius*2)


    def pad(shape, smd=False):
      l = [S('pad'), S(shape['name'])]
      shapes = [l]
      if smd:
        l.append(S('smd'))
      else:
        l.append(S('thru_hole'))
      shape2 = 'disc' # disc is the default
      if 'shape' in shape:
        shape2 = shape['shape']
      r = fget(shape, 'r')
      if shape2 == 'disc':
        l.append(S('circle'))
        l.append([S('size'), r*2, r*2])
      elif shape2 == 'rect':
        ro = iget(shape, 'ro')
        dx = fget(shape, 'dx')
        dy = fget(shape, 'dy')
        if ro == 100:
          l.append(S('oval'))
          l.append([S('size'), dx, dy])
        else:
          l.append(S('rect'))
          if ro == 0:    
            l.append([S('size'), dx, dy])
	  else:
	    #find the smallest dimension and create a rectangular pad squished by that amount
	    #TODO: the rectangular pad is simple with 4 lines, 1 rect and guaranteed no holes		
	    #however it can create arbitrarily small pad which will make text in kicad hard to 
	    #read. may be better to use a oval pad, which can be not shrunk and is still guaranteed 
	    #to not overrun the pad, however it is tricky to make sure the 4 lines don't create any holes. 
	    small = dx
	    if dy < dx :
               small = dy
            radius = small/2 * ro / 100.0;
            l.append([S('size'), dx-radius*2, dy-radius*2])
            gen_lines(shapes, fget(shape, 'x'), -fget(shape, 'y'), iget(shape, 'rot'), radius, dx, dy)
      else:
        raise Exception("%s shaped pad not supported in kicad" % (shape2))
      l.append([S('at'), fget(shape, 'x'), -fget(shape, 'y'), iget(shape, 'rot')])
      if smd:
        l.append([S('layers'), S('F.Cu'), S('F.Paste'), S('F.Mask')])
      else:
        l.append([S('layers'), S('*.Cu'), S('*.Mask')])
      if not smd:
        l2 = [S('drill'), fget(shape, 'drill')]
        if 'drill_dx' in shape or 'drill_dy' in shape:
          l2.append([S('offset'), fget(shape, 'drill_dx'), fget(shape, 'drill_dy')])
        l.append(l2)
      return shapes
    
    #(fp_line (start -2.54 -1.27) (end 2.54 -1.27) (layer F.SilkS) (width 0.381))
    # (fp_arc (start 7.62 0) (end 7.62 -2.54) (angle 90) (layer F.SilkS) (width 0.15))
    def vertex(shape, layer):
      if not 'curve' in shape or shape['curve'] == 0.0:
        l = [S('fp_line')] 
        l.append([S('start'), fget(shape, 'x1'), -fget(shape, 'y1')])
        l.append([S('end'), fget(shape, 'x2'), -fget(shape, 'y2')])
        l.append([S('layer'), S(layer)])
        l.append([S('width'), fget(shape, 'w')])
      else:
        l = [S('fp_arc')] 
        # start == center point
        # end == start point of arc
        # angle == angled part in that direction
        x1 = fget(shape, 'x1')
        y1 = fget(shape, 'y1')
        x2 = fget(shape, 'x2')
        y2 = fget(shape, 'y2')
        curve =  fget(shape, 'curve')
        angle = curve*math.pi/180.0
        ((x0, y0), r, a1, a2) = calc_center_r_a1_a2((x1,y1),(x2,y2),angle)
        l.append([S('start'), fc(x0), fc(-y0)])
        l.append([S('end'), fc(x1), fc(-y1)])
        # also invert angle because of y inversion
        l.append([S('angle'), -(a2-a1)])
        l.append([S('layer'), S(layer)])
        l.append([S('width'), fget(shape, 'w')])
      return [l]

    # (fp_circle (center 5.08 0) (end 6.35 -1.27) (layer F.SilkS) (width 0.15))
    def circle(shape, layer):
      x = fget(shape, 'x')
      y = -fget(shape, 'y')
      r = fget(shape, 'r')
      if not 'a1' in shape and not 'a2' in shape:
        l = [S('fp_circle')] 
        l.append([S('center'),fc(x),fc(y)])
        l.append([S('end'), fc(x+(r/math.sqrt(2))), fc(y+(r/math.sqrt(2)))])
        l.append([S('layer'), S(layer)])
        l.append([S('width'), fget(shape, 'w')])
      else:
        l = [S('fp_arc')] 
        l.append([S('start'),fc(x),fc(y)])
        # start == center point
        # end == start point of arc
        # angle == angled part in that direction
        a1 = fget(shape, 'a1')
        a2 = fget(shape, 'a2')
        a1rad = a1 * math.pi/180.0
        ex = x + r*math.cos(a1rad)
        ey = y + r*math.sin(a1rad)
        l.append([S('end'), fc(ex), fc(-ey)])
        l.append([S('angle'), -(a2-a1)])
      l.append([S('layer'), S(layer)])
      l.append([S('width'), fget(shape, 'w')])
      return [l]

    # a disc is just a circle with a clever radius and width
    def disc(shape, layer):
      l = [S('fp_circle')] 
      x = fget(shape, 'x')
      y = -fget(shape, 'y')
      l.append([S('center'), fc(x), fc(y)])
      r = fget(shape, 'r')
      rad = r/2
      l.append([S('end'), x+(rad/math.sqrt(2)), y+(rad/math.sqrt(2))])
      l.append([S('layer'), S(layer)])
      l.append([S('width'), rad])
      return [l]

    def hole(shape):
      layer = type_to_layer_name(shape['type']) # aka 'hole'
      shape['r'] = shape['drill'] / 2
      return circle(shape, layer)

    # (fp_poly (pts (xy 6.7818 1.6002) (xy 6.6294 1.6002) (xy 6.6294 1.4478) (xy 6.7818 1.4478) (xy 6.7818 1.6002)) (layer F.Cu) (width 0.00254))
    # kicad doesn't do arced vertex in polygon :(
    def polygon(shape, layer):
      l = [S('fp_poly')]
      lxy = [S('pts')]
      for v in shape['v']:
        xy = [S('xy'), fc(v['x1']), fc(-v['y1'])]
        lxy.append(xy)
      xy = [S('xy'), fc(shape['v'][0]['x1']), fc(-shape['v'][0]['y1'])]
      lxy.append(xy)
      l.append(lxy)
      l.append([S('layer'), S(layer)])
      l.append([S('width'), shape['w']])
      return [l]

    def rect(shape, layer):
      l = [S('fp_poly')]
      x = fget(shape, 'x')
      y = - fget(shape, 'y')
      dx = fget(shape, 'dx')
      dy = fget(shape, 'dy')
      lxy = [S('pts')]
      def add(x1, y1):
        lxy.append([S('xy'), fc(x1), fc(y1)])
      add(x - dx/2, y - dy/2)
      add(x - dx/2, y + dy/2)
      add(x + dx/2, y + dy/2)
      add(x + dx/2, y - dy/2)
      add(x - dx/2, y - dy/2)
      l.append(lxy)
      l.append([S('layer'), S(layer)])
      l.append([S('width'), 0])
      return [l]

    # (fp_text reference MYCONN3 (at 0 -2.54) (layer F.SilkS)
    #   (effects (font (size 1.00076 1.00076) (thickness 0.25146)))
    # )
    # (fp_text value SMD (at 0 2.54) (layer F.SilkS) hide
    #   (effects (font (size 1.00076 1.00076) (thickness 0.25146)))
    # )
    def label(shape, layer):
      s = shape['value'].upper()
      t = 'user'
      if s == 'VALUE': t = 'value'
      if s == 'NAME': t = 'reference'
      l = [S('fp_text'), S(t), S(shape['value'])]
      if (('rot' in shape) and (fget(shape, 'rot') != 0.0)):
        l.append([S('at'), fget(shape, 'x'), fc(-fget(shape, 'y')), fget(shape, 'rot')])
      else:
        l.append([S('at'), fget(shape, 'x'), fc(-fget(shape, 'y'))])
      l.append([S('layer'), S(layer)])
      if s == 'VALUE':
        l.append(S('hide'))
      dy = fget(shape, 'dy', 1/1.6)
      th = fget(shape, 'w', 0.1)
      l.append([S('effects'), 
                [S('font'), [S('size'), dy, dy], [S('thickness'), th]]])
      return [l]

    def silk(shape):
      if not 'shape' in shape: return None
      layer = type_to_layer_name(shape['type'])
      s = shape['shape']
      if s == 'line': return vertex(shape, layer)
      if s == 'vertex': return vertex(shape, layer)
      elif s == 'circle': return circle(shape, layer)
      elif s == 'disc': return disc(shape, layer)
      elif s == 'label': return label(shape, layer)
      elif s == 'rect': return rect(shape, layer)
      elif s == 'polygon': return polygon(shape, layer)

    def unknown(shape):
      return None

    for shape in interim:
      if 'type' in shape:
        l2 = {
          'pad': pad,
          'cu': silk,
          'silk': silk,
          'docu': silk,
          'keepout': unknown,
          'stop': silk,
          'glue': silk,
          'restrict': unknown,
          'vrestrict': unknown,
          'smd': lambda s: pad(s, smd=True),
          'hole': hole,
          }.get(shape['type'], unknown)(shape)
        if l2 != None:
         l.extend(l2)
    self.data = l
    self.name = name
    return name

  def save(self):
    if os.path.isdir(self.fn) and '.pretty' in self.fn:
      name = self.name.replace(' ', '_')
      fn = os.path.join(self.fn, name + '.kicad_mod')
    else:
      fn = self.fn
    with open(fn, 'w+') as f:
      sexpdata.dump(self.data, f)

  def get_string(self):
    return sexpdata.dumps(self.data)

class Import:

  def __init__(self, fn):
    self.fn = fn
    if os.path.isdir(self.fn) and '.pretty' in self.fn:
      self.files = glob.glob(self.fn + '/*.kicad_mod')
    else:
      self.files = [self.fn]

  def list_names(self):
    l = []
    for f in self.files:
      s = sexpdata.load(open(f, 'r'))
      name = _convert_sexp_symbol_to_string(s[1])
      fp = self._import_footprint(s)
      desc = None
      for x in fp:
         if x['type'] == 'meta':
           if 'desc' in x:
             desc = x['desc']
             break
      l.append((name, desc))
    return l

  def list(self):
    for f in self.files:
      l = sexpdata.load(open(f, 'r'))
      print _convert_sexp_symbol_to_string(l[1])

  def import_footprint(self, name):
    s = None
    for f in self.files:
      s = sexpdata.load(open(f, 'r'))
      if _convert_sexp_symbol_to_string(s[1]) == name:
        break
    if s is None:
      raise Exception("Footprint %s not found" % (name))
    return self._import_footprint(s)

  def _import_footprint(self, s):
    meta = {}
    meta['type'] = 'meta'
    meta['name'] = _convert_sexp_symbol_to_string(s[1])
    meta['id'] = uuid.uuid4().hex
    meta['desc'] = None
    l = [meta]

    def get_sub(x, name):
      #print "X: "
      #print x
      for e in x:
        if ("__len__" not in dir(e)):
          continue # Ignore objects without length
        if (len(e) == 0):
          continue # Ignore empty
        if _convert_sexp_symbol_to_string(e[0]) == name:
          return list(map(_convert_sexp_symbol, e[1:]))
      return None

    def has_sub(x, name):
      for e in x:
        if ("__len__" not in dir(e)):
          continue # Ignore objects without length
        if (len(e) == 0):
          continue # Ignore empty
        if _convert_sexp_symbol_to_string(e[0]) == name:
          return True
      return False
      
    def get_single_element_sub(x, name, default=None):
      sub = get_sub(x, name)
      if (sub != None):
        if (len(sub) != 1):
          raise Exception("Unexpected multi-element '%s' sub: %s" % (name, str(sub)))
        return sub[0]
      return default

    def get_list_sub(x, name, default=None):
      sub = get_sub(x, name)
      if (sub != None):
        if len(sub) < 1:
          return []
        else:
          return sub
      
    def get_layer_sub(x, default=None):
      layer = get_single_element_sub(x, 'layer')
      if (layer != None):
        return layer_name_to_type(layer)
      return default
    
    def get_layers_sub(x, default=None):
      layers = get_sub(x, 'layers')
      if (layers != None):
        return list(map(layer_name_to_type, layers))
      return default

    def get_at_sub(x):
      sub = get_sub(x, 'at')
      if (sub is None):
        raise Exception("Expected 'at' element in %s" % (str(x)))
      if (len(sub) == 2):
        [x1, y1] = sub
        rot = 0
      elif (len(sub) == 3):
        [x1, y1, rot] = sub
      else:
        raise Exception("Invalid 'at' element in %s" % (str(x)))      
      return (x1, y1, rot)

    def descr(x):
      meta['desc'] = x[1]

    # (pad 1 smd rect (size 1.1 1.0) (at -0.85 -0.0 0) (layers F.Cu F.Paste F.Mask))
    # (pad 5 thru_hole circle (size 0.75 0.75) (at 1.79 3.155 0) (layers *.Cu *.Mask) (drill 1.0))
    def pad(x):
      shape = {'name': _convert_sexp_symbol_to_string(x[1]) }
      smd = (_convert_sexp_symbol_to_string(x[2]) == 'smd')
      if smd:
        shape['type'] = 'smd'
      else:
        shape['type'] = 'pad'
      s = _convert_sexp_symbol_to_string(x[3])
      [x1, y1, rot] = get_at_sub(x)
      shape['x'] = x1
      shape['y'] = -y1
      shape['rot'] = rot
      [dx, dy] = get_sub(x, 'size')
      if s == 'circle':
        shape['shape'] = 'disc'
        shape['r'] = dx/2
      elif s == 'rect':
        shape['shape'] = 'rect'
        shape['dx'] = dx
        shape['dy'] = dy
      elif s == 'oval':
        shape['shape'] = 'rect'
        shape['dx'] = dx
        shape['dy'] = dy
        shape['ro'] = 100
      else:
        raise Exception("Pad with unknown shape %s" % (str(s)))
      if not smd:
        drill = get_sub(x, 'drill')
        shape['drill'] = drill[0]
        if has_sub(drill, 'offset'):
          [drill_dx, drill_dy] = get_sub(drill, 'offset')
          shape['drill_dx'] = drill_dx
          shape['drill_dy'] = -drill_dy
      return shape

    #(fp_line (start -2.54 -1.27) (end 2.54 -1.27) (layer F.SilkS) (width 0.381))
    def fp_line(x):
      [x1, y1] = get_sub(x, 'start')
      [x2, y2] = get_sub(x, 'end')
      layer = get_layer_sub(x, 'silk')
      width = get_single_element_sub(x, 'width')
      shape = { 
        'shape': 'vertex',
        'x1': x1, 'y1': -y1, 
        'x2': x2, 'y2': -y2, 
        'type': layer, 'w': width
      }
      return shape

    # (fp_circle (center 5.08 0) (end 6.35 -1.27) (layer F.SilkS) (width 0.15))
    def fp_circle(x):
      shape = { 'shape': 'circle' }
      shape['type'] = get_layer_sub(x, 'silk')
      [x1, y1] = get_sub(x, 'center')
      shape['x'] = x1
      shape['y'] = -y1
      shape['w'] = get_single_element_sub(x, 'width')
      [ex, ey] = get_sub(x, 'end')
      dx = abs(x1 - ex)
      dy = abs(y1 - ey)
      if f_eq(dx, dy):
        shape['r'] = dx*math.sqrt(2)
        if f_eq(shape['w'], shape['r']):
          shape['type'] = 'disc'
          shape['r'] = shape['r'] * 2
          del shape['w']
        elif shape['type'] == 'hole':
          shape['shape'] = 'hole'
          shape['drill'] = shape['r'] * 2
          del shape['w']
          del shape['r']
      else:
        shape['rx'] = dx*math.sqrt(2)
        shape['ry'] = dy*math.sqrt(2)
      return shape

    # (fp_arc (start 7.62 0) (end 7.62 -2.54) (angle 90) (layer F.SilkS) (width 0.15))
    def fp_arc(x):
      # start is actually center point
      [xc, yc] = get_sub(x, 'start')
      yc = -yc
      # end is actually start point of arc
      [x1, y1] = get_sub(x, 'end')
      y1 = -y1
      [angle] = get_sub(x, 'angle')
      a = angle*math.pi/180.0
      (x2, y2) = calc_second_point((xc,yc),(x1,y1),a)
      width = get_single_element_sub(x, 'width')
      shape = { 'shape': 'vertex'}
      shape['type'] = get_layer_sub(x, 'silk')
      shape['curve'] = -angle
      shape['x1'] = x1
      shape['y1'] = y1
      shape['x2'] = x2
      shape['y2'] = y2
      width = get_single_element_sub(x, 'width')
      shape['w'] = width
      return shape

    # (fp_poly (pts (xy 6.7818 1.6002) (xy 6.6294 1.6002) (xy 6.6294 1.4478) (xy 6.7818 1.4478) (xy 6.7818 1.6002)) (layer F.Cu) (width 0.00254))
    def fp_poly(x):
      width = get_single_element_sub(x, 'width')
      shape = { 'shape': 'polygon'}
      shape['w'] = width
      shape['type'] = get_layer_sub(x, 'silk')
      shape['v'] = []
      for p in get_list_sub(x, 'pts')[0:-1]:
        v = { 'shape':'vertex' }
        v['x1'] = p[1]
        v['y1'] = -p[2]
        shape['v'].append(v)
      l = len(shape['v'])
      for i in range(0, l):
        shape['v'][i]['x2'] = shape['v'][i-l+1]['x1']
        shape['v'][i]['y2'] = shape['v'][i-l+1]['y1']
      return shape

    # (fp_text reference MYCONN3 (at 0 -2.54) (layer F.SilkS)
    #   (effects (font (size 1.00076 1.00076) (thickness 0.25146)))
    # )
    # (fp_text value SMD (at 0 2.54) (layer F.SilkS) hide
    #   (effects (font (size 1.00076 1.00076) (thickness 0.25146)))
    # )
    def fp_text(x):
      shape = { 'shape': 'label', 'type': 'silk', 'value': '' }
      shape['value'] = _convert_sexp_symbol_to_string(x[2])
      shape['type'] = get_layer_sub(x, 'silk')
      
      if (_convert_sexp_symbol_to_string(x[1]) == "reference"):
        shape['value'] = 'NAME' # Override "NAME" field text
      elif (_convert_sexp_symbol_to_string(x[1]) == "value"):
        shape['value'] = 'VALUE' # Override "VALUE" field text
      else:
        # Don't let 'user' fields have 'NAME' or 'VALUE' as text
        if ((shape['value'] == 'NAME') or (shape['value'] == 'VALUE')):
          shape['value'] = "_%s_" % (shape['value'])
      
      [x1, y1, rot] = get_at_sub(x)
      font = get_sub(get_sub(x, 'effects'), 'font')
      [dx, dy] = get_sub(font, 'size')
      w = get_sub(font, 'thickness')
      shape['x'] = x1
      shape['y'] = -y1
      shape['w'] = w
      shape['dy'] = dy
      # TODO: Add rotated text support
      shape['rot'] = rot
      return shape

    for x in s[3:]:
      #print "ELEMENT:"
      #print x
      res = {
        'descr': descr,
        'pad': pad,
        'fp_line': fp_line,
        'fp_circle': fp_circle,
        'fp_arc': fp_arc,
        'fp_text': fp_text,
        'fp_poly': fp_poly,
      }.get(_convert_sexp_symbol_to_string(x[0]), lambda a: None)(x)
      if res != None:
        l.append(res)

    return clean_floats(l)

    
    
