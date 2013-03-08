# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

# default values for settings

color_schemes = {}
    
color_schemes['default'] = {
  'background': (0.0, 0.0, 0.0),
  'grid': (0.5, 0.5, 0.5),
  'axes': (1.0, 0.0, 0.0),
  'name': (1.0, 1.0, 1.0),
  'value': (1.0, 1.0, 1.0),
  'silk': (1.0, 1.0, 1.0),
  'docu': (1.0, 1.0, 0.0),
  'smd': (0.0, 0.0, 1.0),
  'pad': (0.0, 1.0, 0.0),
  'meta':  (1.0, 1.0, 1.0),
  'restrict':  (0.0, 1.0, 0.0),
  'stop':  (0.0, 0.3, 0.3),
  'unknown':  (1.0, 0.0, 1.0),
  }

def _inverse(color_scheme):
  re = {}
  for (k,(r,g,b)) in color_scheme.items():
    re[k] = (1.0-r, 1.0-g, 1.0-b)
  return re

color_schemes['inverse'] = _inverse(color_schemes['default'])

default_settings = {
  'gl/dx': 200,
  'gl/dy': 200,
  'gl/fontfile': "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
  'gl/zoomfactor': 50,
  'gl/colorscheme': 'default',
  'gui/keyidle': 0.5,
}
