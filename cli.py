#!/usr/bin/env python
#
# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

import argparse

def cli_main():
  parser = argparse.ArgumentParser()
  parser.add_argument('command', help='command to execute', choices=['import','export'])
  parser.add_argument('-f', nargs=1, help='footprint file', required=True, metavar='FILE')
  parser.add_argument('-l', nargs=1, help='library file', required=True, metavar='FILE')
  args = parser.parse_args()
  print args

if __name__ == '__main__':
  cli_main()
