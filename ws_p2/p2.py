#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 10:35:31 2017

@author: stu
"""

import openmc

# materials
uo2 = openmc.Material(name='uo2')
uo2.add_element('U',1.0,enrichment=3.0)
uo2.add_nuclide('O16',2.0)
uo2.set_density('g/cm3',10.0)

zirconium = openmc.Material(name='zirconium')
zirconium.add_element('Zr',1.0)
zirconium.set_density('g/cm3',6.55)

water = openmc.Material(name='water')
water.add_nuclide('H1',2)
water.add_nuclide('O16',1)
water.set_density('g/cm3',0.701)
water.add_s_alpha_beta('c_H_in_H2O')

pyrex = openmc.Material(name='pyrex')
pyrex.add_element('B',0.49)
pyrex.add_element('O',4.7)
pyrex.add_element('Al',0.17)
pyrex.add_element('Si',1.8)
pyrex.set_density('g/cm3',2.26)

mf = openmc.Materials((uo2,zirconium,water,pyrex))
mf.export_to_xml()

# color stuff
colors = {}
colors[water] = (100, 200, 200)
colors[zirconium] = (150, 150, 150)
colors[pyrex] = (100, 255, 100)
colors[uo2] = (255, 50, 50)

#fuel pin

pitch = 1.26
fuel_or = openmc.ZCylinder(R=0.39)
clad_ir = openmc.ZCylinder(R=0.40)
clad_or = openmc.ZCylinder(R=0.46)

fuel = openmc.Cell(1,'fuel')
fuel.fill = uo2
fuel.region = -fuel_or

gap = openmc.Cell(2,'air gap')
gap.fill = 'void'
gap.region = +fuel_or & -clad_ir

clad = openmc.Cell(3,'clad')
clad.fill = zirconium
clad.region = +clad_ir & -clad_or

moderator = openmc.Cell(4,'moderator')
moderator.fill = water
moderator.region = +clad_or

fuel_pin = openmc.Universe();
fuel_pin.add_cells((fuel,gap,clad,moderator))

main = openmc.Cell()
main.fill = fuel_pin

root = openmc.Universe()
root.add_cell(main)

g = openmc.Geometry()
g.root_universe=root
g.export_to_xml()

# guide tube
clad_ir = openmc.ZCylinder(R=0.56)
clad_or = openmc.ZCylinder(R=0.60)

inner = openmc.Cell()
inner.fill=water
inner.region = -clad_ir

clad = openmc.Cell()
clad.fill = zirconium
clad.region = +clad_ir & -clad_or

outer = openmc.Cell()
outer.fill = water
outer.region = +clad_or

guide_tube = openmc.Universe()
guide_tube.add_cells((inner,clad,outer))

main = openmc.Cell()
main.fill = guide_tube
root = openmc.Universe()
root.add_cell(main)
g = openmc.Geometry()
g.root_universe = root
g.export_to_xml()

# pyrex tube 
# Define the cylinders which bound each radial zone.
radii = [0.21, 0.23, 0.24, 0.43, 0.44, 0.48, 0.56, 0.60]
cyls = [openmc.ZCylinder(R=R) for R in radii]

# Initialize a list of cells.
bp_cells = []

# Define the inner void zone first.
c = openmc.Cell()
c.region = -cyls[0]
c.fill = 'void'
bp_cells.append(c)

# Now all the sandwiched layers.
mats = [zirconium, 'void', pyrex, 'void', zirconium, water, zirconium]
for i in range(len(mats)):
    c = openmc.Cell()
    c.region = +cyls[i] & -cyls[i+1]
    c.fill = mats[i]
    bp_cells.append(c)

# And the outer moderator region.
c = openmc.Cell()
c.region = +cyls[-1]
c.fill = water
bp_cells.append(c)

# Make a universe containing these cells
burn = openmc.Universe()
burn.add_cells(bp_cells)

main = openmc.Cell()
main.fill = burn

root = openmc.Universe()
root.add_cell(main)

g = openmc.Geometry()
g.root_universe = root
g.export_to_xml()

# moderator universe
moderator = openmc.Cell()
moderator.fill = water
all_water = openmc.Universe()
all_water.add_cell(moderator)

lattice = openmc.RectLattice()

lattice.dimension = [9, 9]
lattice.pitch = [pitch]*2
lattice.outer = all_water

# I want (x0, y0) = (0, 0) to be the center of the instrument tube so that means
# the lower-left will be -half a pin pitch in x and y.
lattice.lower_left = [-pitch/2.0]*2

# Most of the lattice positions are fuel pins so rather than type all of those
# out, I will use a Python list comprehension to start with a 9x9 array of fuel.
lattice.universes = [[fuel_pin for i in range(9)] for j in range(9)]

# Then I will replace some fuel pins with guide tubes.  First index is the row,
# starting from the top, and the second is the column (like a matrix).
lattice.universes[2][0] = guide_tube
lattice.universes[2][3] = guide_tube
lattice.universes[5][0] = guide_tube
lattice.universes[5][3] = guide_tube
lattice.universes[5][6] = guide_tube
lattice.universes[8][0] = guide_tube
lattice.universes[8][3] = guide_tube
lattice.universes[8][6] = guide_tube

# And the burnable poison rod.
#lattice.universes[3][5] = burn
lattice.universes[2][6] = burn

height = 100
assembly_pitch = 21.5
x0 = openmc.XPlane(x0=0.0,boundary_type='reflective')
x1 = openmc.XPlane(x0=assembly_pitch/2.0, boundary_type='reflective')
y0 = openmc.YPlane(y0=0.0,boundary_type='reflective')
y1 = openmc.YPlane(y0=assembly_pitch/2.0,boundary_type='reflective')
z0 = openmc.ZPlane(z0=-height/2.0, boundary_type='reflective')
z1 = openmc.ZPlane(z0=height/2.0,boundary_type='reflective')

main = openmc.Cell()
main.region = +x0 & -x1 & +y0 & -y1 & +z0 & -z1
main.fill = lattice

root = openmc.Universe()
root.add_cell(main)

g = openmc.Geometry()
g.root_universe = root
g.export_to_xml()

settings = openmc.Settings()
settings.source = openmc.Source(space=openmc.stats.Box((0.1,0.1,0),(0.49*assembly_pitch,0.49*assembly_pitch,0)))
settings.batches = 50
settings.inactive = 10
settings.particles = 1000
settings.export_to_xml()

# tallies
tallies = openmc.Tallies()
mesh = openmc.Mesh()
mesh.dimension = [3,3]
mesh.lower_left = lattice.lower_left
mesh.width = lattice.pitch

mesh_filt = openmc.MeshFilter(mesh)
t = openmc.Tally(1)
t.filters = [mesh_filt]
t.scores = ['total','fission']
t.nuclides = ['total','U235']
tallies.append(t)

dist_filt = openmc.DistribcellFilter(fuel.id)
t = openmc.Tally(2)
t.filters = [dist_filt]
t.scores = ['total','fission']
t.nuclides = ['total','U235']
tallies.append(t)
tallies.export_to_xml()


openmc.run()

