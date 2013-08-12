# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import os.path
import shlex
import uuid
import math

import mutil.mutil as mutil

def detect(fn):
  if os.path.isdir(fn): return None
  try:
    with open(fn, 'r') as f:
      l = f.readlines()
      l0 = l[0]
      l2 = l0.split()
      if (l2[0] == 'PCBNEW-LibModule-V1'): 
        return "1" # imperial only
      elif (l2[0] == 'PCBNEW-LibModule-V2'):
        return "2" # support metric also
      return None
  except:
    return None

def num_to_type(i):
  i = int(i)
  return {
    17: 'glue',
    19: 'paste',
    21: 'silk',
    23: 'stop',
    24: 'docu', # ???
    25: 'docu', # ???
    28: 'hole', # actually, 'edge'
  }.get(i)

def type_to_num(t):
  return {
    'glue': 17,
    'paste': 19,
    'silk': 21,
    'stop': 23,
    'docu': 24,
    'hole': 28,
  }.get(t, 21)

class Export:

  def __init__(self, fn):
    self.fn = fn

  def export_footprint(self, interim):
    meta = inter.get_meta(interim)
    name = eget(meta, 'name', 'Name not found')
    idx = eget(meta, 'id', 'Id not found')
    descr = oget(meta, 'desc', '')
    parent_idx = oget(meta, 'parent', None)
    d = []
    # generate kicad-old for individual footprint
    # use metric; convert to imperial in "save" if needed
    d.append("$MODULE %s" % (name))
    d.append("Po 0 0 0 154F986D86 00000000 ~~") # dummy data
    d.append("Li %s" % (name))
    d.append("Cd %s" % (desc.replace('\n',' '))) # ugly
    # assuming Kw is optional
    d.append("Sc 00000000")
    d.append("Op 0 0 0")

  # DS Xstart Ystart Xend Yend Width Layer
  # DS 6000 1500 6000 -1500 120 21
  # DA Xcentre Ycentre Xstart_point Ystart_point angle width layer
  def vertex(shape, layer):
    l = []
    x1 = fget(shape, 'x1')
    y1 = fget(shape, 'y1')
    x2 = fget(shape, 'x2')
    y2 = fget(shape, 'y2')
    w = fget(shape, 'w')
    if not 'curve' in shape or shape['curve'] == 0.0:
      line = "DS %s %s %s %s %s %s" % (x1, fc(-y1), x2, fc(-y2), w, layer)
      l.append(line)
    else:
      curve =  fget(shape, 'curve')
      angle = curve*math.pi/180.0
      ((x0, y0), r, a1, a2) = calc_center_r_a1_a2((x1,y1),(x2,y2),angle)
      arc = "DA %s %s %s %s %s %s %s" 
        % (x0, fc(-y0), x1, fc(-y1), -(a2-a1), w, layer)
      l.append(arc)
    return l

    # DC Xcentre Ycentre Xpoint Ypoint Width Layer
    def circle(shape, layer):
      l = []
      x = fget(shape, 'x')
      y = fget(shape, 'y')
      r = fget(shape, 'r')
      w = fget(shape, 'w')
      if not 'a1' in shape and not 'a2' in shape:
        circle = "DC %s %s %s %s %s %s" 
          % (x, fc(-y), fc(x+(r/math.sqrt(2))), fc(-y+(r/math.sqrt(2))), w, layer)
        l.append(circle)
      else:
        l = [S('fp_arc')] 
        l.append(start)
        # start == center point
        # end == start point of arc
        # angle == angled part in that direction
        a1 = fget(shape, 'a1')
        a2 = fget(shape, 'a2')
        a1rad = a1 * math.pi/180.0
        ex = x + r*math.cos(a1rad)
        ey = y + r*math.sin(a1rad)
        arc = "DA %s %s %s %s %s %s %s" 
          % (x, fc(-y), ex, fc(-ey), -(a2-a1), w, layer)
        l.append(arc)
      return l

    # T0 -79 -3307 600 600 0 120 N V 21 N "XT"
    def label(shape, layer):
      s = shape['value'].upper()
      t = 'T2'
      visible = 'V'
      if s == 'VALUE': 
        t = 'T1'
        visible = 'I'
      if s == 'NAME': 
        t = 'T0'
      dy = fget(shape, 'dy', 1/1.6)
      w = fget(shape, 'w', 0.1)
      x = fget(shape, 'x')
      y = fc(-fget(shape, 'y'))
      line = "%s %s %s %s %s 0 %s N %s \"%s\"" % 
        (t, x, y, dy, dy, w, visible, shape['value'])
      return [l]

    def silk(shape):
      if not 'shape' in shape: return None
      layer = type_to_num(shape['type'])
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
        l = {
          'pad': pad,
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
        if l != None:
         d += l
      
    d.append("$ENDMODULE %s" % (name))
    self.data = d

  def save(self):
    # check index and see if part already exist, making it an
    # overwrite or an insert
    pass
    
class Import:

  def __init__(self, fn):
    self.fn = fn

  def import_module(self, name, lines, metric):
    meta = {}
    meta['type'] = 'meta'
    meta['name'] = name
    meta['id'] = uuid.uuid4().hex
    meta['desc'] = None
    l = [meta]

    def cd(s, d): 
      if meta['desc'] == None:
        meta['desc'] = d
      else:
        meta['desc'] = meta['desc'] + "\n" + d
      return None

    def label(s, labeltype='user'):
      shape = { 'shape': 'label', 'type': 'silk' }
      shape['value'] = s[11]
      if (labeltype == 'value'):
        shape['value'] = 'VALUE'
      if (labeltype == 'reference'):
        shape['value'] = 'NAME'
      shape['x'] = float(s[1])
      shape['y'] = -float(s[2])
      shape['dy'] = float(s[3])
      shape['w'] = float(s[6])
      return shape

    def line(s):
      shape = { 'shape': 'line' }
      shape['x1'] = float(s[1])
      shape['y1'] = -float(s[2])
      shape['x2'] = float(s[3])
      shape['y2'] = -float(s[4])
      shape['w'] = float(s[5])
      shape['type'] = num_to_type(s[6])
      return shape

    # DC Xcentre Ycentre Xpoint Ypoint Width Layer
    def circle(s):
      shape = { 'shape': 'circle' }
      x = float(s[1])
      y = -float(s[2])
      shape['x'] = x
      shape['y'] = y
      ex = float(s[3])
      ey = float(s[4])
      shape['w'] = float(s[5])
      dx = abs(x - ex)
      dy = abs(y - ey)
      shape['r'] = math.sqrt(dx*dx + dy*dy)
      if mutil.f_eq(shape['w'], shape['r']):
        shape['shape'] = 'disc'
        shape['r'] = shape['r'] * 2
        del shape['w']
      shape['type'] = num_to_type(s[6])
      if shape['type'] == 'hole':
        shape['drill'] = shape['r'] * 2
        shape['shape'] = 'hole'
        delete shape['w']
        delete shape['r']
      return shape

    # DA Xcentre Ycentre Xstart_point Ystart_point angle width layer
    def arc(s):
      shape = { 'shape': 'vertex' }
      xc = float(s[1])
      yc = -float(s[2])
      x1 = float(s[3])
      y1 = -float(s[4])
      angle = float(s[5])/10
      a = angle*math.pi/180.0
      (x2, y2) = mutil.calc_second_point((xc,yc),(x1,y1),a)
      shape['w'] = float(s[6])
      shape['type'] = num_to_type(s[7])
      shape['curve'] = -angle
      shape['x1'] = x1
      shape['y1'] = y1
      shape['x2'] = x2
      shape['y2'] = y2
      return shape

    # DP 0 0 0 0 corners_count width layer
    # Dl corner_posx corner_posy
    def import_polygon(lines, k):
      shape = { 'shape': 'polygon'}
      s = shlex.split(lines[k])
      count = int(s[5])
      shape['w'] = float(s[6])
      shape['type'] = num_to_type(s[7])
      shape['v'] = []
      for j in range(k+1, k+count): # don't want last looping back
        s = shlex.split(lines[j])
        v = { 'shape':'vertex' }
        v['x1'] = float(s[1])
        v['y1'] = -float(s[2])
        shape['v'].append(v)
      l = len(shape['v'])
      for i in range(0, l):
        shape['v'][i]['x2'] = shape['v'][i-l+1]['x1']
        shape['v'][i]['y2'] = shape['v'][i-l+1]['y1']
      return (k+count+1, shape)

    def import_pad(lines, i):
      shape = { }
   
      def drill(s):
        # Dr <Pad drill> Xoffset Yoffset (round hole)
        if len(s) == 4:
          d = float(s[1])
          dx = float(s[2])
          dy = float(s[3])
          if d != 0.0:
            shape['drill'] = d
          if dx != 0.0:
            shape['drill_dx'] = dx
          if dy != 0.0:
            shape['drill_dy'] = dy
        # Dr <Pad drill.x> Xoffset Yoffset <Hole shape> <Pad drill.x> <Pad drill.y>
        else:
          print "oblong holes are currently not supported by madparts (converted to round)"
          d = float(s[1])
          dx = float(s[2])
          dy = float(s[3])
          if d != 0.0:
            shape['drill'] = d
          if dx != 0.0:
            shape['drill_dx'] = dx
          if dy != 0.0:
            shape['drill_dy'] = dy

      # Sh <pad name> shape Xsize Ysize Xdelta Ydelta Orientation 
      def handle_shape(s):
        shape['name'] = s[1]
        dx = float(s[3])
        dy = float(s[4])
        # xdelta, ydelta not used?
        rot = int(s[7])/10
        if rot != 0:
          shape['rot'] = rot
        sh = s[2]
        if sh == 'C':
          shape['shape'] = 'disc'
          shape['r'] = dx/2
        elif sh == 'O':
          shape['shape'] = 'rect'
          shape['ro'] = 100
          shape['dx'] = dx
          shape['dy'] = dy
        # trapeze is converted to rect for now
        elif sh == 'R' or sh == 'T':
          shape['shape'] = 'rect'
          shape['dx'] = dx
          shape['dy'] = dy
   
      # At <Pad type> N <layer mask>
      def attributes(s):
        if s[1] == 'SMD':
          shape['type'] = 'smd'
        else:
          shape['type'] = 'pad'

      # Po <x> <y>
      def position(s):
        shape['x'] = float(s[1])
        shape['y'] = -float(s[2])

      while i < len(lines):
        s = shlex.split(lines[i])
        k = s[0].lower()
        if k == "$endpad":
          print shape
          return (i+1, shape)
        else:
          {
            'sh': handle_shape,
            'dr': drill,
            'at': attributes,
            'po': position,
          }.get(k, lambda a: None)(s)
          i = i + 1
    
    i = 0
    while i < len(lines):
      s = shlex.split(lines[i])
      k = s[0].lower()
      if k == '$endmodule':
        break
      elif k == '$pad':
        (i, pad) = import_pad(lines, i)
        l.append(pad)
      elif k == 'dp':
        (i, poly) = import_polygon(lines, i)
        l.append(poly)
      else:
        res = {
          'cd': lambda a: cd(a, lines[i][3:]),
          't0': lambda a: label(a, 'reference'),
          't1': lambda a: label(a, 'value'),
          't2': lambda a: label(a, 'user'),
          'ds': line,
          'dc': circle,
          'da': arc,
        }.get(k, lambda a: None)(s)
        if res != None:
          l.append(res)
        i = i + 1
    if not metric:
      # convert to metric from tenths of mils
      for x in l:
        for k in x.keys():
          if type(x[k]) == type(3.14):
            x[k] = x[k] * 0.00254
    l = mutil.clean_floats(l)
    return l

  def import_footprint(self, name):
    metric = False
    with open(self.fn, 'r') as f:
      lines = f.readlines()
    for i in range(0, len(lines)):
      s = shlex.split(lines[i])
      if s[0] == 'Units' and s[1] == 'mm':
        metric = True
      if s[0] == '$MODULE' and s[1] == name:
        return self.import_module(name, lines[i+1:], metric)
    raise Exception("footprint not found %s" % (name))

  def list(self):
    with open(self.fn, 'r') as f:
      lines = f.readlines()
    for line in lines:
      s = shlex.split(line)
      if s[0] == '$MODULE':
        print s[1]

  def list_names(self):
    l = []
    with open(self.fn, 'r') as f:
      lines = f.readlines()
      for line in lines:
        s = shlex.split(line)
        k = s[0].lower()
        if k == '$module':
          name = s[1]
          desc = None
        elif k == 'cd':
          desc = s[1]
        elif k == '$endmodule':
          l.append((name, desc))
    return l
