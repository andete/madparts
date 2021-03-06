# (c) 2013-2015 Joost Yervante Damad <joost@damad.be>
# License: GPL

# default values for settings

color_schemes = {}
    
color_schemes['default'] = {
  'background': (0.0, 0.0, 0.0, 1.0),
  'grid': (0.5, 0.5, 0.5, 1.0),
  'axes': (1.0, 0.0, 0.0, 1.0),
  'name': (1.0, 1.0, 1.0, 1.0),
  'value': (1.0, 1.0, 1.0, 1.0),
  'silk': (1.0, 1.0, 1.0, 1.0),
  'bsilk': (0.7, 0.7, 0.7, 0.3),
  'docu': (1.0, 1.0, 0.0, 0.7),
  'smd': (0.0, 0.0, 1.0, 1.0),
  'pad': (0.0, 1.0, 0.0, 1.0),
  'meta':  (1.0, 1.0, 1.0, 1.0),
  'restrict':  (0.0, 1.0, 0.0, 0.3),
  'stop':  (0.0, 1.0, 1.0, 0.3),
  'keepout':  (1.0, 0.0, 0.5, 0.7),
  'bkeepout':  (0.7, 0.0, 0.35, 0.4),
  'vrestrict':  (0.0, 1.0, 0.0, 0.4),
  'unknown':  (1.0, 0.0, 1.0, 0.7),
  'hole': (1.0, 1.0, 1.0, 0.7),
  'edge': (1.0, 1.0, 1.0, 0.7),
  'paste': (0.0, 1.0, 0.0, 0.7),
  'bpaste': (0.0, 0.7, 0.0, 0.3),
  'comments': (0.82, 0.66, 0.63, 0.8),
  'assembly': (0.9, 0.6, 0.3, 0.8),
  'bassembly': (0.65, 0.5, 0.2, 0.5),
  'user1': (0.3, 0.6, 0.0, 0.7),
  'user2': (0.3, 0.0, 0.6, 0.7)
  }

def _inverse(color_scheme):
  re = {}
  for (k,(r,g,b,a)) in color_scheme.items():
    re[k] = (1.0-r, 1.0-g, 1.0-b, a)
  return re

color_schemes['inverse'] = _inverse(color_schemes['default'])

default_settings = {
  'gl/dx': '200',
  'gl/dy': '200',
  'gl/zoomfactor': '50',
  'gl/colorscheme': 'default',
  'gui/keyidle': '1500',
  'gl/autozoom': 'True',
  'gui/displaydocu': 'True',
  'gui/displayrestrict': 'False',
  'gui/displaystop': 'False',
  'gui/displaykeepout': 'False',
  'gui/autocompile': 'True',
}
