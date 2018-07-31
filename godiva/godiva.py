#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 12:12:25 2017

@author: stu
"""

import openmc

pit = openmc.Material(name='pit')

aDensity49 = 3.7047e-2;
aDensity40 = 1.751e-3;
aDensity41 = 1.17e-4;
aDensityGa = 1.375e-3;
aDensityNi = 9.1322e-2;



aDensity_pit = aDensity49+aDensity40+aDensity41+aDensityGa;

pit.add_nuclide('Pu239',aDensity49/aDensity_pit)
pit.add_nuclide('Pu240',aDensity40/aDensity_pit)
pit.add_nuclide('Pu241',aDensity41/aDensity_pit)
pit.add_element('Ga',aDensityGa/aDensity_pit)
pit.set_density('atom/b-cm',aDensity_pit)


coat = openmc.Material(name='coat')
coat.add_element('Ni',1)
coat.set_density('atom/b-cm',aDensityNi)

# write the materials to file
mf = openmc.Materials((pit,coat))
mf.export_to_xml()

# create the geometry and cells
pit_or = openmc.Sphere(R=6.38493)
coat_or = openmc.Sphere(R=6.39763,boundary_type='vacuum')

pit_cell = openmc.Cell()
pit_cell.fill=pit
pit_cell.region = -pit_or

pit_cell.temperature=293.

coat_cell = openmc.Cell()
coat_cell.fill = coat
coat_cell.region = +pit_or & -coat_or

extern_cell = openmc.Cell()
extern_cell.fill = 'void'
extern_cell.region = +coat_or

root = openmc.Universe()
root.add_cells((pit_cell,coat_cell,extern_cell))

g = openmc.Geometry()
g.root_universe = root
g.export_to_xml()

p = openmc.Plot()
p.width = [10, 10]
p.color_by = 'material'
p.colors = {pit: 'salmon', coat: 'gray'}

#pf = openmc.Plots((p))
#pf.export_to_xml()
#openmc.plot_geometry()

# source and settings
point = openmc.stats.Point((0,0,0))
src = openmc.Source(space=point)
settings = openmc.Settings()
source_energy_dist = openmc.stats.Discrete(0.01,1.)
src.energy = source_energy_dist
settings.source = src
settings.batches = 700
settings.inactive = 50
settings.particles = 15000
settings.export_to_xml()

# no tallies for now...

openmc.run()