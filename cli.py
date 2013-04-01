#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import argparse, sys

import coffee.pycoffee as pycoffee
from inter import inter
import export.eagle

def export_footprint(args):
  with open(args.f[0], 'r') as f:
    code = f.read()
  (error_txt, status_txt, interim) = pycoffee.compile_coffee(code)
  if interim == None:
    print >> sys.stderr, error_txt
    return 1
  meta = filter(lambda x: x['type'] == 'meta', interim)[0]
  name = meta['name']
  print name, 'compiled.'
  library_file = args.l[0]
  try:
    version = export.eagle.check_xml_file(library_file)
  except Exception as ex:
    print >> sys.stderr, str(ex)
    return 1
  exporter = export.eagle.Export(library_file)
  exporter.export_footprint(interim)
  exporter.save()
  print "Exported to "+library_file+"."
  return 0

def import_footprint(args):
  print >> sys.stderr, 'Not implemented: import footprint'
  return 1

def cli_main():
  parser = argparse.ArgumentParser()
  parser.add_argument('command', help='command to execute', choices=['import','export'])
  parser.add_argument('-f', nargs=1, help='footprint file', required=True, metavar='FILE')
  parser.add_argument('-l', nargs=1, help='library file', required=True, metavar='FILE')
  args = parser.parse_args()
  if args.command == 'import':
    return import_footprint(args)
  else:
    return export_footprint(args)

if __name__ == '__main__':
  sys.exit(cli_main())
