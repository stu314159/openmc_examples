#!/home/stu/anaconda2/bin/python

import openmc

# initially, no materials
mf = openmc.Materials([])
mf.export_to_xml()

sph1 = openmc.Sphere(R=1000.0,boundary_type='vacuum')

sph_inside = -sph1;
sph_outside = +sph1;

c1 = openmc.Cell(name='inside')
c1.fill = 'void'
c1.region = sph_inside

c2 = openmc.Cell(name='outside')
c2.fill = 'void'
c2.region = sph_outside

root = openmc.Universe()
root.add_cells((c1,c2))
g = openmc.Geometry()
g.root_universe = root
g.export_to_xml()

point = openmc.stats.Point((0.,0.,0.))
src = openmc.Source(space=point)

settings = openmc.Settings()
settings.source =src
settings.batches = 100
settings.inactive = 0
settings.particles = 1000
settings.export_to_xml()

t = openmc.Tally(name='surface fluence')
#surf_filter = openmc.SurfaceFilter(sph1.id) #<-- not yet supported?
s_filter = openmc.CellFilter()
t.filters=[surf_filter]
t.scores=['flux']
tallies = openmc.Tallies([t])
tallies.export_to_xml()

openmc.run()