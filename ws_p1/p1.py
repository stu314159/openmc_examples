#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 09:43:36 2017
@author: stu
"""

import openmc

# define the model materials

# define fuel: 3% (atom percent) enriched UO2
uo2 = openmc.Material()
uo2.add_nuclide('U235',0.03)
uo2.add_nuclide('U238',0.97)
uo2.add_element('O',2.0)
uo2.set_density('g/cm3',10.0)

# define zirconium
zirconium = openmc.Material()
zirconium.add_element('Zr',1.0)
zirconium.set_density('g/cm3',6.6)

# define water
water = openmc.Material()
water.add_element('H',2.0)
water.add_element('O',1.0)
water.set_density('g/cm3',0.7)
water.add_s_alpha_beta('c_H_in_H2O')

mf = openmc.Materials((uo2,zirconium,water))
mf.export_to_xml()

# define the geometry
# start by defining surfaces
# fuel and clad system
fuel_or = openmc.ZCylinder(R=0.39)
clad_ir = openmc.ZCylinder(R=0.40)
clad_or = openmc.ZCylinder(R=0.46)

# pin-cell
pitch = 1.26
left = openmc.XPlane(x0=-pitch/2.,boundary_type='reflective')
right = openmc.XPlane(x0=pitch/2.,boundary_type='reflective')
bottom = openmc.YPlane(y0=-pitch/2.,boundary_type='reflective')
top = openmc.YPlane(y0=pitch/2.,boundary_type='reflective')

# make regions from surfaces and their sense.  Kind of like cells in MCNP.
fuel_region = -fuel_or
gap_region = +fuel_or & -clad_ir
clad_region = +clad_ir & -clad_or
water_region = +left & -right & +bottom & -top & +clad_or

fuel = openmc.Cell()
fuel.fill = uo2
fuel.region = fuel_region

gap = openmc.Cell()
gap.fill = 'void'
gap.region = gap_region

clad = openmc.Cell()
clad.fill = zirconium
clad.region = clad_region

moderator = openmc.Cell()
moderator.fill = water
moderator.region = water_region

# openmc universe stuff.  Think about this
root = openmc.Universe()
root.add_cells((fuel,gap,clad,moderator))

g = openmc.Geometry()
g.root_universe = root
g.export_to_xml()


# need to work through questions on the plotting (without using Jupyter)
#p = openmc.Plot()
#p.width = [pitch,pitch]
#p.pixels = [400,400]
#p.color_by = 'material'
#p.colors = {uo2:'salmon', water:'cyan', zirconium:'gray'}
#
#plts = openmc.Plots(p)
#plts.export_to_xml()
#openmc.plot_geometry()

# starting source and settings
point = openmc.stats.Point((0,0,0))
src = openmc.Source(space=point)
settings = openmc.Settings()
settings.source = src
settings.batches = 100
settings.inactive = 10
settings.particles = 1000
settings.export_to_xml()

# tallies
t = openmc.Tally(name='fuel tally')
cell_filter = openmc.CellFilter(fuel.id)
t.filters = [cell_filter]
t.nuclides = ['U235']
t.scores = ['total','fission','absorption','(n,gamma)']

tallies = openmc.Tallies([t])
tallies.export_to_xml()

openmc.run()
