# Imports
import matplotlib.pyplot as plt
import geopandas as gpd
import pysal as ps
#from pysal.contrib.viz import mapping as maps

# paths
lcp_dir = r'C:\Users\Christian\Dropbox\Uddannelse\DTU\Diverse\Python\Geographic Data Science\Lecture 3\Liverpool'
los_dir = r'C:\Users\Christian\Dropbox\Uddannelse\DTU\Diverse\Python\Geographic Data Science\Lecture 3\E08000012'

# 1.1
lsoas_link = lcp_dir + '/shapefiles/Liverpool_lsoa11.shp'
lsoas = gpd.read_file(lsoas_link)
#print(lsoas.head())
#lsoas.plot()
rwy_tun = gpd.read_file(los_dir + '/RailwayTunnel.shp')
rwy_tun = rwy_tun.set_index('id')
#print(rwy_tun.info())
#rwy_tun.plot()

namp = gpd.read_file(los_dir + '/NamedPlace.shp')
#namp.plot()

f, ax = plt.subplots(1)
gpd.plotting.plot_polygon_collection(ax, lsoas, linewidth=0.1, edgecolor='grey')


plt.show()
