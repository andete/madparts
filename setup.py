#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import glob, sys, platform

from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

arch = platform.uname()[4]

extra_data_files = []

if sys.platform == 'darwin':
  OPTIONS = {
      'argv_emulation': True,
      #'includes': ['sip', 'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui', 'simplejson'],
      #'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL', 'PyQt4.QtScript', 'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtWebKit', 'PyQt4.QtXml', 'PyQt4.phonon'],
      }
  extra_options = dict(
      setup_requires=['py2app'],
      app=['madparts'],
      # Cross-platform applications generally expect sys.argv to
      # be used for opening files.
      options=dict(py2app=OPTIONS),
      )
elif sys.platform == 'win32':
  import py2exe
  OPTIONS = {
    'includes': [
          "OpenGL.arrays._buffers",
          "OpenGL.arrays._numeric",
          "OpenGL.arrays._strings",
          "OpenGL.arrays.arraydatatype",
          "OpenGL.arrays.arrayhelpers",
          "OpenGL.arrays.buffers",
          "OpenGL.arrays.ctypesarrays",
          "OpenGL.arrays.ctypesparameters",
          "OpenGL.arrays.ctypespointers",
          "OpenGL.arrays.formathandler",
          "OpenGL.arrays.lists",
          "OpenGL.arrays.nones",
          "OpenGL.arrays.numbers",
          "OpenGL.arrays.numeric",
          "OpenGL.arrays.numericnames",
          "OpenGL.arrays.numpymodule",
          "OpenGL.arrays.strings",
          "OpenGL.arrays.vbo",
          "OpenGL.platform.ctypesloader",
          "OpenGL.platform.win32",

          "OpenGL_accelerate.formathandler",
          "OpenGL_accelerate.arraydatatype",
          "OpenGL_accelerate.errorchecker",
          "OpenGL_accelerate.latebind",
          "OpenGL_accelerate.nones_formathandler",
          "OpenGL_accelerate.numpy_formathandler",
          "OpenGL_accelerate.vbo",
          "OpenGL_accelerate.wrapper",
          ]
  }
  extra_data_files = ['msvcp90.dll',]
  extra_options = dict(
      setup_requires=['py2exe'],
      console=['madparts'],
      options=dict(py2exe=OPTIONS)
      )
elif sys.platform.startswith('linux'):
   extra_options = dict(
       # Normally unix-like platforms will use "setup.py install"
       # and install the main script as such
       scripts=['madparts'],
       )
   if not arch in ['x86_64']:
     raise Exception("unsupported arch %s" % (arch))
else:
  raise Exception("unsupported platform %s" % (sys.platform))

setup(
  name = 'madparts',
  description = 'a functional footprint editor',
  long_description = long_description,
  author = 'Joost Yervante Damad',
  author_email = 'joost@damad.be',
  version = '1.1',
  url = 'http://madparts.org/',
  packages = [
        'coffee',
        'export',
        'gui',
        'inter',
        'main',
        'syntax',
        'mutil',
        ],
  package_data= { 
        'gui': [
          '../COPYING', '../README.md', # dirty trick ;)
          ],
        },
  data_files = [
    ('share/madparts/examples', glob.glob('examples/*.coffee')),
    ('share/madparts/grind', glob.glob('grind/*.coffee')),
    ('share/madparts/coffeescript', ['coffeescript/LICENSE', 'coffeescript/README'] + glob.glob('coffeescript/*.js')),
    ('share/madparts/shaders', glob.glob('shaders/*.vert') + glob.glob('shaders/*.frag')),
    ('share/madparts/gui', ['gui/freefont.COPYING', 'gui/FreeMonoBold.ttf'] ),
    ] + extra_data_files,
  platforms = ["Windows", "Linux", "Mac OS-X"],
  **extra_options
  )
