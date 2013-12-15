# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import math

def oget(m, k, d):
  if k in m: return m[k]
  return d

def fget(m, k, d = 0.0):
  f = float(oget(m, k, d))
  if str(f)=='-0.0':
    return -f
  return f

def iget(m, k, d = 0.0):
  return int(oget(m, k, d))

def eget(m, k, e):
  if k in m: return m[k]
  raise Exception(e)

def generate_ints():
  for i in xrange(1, 10000):
    yield i

def f_eq(a, b):
  return abs(a-b) < 1E-8

def f_neq(a, b):
  return not f_eq(a, b)

def list_combine(l):
  l2 = []
  for x in l: l2 = l2 + x
  return l2

# angle is expected in radians
def calc_center_r_a1_a2(p, q, angle):
  (x1, y1) = p
  (x2, y2) = q
  dx = x2-x1
  dy = y2-y1
  # l: distance between p and q
  l = math.sqrt(dx*dx + dy*dy)
  angle_for_sin = abs(angle)
  if angle_for_sin > math.pi:
    angle_for_sin = -(2*math.pi-angle)
  # rc: radius of circle containing p and q and arcing through it
  #     with 'angle'
  rc = l / (2 * math.sin(angle_for_sin/2))
  # a: distance from center point to point in between p and q
  a = math.sqrt((rc * rc) - ((l/2)*(l/2)))
  # (ndx, ndy): unit vector pointing from p to q
  (ndx, ndy) = (dx / l, dy / l)
  # (pdx, pdy): perpendicular unit vector
  (pdx, pdy) = (-ndy, ndx)
  # (x3, y3): point between p and q
  (x3,y3) = ((x1+x2)/2, (y1+y2)/2) 
  # (fx, fy): (x3, y3) vector with length a
  # fix sign of (fx, fy) if needed
  (fx, fy) = (a*pdx, a*pdy)
  if rc > 0:
     (fx, fy) = (-fx, -fy)
  if angle > 0:
     (fx, fy) = (-fx, -fy)
  # (x0, y0): center point of circle aka 'c'
  (x0, y0) = (x3 + fx, y3 + fy)
  # (cpx, cpy): vector from c to p
  (cpx, cpy) = (x1-x0, y1-y0)
  # (cqx, cqy): vector from c to q
  (cqx, cqy) = (x2-x0, y2-y0)
  # calculate angles
  a1 = math.acos(cpx/rc)
  a1s = math.asin(cpy/rc)
  a2 = math.acos(cqx/rc)
  a2s = math.asin(cqy/rc)
  if a1s < 0:
    a1 = 2*math.pi - a1
  if a2s < 0:
    a2 = 2*math.pi - a2
  a1 = a1 * 180 / math.pi
  a2 = a2 * 180 / math.pi
  if angle < 0:
    (a1, a2) = (a2, a1)
  return ((x0, y0), rc, a1, a2)

def calc_second_point(c, s, a):
   (xc, yc) = c
   (x1, y1) = s
   dx = x1-xc
   dy = y1-yc
   r = math.sqrt(dx*dx + dy*dy)
   a1 = math.acos(dx/r)
   if math.asin(dy/r) < 0:
     a1 = 2*math.pi - a1
   a2 = a1 - a
   x2 = xc + r*math.cos(a2)
   y2 = yc + r*math.sin(a2)
   return (x2, y2)

def fc(f):
  if str(f)=='-0.0':
    return -f
  return f

def clean_floats(l):
  def clean_one(h):
    for k in h.keys():
      v = h[k]
      if k == 'v':
        h[k] = clean_floats(v)
      if type(v) == type(42.3):
        if str(v)=='-0.0':
          h[k] = -v
    return h
  return [clean_one(x) for x in l]
