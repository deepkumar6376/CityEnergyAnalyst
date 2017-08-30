from __future__ import division

import geopandas as gpd

# sources:
# https://automating-gis-processes.github.io/2016/Lesson2-geopandas-basics.html
# http://www.qgistutorials.com/en/docs/find_neighbor_polygons.html

# file path
fp = "C:/reference-case-open/baseline/inputs/building-geometry/zone.shp"
fp2 = "C:/cea-reference-case/reference-case-zug/baseline/inputs/building-geometry/zone.shp"

# read file
data = gpd.read_file(fp2)

# display file type
type(data)

# display data
p1 = data.plot()

data.set_index('Name',inplace=True)

# display data
data.envelope.plot()

for name in data.index:
    # print row.geometry
    # print data.geometry
   building_footprint = data.iloc[0]

  #  print data.loc[name]
  #  print type(building_footprint)

  #  print data.loc[name].geometry.distance(data)

