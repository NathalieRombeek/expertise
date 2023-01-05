"""
Set of definitions regarding shape files for plotting and MeteoSwiss radars
"""
import shapefile as shp
import rasterio

###############
# RADARS
###############
albis = {'name': 'Albis', 'code': 'A', 'chx': 2681201, 'chy': 1237604, 'height': 938}
dole = {'name': 'La Dôle', 'code':  'D', 'chx': 2497057, 'chy': 1142408, 'height': 1682}
lema = {'name': 'Monte Lema', 'code': 'L', 'chx': 2707957, 'chy': 1099762, 'height': 1626}
weissfluhgipfel = {'name': 'Weissfluhgipfel', 'code': 'W', 'chx': 2779700, 'chy': 1189790, 'height': 2850}
plainemorte = {'name': 'Pointe de la Plaine Morte', 'code': 'P', 'chx': 2603687, 'chy': 1135476, 'height': 2937}

RADARS = [albis, dole, lema, weissfluhgipfel, plainemorte]
ELEVATIONS = [-0.2, 0.4, 1, 1.6, 2.5, 3.5, 4.5, 5.5, 6.5,
     7.5, 8.5, 9.5, 11, 13, 16, 20, 25, 30, 35, 40]

###############
# SHAPEFILES
###############

# directories
terrainBgFile = "/scratch/nrombeek/expertise/shapes/ch_n30e000.tif"
demFile = "/scratch/nrombeek/expertise/shapes/swisstopo_DHM25_MONA_DTED_lv95.tif"

# read raster files
TERRAINBG = rasterio.open(terrainBgFile)
DEM = rasterio.open(demFile)
TERRAIN = DEM.read(1)
TERRAIN[TERRAIN == TERRAIN.min()] = 0

# read shape files
SF = shp.Reader("/scratch/nrombeek/expertise/shapes/swiss.shp")
RIVERS = shp.Reader("/scratch/nrombeek/expertise/shapes/r1.shp")
CHLAKES = shp.Reader("/scratch/nrombeek/expertise/shapes/chlakes.shp")
