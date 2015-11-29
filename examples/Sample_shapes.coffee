#format 1.2
#name Sample shapes
#desc Overview of madparts capabilities
#desc Code is 99%+ madparts example code
#desc Lot of extra code here moving parts into a display layout  .... you do not normally need to do this. 
#desc   Best if footprints centered on origin 0,0
#desc   then they rotate/mirror nicely in Kicad/Eaglewithout jumping position!
#desc ** Some useful tips & some really powerfull tips are labelled 'Tip:-' :)

##
## so if you want to create footprints ...
## and don't want LOTS of mistake prone mouse clicks - ESPECIALLY when revising
## Do want very quickly revise/clone/full rehash footprints
## Want simple automation of repeating footprint features
## Creates Kicad and eagle footprints
## Import, EDIT, CONVERT Kicad & eagle footprints... old/new formats
## .......
## 
## DO SCREEN CAPTURE MADPARTS & KICAD & EAGLE OF SAME SHAPES!!!!!
##  ... AND DEMO SINGLE/QUAD ... INCLUDING DIF LAYOUTS/EXPLODED/CUTTING
## .. demo some imported footprints
## 
## ?? do a legend of labels in each layer - to get the layer colours
## and to doc the layers & maybe which object go in each layer

# gather some "related code" refs - eg [] = list


footprint = () ->

#Tip:- Units: Milimeters are used everywhere. 
# Can suffix number with mi or mil for mils and with in for inches. 
# eg: 1in, 6mi. 
# Note that no space is allowed between the number and the suffix.

# Tip:- Common variables used. 

  size = 11		# width of the footprint, sometimes known as between

# Note some variables are ALSO commonly used in datasheets (d, e...)
  d = 5		# distance between pin/pad ROW CENTERS??, 
		# distance between 'auto-generated' objects (pads, lines, ...) when using single etc?????
  dia = 1.5		# diameter
  drill = 1.05		# drill diameter
  dx = 1		# delta x/y distance, ie a relative distance
  dy = 2		# delta x/y distance, ie a relative distance
  e = 2.54		#  distance between pads, ?pin pitch = distance between pad centers?
  n = 2		# total number of pins for device
  r = 2		# radius
  ro = 100		# rounding of pads ENDs. 0 = square, 100% = semi#circular end
  w = 0.05		# line width
  x = 0.3		# absolute x/y co#ordinates. Also x1, y1 etc
  y = 0.4		# absolute x/y co#ordinates. Also x1, y1 etc

  length = 4		# using for length of some lines

#Sample code vars
  # some var/s to track last shape pos AND which dir next
  grid_size_x = 5	# layout shapes this many per row
  grid_size_y = 5	# layout shapes this many per col
  grid_x_offset = -2	# want X & Y to go +/- about origin ... to fit how madparts viewer zooms/pans
  grid_y_offset = -2	# want X & Y to go +/- about origin ... to fit how madparts viewer zooms/pans
  shape_count = 0	# number shapes created so far (don't forget add each one to combine!)
  current_row = grid_y_offset	# current row to place shapes

#create each sample shape and place it on a grid centered around origin
  rect = new Rect	# filled area type silk
  rect.name = "rect"
  rect.dx = dx
  rect.dy = dy
  rect.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  rect.y = current_row * d
  shape_count += 1

  disc = new Disc r	# filled area type silk
  disc.name = "disc"
  disc.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  disc.y = current_row * d
  shape_count += 1

  circle = new Circle w	# outline only, type silk
  circle.name = "circle"
  circle.r = r
  circle.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  circle.y = current_row * d
  shape_count += 1

  hole = new Hole drill	# non-plated - use pad to get plated hole
  hole.name = "hole does not show it's name!"
  hole.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  hole.y = current_row * d
  shape_count += 1

#An Arc is just a vertex with typically curve!=0.
  arc = new Arc w
  arc.name = "arc's do not show their name!"
  arc.x1 = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  arc.y1 =current_row * d
  arc.x2 = arc.x1 + 1.5
  arc.y2 =arc.y1 - 1.5
  arc.curve = 100
  shape_count += 1

  angle  = 45
  c = new Circle 0.2
  c.name = "circle not arc! NOTE: moving this circle leaves TWO dots at original postions of circle arc ends!"
  c.r = 2
  c.a1 = angle
  c.a2 = angle+180
  c.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  c.y = current_row * d
  shape_count += 1

# A Line is just a Vertex with curve=0.
  line = new Line w
  line.name = "line's do not show their names!"
  line.x1 =d * ((shape_count % grid_size_x) + grid_x_offset)
  line.y1 = current_row * d
  line.y += d if (shape_count % grid_size_x) == 0
  line.x2 = line.x1 + length
  line.y2 =line.y1 + length
  line.curve = 0		# > 0 turns line into a curve!
  shape_count += 1


# Normally you don't manipulate the list of vertices directly, but use methods shown
#     Note eagle supports polygons curves but kicad does not at the moment
  polygon = new Polygon w
  polygon.name = "polygon"
  polygon.type = 'docu'
  polygon.start 0, 1
  polygon.add -1, 0, 180
  polygon.add 0, -1, 180
  polygon.add 1, 0, -10
  polygon.end -10
  px =d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  py = current_row * d
  shape_count += 1
  adjust polygon, px, py

  p2 = new Polygon w
  p2.name = "p2"
  p2.type = 'keepout'	# same as polygon above, but dif layer = dif colour here, and is dif position so can be seen
  p2.start 0, 1
  p2.add -1, 0, 180
  p2.add 0, -1, 180
  p2.add 1, 0, -10
  p2.end -10		#end polygon with curvage
  p2x =d * ((shape_count % grid_size_x) + grid_x_offset)
  shape_count += 1
  adjust p2, p2x, 0	# note not using x/y properties to set position

  p3 = new Polygon 0.1
  p3.start -1,-1
  p3.add -1, 1
  p3.add 0, 1
  p3.add 1, 0, -90
  p3.end -70
  current_row += 1 if (shape_count % grid_size_x) == 0
  p3y = current_row * d
  p3x =d * ((shape_count % grid_size_x) + grid_x_offset)
  rotate90 p3
  shape_count += 1
  adjust p3, p3x, p3y	# note not using x/y properties to set position

  p4 = new Polygon 0.05
  p4.start 1,1
  p4.add 1,0
  p4.add 0,1
  p4.end 0
  current_row += 1 if (shape_count % grid_size_x) == 0
  p4y = current_row * d
  p4x =d * ((shape_count % grid_size_x) + grid_x_offset)
  rotate90 p4
  shape_count += 1
  adjust p4, p4x, p4y	# note not using x/y properties to set position

  p5 = new Polygon 0.05
  p5.type = 'docu'
  p5.start 1, 0
  p5.add 3, 2, 40
  p5.add 4,0, -45
  p5.add 3,-2,-40
  p5.end 40
  current_row += 1 if (shape_count % grid_size_x) == 0
  p5y = current_row * d
  p5x =d * ((shape_count % grid_size_x) + grid_x_offset)
  rotate90 p5
  shape_count += 1
  adjust p5, p5x, p5y-2	# note not using x/y properties to set position

# try use vertex and polygon???
  vertex = new Vertex w 
  vertex.x1 = 3
  vertex.y1 = -2
  vertex.x2 = 1
  vertex.y2 = -0.5
  vertex.curve = 100

  # just ONE SMD pad - it is auto-numbered
  smd_pad = new Smd
  smd_pad.dx = 1.1
  smd_pad.dy = 1.0
  smd_pad.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  smd_pad.y = current_row * d
  shape_count += 1

  r_pad = new RoundPad r, drill
  r_pad.dx = 1.1
  r_pad.dy = 1.0
  r_pad.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  r_pad.y = current_row * d
  shape_count += 1

  s_pad = new SquarePad dia, drill
  s_pad.dx = 2.0
  s_pad.dy = 2.0
  s_pad.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  s_pad.y = current_row * d
  shape_count += 1

  l_pad = new LongPad dia, drill
  l_pad.dx = 4.0
  l_pad.dy = 2.0
  l_pad.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  l_pad.y = current_row * d
  shape_count += 1

# "Exception: octagon shaped pad not supported in kicad" ... so don't use for Kicad :(
  o_pad = new OctagonPad r, drill
  o_pad.dx = 3.0
  o_pad.dy = 3.0
  o_pad.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  o_pad.y = current_row * d
  shape_count += 1

  off_pad = new OffsetPad dia, drill+0.3
  off_pad.drill_off_dx = -0.5			# This param adjusts the drill offset
  off_pad.dx = 3.0
  off_pad.dy = 3.0
  off_pad.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  off_pad.y = current_row * d
  shape_count += 1

#Generic 0603 footprint - with keepout  docu and silkscreen layers
  smd = new Smd
  smd.dx = 1.1
  smd.dy = 1.0
  smd.x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  smd.y = current_row * d
  shape_count += 1
  l = rot_single [smd], 2, 1.7	# create rotated single list "l" of 2 pads, 1.7mm apart

  kx = 1.6
  ky = 0.75
  keepout1 = new Line 0.1
  keepout1.x1 = -kx
  keepout1.y1 = ky
  keepout1.x2 = kx
  keepout1.y2 = ky
  keepout1.type = 'keepout'
  keepout2 = new Line 0.1
  keepout2.x1 = kx
  keepout2.y1 = ky
  keepout2.x2 = kx
  keepout2.y2 = -ky
  keepout2.type = 'keepout'
  keepout3 = mirror_x clone keepout1
  keepout4 = mirror_y clone keepout2

# Tip:- demo of grouping like items, then processing group to change individual item properties
# instead of the '-> adjust... below you could change otehr properties, eg type (layer)
  keepout = [keepout1, keepout2, keepout3, keepout4]  # group in a list
  keepout = keepout.map ((o) -> adjust o, smd.x, smd.y)  # then process properties to adjust pos of ALL keepouts
			
  silk = clone_modl keepout, 'type', 'silk'	# no need adjust position- already cloned desired position

  docu1 = new Line 0.1
  docu1.x1 = -0.35
  docu1.y1 = 0.45
  docu1.x2 = 0.35
  docu1.y2 = 0.45
  docu1.type = 'docu'
  docu2 = mirror_x clone docu1
  docu3 = new Rect
  docu3.dx = 0.5
  docu3.dy = 1
  docu3.x = -0.6
  docu3.type = 'docu'
  docu4 = mirror_y clone docu3
  docu4.type = 'docu'


  docu = [docu1, docu2, docu3, docu4] # Note how several items "combined" into list
  docu = docu.map ((o) -> adjust o, smd.x, smd.y)  # then process properties to adjust pos of ALL 

  smd_all = [l, docu, keepout, silk]	   # this appears to work - but fails if used in "combine [smd_all]"
################################ END SMD 0603

# name = reference in Kicad 
  name = new Name -11
  name.value = "name: madparts sample shapes"

  value = new Value 21
  value.value = "value eg 10uF"


  label = new Label "This label points at a hole^, arc^"
  label.y = -7
  label.x = -5

# utility functions
#	=== Examples of this group already above! ===
# clone 				makes a deep copy of an item. 
# 				You need to take a clone if you want to base another shape on an existing shape.
# rotate90, rotate180, rotate270 		rotate a shape around the origin.
# rotate90pad, rotate180pad,rotate270pad	are the same, but they only work on pads and smds.
# mirror_y and mirror_x 			mirror a shape.
# adjust_x and adjust_y 			adjust x or y for a shape.
# single and single_rot 			generate a single line of vertical or horizontal pads in a list.


# lines 				creates a sequence of lines with a certain width.
  some_lines = lines w, [
    [-length/2,  length/3]
    [ length/2,  length/2]
    [ length/2, -length/2]
    [-length/2, -length/4]
    [-length/2,  length/3]
  ]
  some_lines_x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  some_lines_y = current_row * d
  shape_count += 1
  some_lines = some_lines.map ((o) -> adjust o, some_lines_x, some_lines_y)  # then process properties to adjust pos of ALL 


# silk_square 			draws a square of silk lines
  silk_sq = silk_square length/3, w
  silk_sq_x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  silk_sq_y = current_row * d
  shape_count += 1
  adjust silk_sq, silk_sq_x, silk_sq_y

# make_rect 			makes draws a simple rect based on dx, 
  m_r = make_rect dx, dy, w, 'docu'
  m_r_x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  m_r_y = current_row * d
  shape_count += 1
  adjust m_r, m_r_x, m_r_y

# dual, alt_dual, rot_dual and alt_rot_dual 	generate a dual line of vertical or horizontal pads in a list. the alt variants have alternating pad numbers.
  p = new Smd 
  p.dx = dx
  p.dy = dy
  p.ro = 100
  l1 = dual p, n, 2, e
  l1_x = d * ((shape_count % grid_size_x) + grid_x_offset)
  current_row += 1 if (shape_count % grid_size_x) == 0
  l1_y = current_row * d
  shape_count += 1
  adjust l1, l1_x, l1_y


# quad 	generates a quad layout list of pads.dy, line_width and type.
# See examples supplied for a lot more sild, docu, pin renumbering etc.....
  q_smd = new Smd
  q_smd.dx = 2
  q_smd.dy = 1
  qs = quad [q_smd], 16, 2, 10
  qs_x = d * ((shape_count % grid_size_x) + grid_x_offset) + 15
  current_row += 1 if (shape_count % grid_size_x) == 0
  qs_y = current_row * d
  shape_count += 1
  adjust qs, qs_x, qs_y


# remove 	allows removing a pad/smd from a list typically generated by one of the single, dual, ... methods above by name
  qs1 = clone qs
  qs1 = remove qs1, 5				# removed pad #5
  current_row += 1 if (shape_count % grid_size_x) == 0
  qs1_y = current_row * d - 30
  shape_count += 1
  adjust qs1, 0, qs1_y


# END utility functions



# Tip:- really a trick - pass a shape into label to sort of see it's properties!
# this shows as long line of text at bottom 
  lbl = new Label off_pad	# arc
  lbl.y = -15



# ONLY items in next line are displayed!
# everything Eagle supports
#  combine [rect, disc, circle, hole, vertex, arc, c, line, polygon, p2, p3, p4, p5, name, value, label, smd_pad, l,  docu, keepout, silk, r_pad, s_pad, l_pad, o_pad, off_pad, some_lines, silk_sq,   m_r, l1, qs, qs1, lbl ]

# everything Kicad supports (not octogon pad)
  combine [rect, disc, circle, hole, vertex, arc, c, line, polygon, p2, p3, p4, p5, name, value, label, smd_pad, l,  docu, keepout, silk, r_pad, s_pad, l_pad, off_pad, some_lines, silk_sq,   m_r, l1, qs, qs1] #, lbl ]
