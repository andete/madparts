# (c) 2013 Joost Yervante Damad <joost@damad.be>
# License: GPL

from nose.tools import *

import coffee.pycoffee as pycoffee
import coffee.generatesimple as generatesimple
from inter import inter
import export.eagle

assert_multi_line_equal.im_class.maxDiff = None

def _export_eagle(code, expected):
  eagle_lib = 'export/eagle_empty.lbr'
  (error_txt, status_txt, interim) = pycoffee.compile_coffee(code)
  assert interim != None
  version = export.eagle.check_xml_file(eagle_lib)
  assert version == 'Eagle CAD 6.4 library'
  exporter = export.eagle.Export(eagle_lib)
  exporter.export_footprint(interim)
  data = exporter.get_pretty_data()
  assert_multi_line_equal(data, expected)

def _export_eagle_package(code, expected):
  eagle_lib = 'export/eagle_empty.lbr'
  (error_txt, status_txt, interim) = pycoffee.compile_coffee(code)
  assert interim != None
  version = export.eagle.check_xml_file(eagle_lib)
  assert version == 'Eagle CAD 6.4 library'
  exporter = export.eagle.Export(eagle_lib)
  eagle_name = exporter.export_footprint(interim)
  data = exporter.get_pretty_footprint(eagle_name)
  print data
  assert_multi_line_equal(data, expected)
  

def test_export_eagle_full_lib():
   code = """\
#format 1.1
#name DIL16
#id 2ba395a2e67a49bd9defdf961b264e9f
#parent 5162a77450f545079d5716a7c67b2b42
footprint = () ->
 
  n = 16
  e = 2.54
  between = 7.62
  diameter = 1.2
  drill = 0.8
  line_width = 0.3
  outer_y = n*e/4
  half = between/2

  name = new Name outer_y+e/3
  value = new Value -outer_y-e/3

  pad = new LongPad diameter, drill
  l = dual [pad], n, e, between

  # make first pad round
  l[1-1].shape = 'disc'
  l[1-1].r = diameter*3/4

  silk1 = new Line line_width
  silk1.x1 = half-diameter-0.5
  silk1.y1 = outer_y
  silk1.x2 = half-diameter-0.5
  silk1.y2 = -outer_y

  silk2 = rotate180 clone silk1

  silk3 = new Line line_width
  silk3.y1 = outer_y
  silk3.x1 = half-diameter-0.5
  silk3.y2 = outer_y
  silk3.x2 = -half+diameter+0.5

  silk4 = rotate180 clone silk3

  silks = [silk1, silk2, silk3, silk4]

  combine [l,name,silks,value]
"""

   expected = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="6.4">
 <drawing>
  <settings>
   <setting alwaysvectorfont="no"/>
   <setting verticaltext="up"/>
  </settings>
  <grid altdistance="0.01" altunit="inch" altunitdist="inch" display="no" distance="0.1" multiple="1" style="lines" unit="inch" unitdist="inch"/>
  <layers>
   <layer active="yes" color="4" fill="1" name="Top" number="1" visible="yes"/>
   <layer active="yes" color="1" fill="3" name="Route2" number="2" visible="no"/>
   <layer active="yes" color="4" fill="3" name="Route3" number="3" visible="no"/>
   <layer active="yes" color="1" fill="4" name="Route4" number="4" visible="no"/>
   <layer active="yes" color="4" fill="4" name="Route5" number="5" visible="no"/>
   <layer active="yes" color="1" fill="8" name="Route6" number="6" visible="no"/>
   <layer active="yes" color="4" fill="8" name="Route7" number="7" visible="no"/>
   <layer active="yes" color="1" fill="2" name="Route8" number="8" visible="no"/>
   <layer active="yes" color="4" fill="2" name="Route9" number="9" visible="no"/>
   <layer active="yes" color="1" fill="7" name="Route10" number="10" visible="no"/>
   <layer active="yes" color="4" fill="7" name="Route11" number="11" visible="no"/>
   <layer active="yes" color="1" fill="5" name="Route12" number="12" visible="no"/>
   <layer active="yes" color="4" fill="5" name="Route13" number="13" visible="no"/>
   <layer active="yes" color="1" fill="6" name="Route14" number="14" visible="no"/>
   <layer active="yes" color="4" fill="6" name="Route15" number="15" visible="no"/>
   <layer active="yes" color="1" fill="1" name="Bottom" number="16" visible="yes"/>
   <layer active="yes" color="2" fill="1" name="Pads" number="17" visible="yes"/>
   <layer active="yes" color="2" fill="1" name="Vias" number="18" visible="yes"/>
   <layer active="yes" color="6" fill="1" name="Unrouted" number="19" visible="yes"/>
   <layer active="yes" color="15" fill="1" name="Dimension" number="20" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="tPlace" number="21" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="bPlace" number="22" visible="yes"/>
   <layer active="yes" color="15" fill="1" name="tOrigins" number="23" visible="yes"/>
   <layer active="yes" color="15" fill="1" name="bOrigins" number="24" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="tNames" number="25" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="bNames" number="26" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="tValues" number="27" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="bValues" number="28" visible="yes"/>
   <layer active="yes" color="7" fill="3" name="tStop" number="29" visible="no"/>
   <layer active="yes" color="7" fill="6" name="bStop" number="30" visible="no"/>
   <layer active="yes" color="7" fill="4" name="tCream" number="31" visible="no"/>
   <layer active="yes" color="7" fill="5" name="bCream" number="32" visible="no"/>
   <layer active="yes" color="6" fill="3" name="tFinish" number="33" visible="no"/>
   <layer active="yes" color="6" fill="6" name="bFinish" number="34" visible="no"/>
   <layer active="yes" color="7" fill="4" name="tGlue" number="35" visible="no"/>
   <layer active="yes" color="7" fill="5" name="bGlue" number="36" visible="no"/>
   <layer active="yes" color="7" fill="1" name="tTest" number="37" visible="no"/>
   <layer active="yes" color="7" fill="1" name="bTest" number="38" visible="no"/>
   <layer active="yes" color="4" fill="11" name="tKeepout" number="39" visible="yes"/>
   <layer active="yes" color="1" fill="11" name="bKeepout" number="40" visible="yes"/>
   <layer active="yes" color="4" fill="10" name="tRestrict" number="41" visible="yes"/>
   <layer active="yes" color="1" fill="10" name="bRestrict" number="42" visible="yes"/>
   <layer active="yes" color="2" fill="10" name="vRestrict" number="43" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Drills" number="44" visible="no"/>
   <layer active="yes" color="7" fill="1" name="Holes" number="45" visible="no"/>
   <layer active="yes" color="3" fill="1" name="Milling" number="46" visible="no"/>
   <layer active="yes" color="7" fill="1" name="Measures" number="47" visible="no"/>
   <layer active="yes" color="7" fill="1" name="Document" number="48" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Reference" number="49" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="tDocu" number="51" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="bDocu" number="52" visible="yes"/>
   <layer active="yes" color="2" fill="1" name="Nets" number="91" visible="yes"/>
   <layer active="yes" color="1" fill="1" name="Busses" number="92" visible="yes"/>
   <layer active="yes" color="2" fill="1" name="Pins" number="93" visible="no"/>
   <layer active="yes" color="4" fill="1" name="Symbols" number="94" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Names" number="95" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Values" number="96" visible="yes"/>
   <layer active="yes" color="7" fill="1" name="Info" number="97" visible="yes"/>
   <layer active="yes" color="6" fill="1" name="Guide" number="98" visible="yes"/>
  </layers>
  <library>
   <packages>
    <package name="DIL16">
     <description>
      &lt;br/&gt;&lt;br/&gt;
Generated by 'madparts'.&lt;br/&gt;
Id: 2ba395a2e67a49bd9defdf961b264e9f
 parent: 5162a77450f545079d5716a7c67b2b42
     </description>
     <pad diameter="1.8" drill="0.8" name="1" rot="R180" shape="round" x="-3.81" y="8.89"/>
     <pad drill="0.8" name="2" rot="R180" shape="long" x="-3.81" y="6.35"/>
     <pad drill="0.8" name="3" rot="R180" shape="long" x="-3.81" y="3.81"/>
     <pad drill="0.8" name="4" rot="R180" shape="long" x="-3.81" y="1.27"/>
     <pad drill="0.8" name="5" rot="R180" shape="long" x="-3.81" y="-1.27"/>
     <pad drill="0.8" name="6" rot="R180" shape="long" x="-3.81" y="-3.81"/>
     <pad drill="0.8" name="7" rot="R180" shape="long" x="-3.81" y="-6.35"/>
     <pad drill="0.8" name="8" rot="R180" shape="long" x="-3.81" y="-8.89"/>
     <pad drill="0.8" name="9" rot="R0" shape="long" x="3.81" y="-8.89"/>
     <pad drill="0.8" name="10" rot="R0" shape="long" x="3.81" y="-6.35"/>
     <pad drill="0.8" name="11" rot="R0" shape="long" x="3.81" y="-3.81"/>
     <pad drill="0.8" name="12" rot="R0" shape="long" x="3.81" y="-1.27"/>
     <pad drill="0.8" name="13" rot="R0" shape="long" x="3.81" y="1.27"/>
     <pad drill="0.8" name="14" rot="R0" shape="long" x="3.81" y="3.81"/>
     <pad drill="0.8" name="15" rot="R0" shape="long" x="3.81" y="6.35"/>
     <pad drill="0.8" name="16" rot="R0" shape="long" x="3.81" y="8.89"/>
     <text align="center" layer="25" size="1.0" x="0.0" y="11.0066666667">
      &gt;NAME
     </text>
     <wire layer="21" width="0.3" x1="2.11" x2="2.11" y1="10.16" y2="-10.16"/>
     <wire layer="21" width="0.3" x1="-2.11" x2="-2.11" y1="-10.16" y2="10.16"/>
     <wire layer="21" width="0.3" x1="2.11" x2="-2.11" y1="10.16" y2="10.16"/>
     <wire layer="21" width="0.3" x1="-2.11" x2="2.11" y1="-10.16" y2="-10.16"/>
     <text align="center" layer="27" size="1.0" x="0.0" y="-11.0066666667">
      &gt;VALUE
     </text>
    </package>
   </packages>
   <symbols>
   </symbols>
   <devicesets>
   </devicesets>
  </library>
 </drawing>
</eagle>"""

   _export_eagle(code, expected)

def test_eagle_footprint1():
  code = """\
#format 1.1
#name PIN 1X2
#id 708e13cc5f4e43f7833af53070ba5078
#desc 2 pin pinheader
footprint = () ->

  d = 2.54
  drill = 1
  w = 0.15
  pad_r = (d-0.34)/2
  n = 2

  name = new Name (n*d/2+1)
  value = new Value (-n*d/2-1)
  
  pad = new RoundPad pad_r, drill

  silk1 = new Line w
  silk1.x1 = d/2
  silk1.y1 = -d/4
  silk1.x2 = d/2
  silk1.y2 = d/4
  silk2 = rotate90 clone silk1
  silk3 = rotate90 clone silk2
  silk4 = rotate90 clone silk3

  silk5 = new Line w
  silk5.y1 = d/4
  silk5.x1 = d/2
  silk5.y2 = d/2
  silk5.x2 = d/4
  silk6 = rotate90 clone silk5
  silk7 = rotate90 clone silk6
  silk8 = rotate90 clone silk7

  unit = [pad, silk1, silk2, silk3, silk4, silk5, silk6, silk7, silk8]

  units = single unit, n, d

  combine [name,value, units]
"""
  expected = """\
<package name="PIN_1X2">
 <description>
  2 pin pinheader
&lt;br/&gt;&lt;br/&gt;
Generated by 'madparts'.&lt;br/&gt;
Id: 708e13cc5f4e43f7833af53070ba5078
 </description>
 <text align="center" layer="25" size="1.0" x="0.0" y="3.54">
  &gt;NAME
 </text>
 <text align="center" layer="27" size="1.0" x="0.0" y="-3.54">
  &gt;VALUE
 </text>
 <pad diameter="2.2" drill="1.0" name="1" rot="R0" shape="round" x="0.0" y="1.27"/>
 <wire layer="21" width="0.15" x1="1.27" x2="1.27" y1="0.635" y2="1.905"/>
 <wire layer="21" width="0.15" x1="0.635" x2="-0.635" y1="2.54" y2="2.54"/>
 <wire layer="21" width="0.15" x1="-1.27" x2="-1.27" y1="1.905" y2="0.635"/>
 <wire layer="21" width="0.15" x1="-0.635" x2="0.635" y1="0.0" y2="0.0"/>
 <wire layer="21" width="0.15" x1="1.27" x2="0.635" y1="1.905" y2="2.54"/>
 <wire layer="21" width="0.15" x1="-0.635" x2="-1.27" y1="2.54" y2="1.905"/>
 <wire layer="21" width="0.15" x1="-1.27" x2="-0.635" y1="0.635" y2="0.0"/>
 <wire layer="21" width="0.15" x1="0.635" x2="1.27" y1="0.0" y2="0.635"/>
 <pad diameter="2.2" drill="1.0" name="2" rot="R0" shape="round" x="0.0" y="-1.27"/>
 <wire layer="21" width="0.15" x1="1.27" x2="1.27" y1="-1.905" y2="-0.635"/>
 <wire layer="21" width="0.15" x1="0.635" x2="-0.635" y1="0.0" y2="0.0"/>
 <wire layer="21" width="0.15" x1="-1.27" x2="-1.27" y1="-0.635" y2="-1.905"/>
 <wire layer="21" width="0.15" x1="-0.635" x2="0.635" y1="-2.54" y2="-2.54"/>
 <wire layer="21" width="0.15" x1="1.27" x2="0.635" y1="-0.635" y2="0.0"/>
 <wire layer="21" width="0.15" x1="-0.635" x2="-1.27" y1="0.0" y2="-0.635"/>
 <wire layer="21" width="0.15" x1="-1.27" x2="-0.635" y1="-1.905" y2="-2.54"/>
 <wire layer="21" width="0.15" x1="0.635" x2="1.27" y1="-2.54" y2="-1.905"/>
</package>"""
  _export_eagle_package(code, expected)
