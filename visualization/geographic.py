import fiona
from shapely.geometry import Polygon
import geopandas as gpd


def make_kml_file(region):
    """
    Create a KML file for a given region.
    The KML file is a simple polygon representing the boundary of the region.


    Args:
    -----
    region: object
     An object representing the region for which to create the KML file. It should have a rectangle
     attribute, which is a tuple (xmin, xmax, ymin, ymax) specifying the bounds of the region.

    Returns:
    --------
    None
    """
    # make kml file
    rectx = [
        region.rectangle[2],
        region.rectangle[3],
        region.rectangle[3],
        region.rectangle[2],
        region.rectangle[2],
    ]
    recty = [
        region.rectangle[1],
        region.rectangle[1],
        region.rectangle[0],
        region.rectangle[0],
        region.rectangle[1],
    ]
    rect_coords = list(zip(recty, rectx))
    rect_geom = Polygon(rect_coords)
    rect_gdf = gpd.GeoDataFrame(index=[0], crs="epsg:2056", geometry=[rect_geom])
    fiona.supported_drivers["KML"] = "rw"
    rect_gdf.to_file(region.bname['eventCodeName'] + ".kml", driver="KML")