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
  extra_data_files = ['msvcp90.dll',]
  extra_options = dict(
      setup_requires=['py2exe'],
      console=['madparts'],
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
  version = '1.0',
  url = 'http://madparts.org/',
  packages = [
        'coffee',
        'coffeescript',
        'export',
        'grind',
        'gui',
        'inter',
        'main',
        'shaders',
        'syntax',
        'util',
        ],
  package_data= { 
        'coffeescript': ['*.js', 'LICENSE', 'README'],
        'grind': ['*.coffee'],
        'gui': [
          'freefont.COPYING', 'FreeMonoBold.ttf',
          '../COPYING', '../README.md', # dirty trick ;)
          ],
        'shaders': ['*.vert', '*.frag'],
        },
  data_files = [
    ('share/madparts/examples', glob.glob('examples/*.coffee')),
    ] + extra_data_files,
  platforms = ["Windows", "Linux", "Mac OS-X"],
  **extra_options
  )
