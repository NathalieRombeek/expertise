"""
Methods for visualizing data
"""
from datetime import datetime
import numpy as np
import os
from os.path import exists
import matplotlib.pyplot as plt
import subprocess
import shapefile as shp
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as mcolors
import matplotlib
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle

matplotlib.use("Agg")  # to plot without X window
from shapely.geometry import Polygon

from common import constants
from visualization.utils import find_nearest, plotShapefile


dem = constants.DEM
sf = constants.SF
rivers = constants.RIVERS
chlakes = constants.CHLAKES
terrain = constants.TERRAIN
terrainBg = constants.TERRAINBG

COLOURS_AVG = [
    "#00000088",
    "#FFFFFFFF",
    "#D3EBFFFF",
    "#E9D7F3FF",
    "#9D7F95FF",
    "#650165FF",
    "#AF01AFFF",
    "#3232C8FF",
    "#0064FFFF",
    "#009696FF",
    "#00C832FF",
    "#64FF00FF",
    "#96FF00FF",
    "#C8FF32FF",
    "#FFFF00FF",
    "#FFC800FF",
    "#FFA000FF",
    "#FF7D00FF",
    "#E11901FF",
]
COLOURS_SUM = [
    "#000000FF",
    "#FFFFFFFF",
    "#E9D7F3FF",
    "#9D7F95FF",
    "#650165FF",
    "#AC02ACFF",
    "#3232C8FF",
    "#0064FFFF",
    "#009696FF",
    "#00C832FF",
    "#64FF00FF",
    "#96FF00FF",
    "#C8FF32FF",
    "#FFFF00FF",
    "#FFC800FF",
    "#FFA000FF",
    "#FF7D00FF",
    "#E11901FF",
    "#C10101FF",
    "#9F0101FF",
]
BOUNDS_AVG = [
    -9999,
    -0.1,
    0.01,
    0.08,
    0.16,
    0.25,
    0.4,
    0.63,
    1.0,
    1.6,
    2.5,
    4.0,
    6.3,
    10,
    16,
    25,
    40,
    63,
    100,
    999,
]
TICKLABELS_AVG = [
    "NA",
    "0",
    "wet",
    "0.08",
    "0.16",
    "0.25",
    "0.40",
    "0.63",
    "1.0",
    "1.6",
    "2.5",
    "4.0",
    "6.3",
    "10",
    "16",
    "25",
    "40",
    "63",
    "100",
    "",
]

matplotlib.rc("xtick", labelsize=14)
matplotlib.rc("ytick", labelsize=14)


def make_avg_zoom(region, outDir, useOsm=False):
    cmap, norm = _get_colours(COLOURS_AVG, BOUNDS_AVG)
    bname = region.bname
    fname = region.fbname
    if useOsm:
        import osmnx as ox
    if useOsm and exists("osmdata_water.shp"):
        osm_water_lv95 = shp.Reader("osmdata_water.shp")

    outFile = outDir + "/" + bname["eventCodeName"] + "-avg-zoom.png"

    fig, ax = plt.subplots(figsize=(20, 20))
    cs = plt.imshow(
        terrain,
        extent=[dem.bounds[0], dem.bounds[2], dem.bounds[1], dem.bounds[3]],
        cmap="gray",
    )
    plt.imshow(
        region.totalSum / region.totalDomain.shape[2],
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
        extent=[2255000, 2965000, 840000, 1480000],
    )
    ax.set_title(
        "Average precipitation intensity over "
        + region.name
        + " ["
        + str(int(region.surfacekm2))
        + " km\u00b2]\nfrom: "
        + bname["time"].strftime("%d/%m/%Y")
        + " "
        + bname["hour"]
        + ":"
        + bname["minute"]
        + "UTC to: "
        + fname["time"].strftime("%d/%m/%Y")
        + " "
        + fname["hour"]
        + ":"
        + fname["minute"]
        + "UTC, product = "
        + bname["prd"],
        fontsize=26,
    )
    plt.plot()
    ax.set_aspect("equal")
    plt.xlabel("\nSwiss W-E", fontsize=20)
    plt.ylabel("Swiss S-N\n", fontsize=20)
    plt.yticks(rotation=90, va="center")

    for shape in sf.shapeRecords():
        plotShapefile(shape.shape, "white", linewidth=2.0, ax=ax)

    if useOsm and exists("osmdata_water.shp"):
        osm_water_lv95 = shp.Reader("osmdata_water.shp")
        for shape in osm_water_lv95.shapes():
            plotShapefile(shape, "blue", ax=ax)
    else:
        for shape in rivers.shapes():
            plotShapefile(shape, "blue", ax=ax)
        for shape in chlakes.shapes():
            plotShapefile(shape, "blue", ax=ax)

    ax.set_xlim(region.rectangle[0] - region.delta, region.rectangle[1] + region.delta)
    ax.set_ylim(region.rectangle[2] - region.delta, region.rectangle[3] + region.delta)

    ax.add_patch(
        Rectangle(
            (region.rectangle[0], region.rectangle[2]),
            region.rectangle[1] - region.rectangle[0],
            region.rectangle[3] - region.rectangle[2],
            edgecolor="black",
            fill=False,
            lw=1,
        )
    )

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.5)
    cbar = plt.colorbar(boundaries=BOUNDS_AVG, ticks=BOUNDS_AVG, cax=cax, extend="max")
    cbar.ax.set_yticklabels(TICKLABELS_AVG)
    if bname["prd"] == "AQC":
        cbar.ax.set_title("[mm / 5 min]", fontsize=16)
    else:
        cbar.ax.set_title("[mm/h]", fontsize=16)
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.tick_params(labelsize=16)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(size=0, labelsize=16)
    ax.ticklabel_format(style="plain")
    fig.savefig(outFile)
    plt.close(fig)
    subprocess.call(
        "mogrify -fuzz 25% -trim -border 25 -bordercolor white +repage " + outFile,
        shell=True,
    )


def make_sum_zoom(region, outDir, useOsm=False, unit="mm", **rg_kwargs):
    cmap16, norm = _get_colours(COLOURS_SUM)
    bounds, ticklabels = _get_tick_bounds()
    bname = region.bname
    fname = region.fbname

    if useOsm:
        import osmnx as ox
    if useOsm and exists("osmdata_water.shp"):
        osm_water_lv95 = shp.Reader("osmdata_water.shp")

    outFile = outDir + "/" + bname["eventCodeName"] + "-sum-zoom.png"
    fig, ax = plt.subplots(figsize=(20, 20))
    cs = plt.imshow(
        terrain,
        extent=[dem.bounds[0], dem.bounds[2], dem.bounds[1], dem.bounds[3]],
        cmap="gray",
    )
    plt.imshow(
        region.totalSum,
        cmap=cmap16,
        norm=norm,
        interpolation="nearest",
        extent=[2255000, 2965000, 840000, 1480000],
    )
    ax.set_title(
        "Total precipitation sum over "
        + region.name
        + " ["
        + str(int(region.surfacekm2))
        + " km\u00b2]\nfrom: "
        + bname["time"].strftime("%d/%m/%Y")
        + " "
        + bname["hour"]
        + ":"
        + bname["minute"]
        + "UTC to: "
        + fname["time"].strftime("%d/%m/%Y")
        + " "
        + fname["hour"]
        + ":"
        + fname["minute"]
        + "UTC, product = "
        + bname["prd"],
        fontsize=26,
    )
    plt.plot()
    ax.set_aspect("equal")
    plt.xlabel("\nSwiss W-E", fontsize=20)
    plt.ylabel("Swiss S-N\n", fontsize=20)
    plt.yticks(rotation=90, va="center")

    for shape in sf.shapeRecords():
        plotShapefile(shape.shape, "white", linewidth=2.0, ax=ax)

    if useOsm and exists("osmdata_water.shp"):
        osm_water_lv95 = shp.Reader("osmdata_water.shp")
        for shape in osm_water_lv95.shapes():
            plotShapefile(shape, "blue", ax=ax)
    else:
        for shape in rivers.shapes():
            plotShapefile(shape, "blue", ax=ax)
        for shape in chlakes.shapes():
            plotShapefile(shape, "blue", ax=ax)

    ax.set_xlim(region.rectangle[0] - region.delta, region.rectangle[1] + region.delta)
    ax.set_ylim(region.rectangle[2] - region.delta, region.rectangle[3] + region.delta)

    ax.add_patch(
        Rectangle(
            (region.rectangle[0], region.rectangle[2]),
            region.rectangle[1] - region.rectangle[0],
            region.rectangle[3] - region.rectangle[2],
            edgecolor="black",
            fill=False,
            lw=1,
        )
    )
    if "rain_gauges" in rg_kwargs.keys():
        rain_gauges = rg_kwargs["rain_gauges"]
        for rain_gauge in rain_gauges:
            idx_col = find_nearest(BOUNDS_AVG, rain_gauge["depth"])
            rg_col = COLOURS_AVG[idx_col]
            ax.scatter(
                rain_gauge["chx"],
                rain_gauge["chy"],
                marker="o",
                color=rg_col,
                s=460,
                linewidth=1.5,
                edgecolors="k",
            )
            ax.annotate(
                rain_gauge["label"],
                xy=(rain_gauge["chx"], rain_gauge["chy"] + 500),
                fontsize=18,
                color="white",
                path_effects=[pe.withStroke(linewidth=2, foreground="black")],
                fontweight="bold",
            )

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.5)
    cbar = plt.colorbar(
        boundaries=bounds, ticks=bounds, drawedges=False, cax=cax, extend="max"
    )
    cbar.ax.set_yticklabels(ticklabels)
    ax.ticklabel_format(useOffset=False, style="plain")
    cbar.ax.set_title(unit, fontsize=16)
    ax.tick_params(labelsize=16)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(size=0, labelsize=16)
    ax.ticklabel_format(style="plain")
    fig.savefig(outFile)
    plt.close(fig)
    subprocess.call(
        "mogrify -fuzz 25% -trim -border 25 -bordercolor white +repage " + outFile,
        shell=True,
    )


def make_sum(region, outDir, unit="mm"):
    cmap16, norm = _get_colours(COLOURS_SUM)
    bounds, ticklabels = _get_tick_bounds()
    bname = region.bname
    fname = region.fbname

    outFile = outDir + "/" + bname["eventCodeName"] + "-sum.png"

    fig, ax = plt.subplots(figsize=(20, 20))
    cs = plt.imshow(
        terrainBg.read(1),
        extent=[
            terrainBg.bounds[0],
            terrainBg.bounds[2],
            terrainBg.bounds[1],
            terrainBg.bounds[3],
        ],
        cmap="gray",
    )
    plt.imshow(
        region.totalSum,
        cmap=cmap16,
        norm=norm,
        interpolation="nearest",
        extent=[2255000, 2965000, 840000, 1480000],
    )
    ax.set_xlim([2255000, 2965000])
    ax.set_ylim([840000, 1480000])
    ax.set_title(
        "Total precipitation sum over Swiss radar domain "
        + "\nfrom: "
        + bname["time"].strftime("%d/%m/%Y")
        + " "
        + bname["hour"]
        + ":"
        + bname["minute"]
        + "UTC to: "
        + fname["time"].strftime("%d/%m/%Y")
        + " "
        + fname["hour"]
        + ":"
        + fname["minute"]
        + "UTC",
        fontsize=26,
    )
    ax.set_aspect("equal")
    plt.plot()
    plt.xlabel("\nSwiss W-E", fontsize=20)
    plt.ylabel("Swiss S-N\n", fontsize=20)
    plt.yticks(rotation=90, va="center")

    for shape in rivers.shapes():
        plotShapefile(shape, "blue", ax=ax)
    for shape in chlakes.shapes():
        plotShapefile(shape, "blue", ax=ax)

    for shape in sf.shapeRecords():
        plotShapefile(shape.shape, "white", linewidth=2.0, ax=ax)

    ax.add_patch(
        Rectangle(
            (region.rectangle[0], region.rectangle[2]),
            region.rectangle[1] - region.rectangle[0],
            region.rectangle[3] - region.rectangle[2],
            edgecolor="black",
            fill=False,
            lw=1,
        )
    )
    ax.axhline(
        y=region.rectangle[2] + (region.rectangle[3] - region.rectangle[2]) / 2.0,
        color="k",
        linewidth=2,
    )
    ax.axvline(
        x=region.rectangle[0] + (region.rectangle[1] - region.rectangle[0]) / 2.0,
        color="k",
        linewidth=2,
    )
    ax.ticklabel_format(style="plain")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.5)
    cbar = plt.colorbar(
        boundaries=bounds, ticks=bounds, drawedges=False, cax=cax, extend="max"
    )
    cbar.ax.set_yticklabels(ticklabels)
    ax.ticklabel_format(useOffset=False, style="plain")
    cbar.ax.set_title(unit, fontsize=16)
    ax.tick_params(labelsize=16)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(size=0, labelsize=16)
    fig.savefig(outFile)
    plt.close(fig)
    subprocess.call(
        "mogrify -fuzz 25% -trim -border 25 -bordercolor white +repage " + outFile,
        shell=True,
    )


def processAllFiles(region, allFiles, outDir, useOsmSingleFiles=False):
    for i in range(0, len(allFiles)):
        processSingleFile(region, allFiles, i, outDir, useOsmSingleFiles)


def processSingleFile(region, allFiles, i, outDir, useOsmSingleFiles=False):
    cmap, norm = _get_colours(COLOURS_AVG, bounds=BOUNDS_AVG)

    if not os.path.isdir(outDir + "/single-plots"):
        os.makedirs(outDir + "/single-plots")

    filename = allFiles[i]
    bname = filename.split(os.path.sep)[-1].split(os.path.sep)[-1]
    outFile = None
    if bname[len(bname) - 4 :] == ".gif":
        outFile = outDir + "/single-plots/" + bname[:-4] + ".png"
    elif bname[len(bname) - 3 :] == ".h5":
        outFile = outDir + "/single-plots/" + bname[:-3] + ".png"
    rain = region.totalDomain[:, :, i]

    fig, ax = plt.subplots(figsize=(20, 20))
    # ax.set_rasterized(True)
    # plt.imshow(terrain, extent=[2255000, 2965000, 840000, 1480000], cmap='gray', vmin=0, vmax=terrain.max())
    plt.imshow(
        terrain,
        extent=[dem.bounds[0], dem.bounds[2], dem.bounds[1], dem.bounds[3]],
        cmap="gray",
    )
    plt.imshow(
        rain,
        extent=[2255000, 2965000, 840000, 1480000],
        interpolation="none",
        cmap=cmap,
        aspect="auto",
        norm=norm,
    )
    ax.set_aspect("equal")
    ax.tick_params(labelsize=10)
    # font = {"family": "sans-serif", "weight": "normal", "size": 13}
    # matplotlib.rc('font', **font)
    plt.plot()

    prd = bname[:3]
    year = "20" + bname[3:5]
    day = bname[5:8]
    hour = bname[8:10]
    minute = bname[10:12]
    time = datetime.strptime(year + " " + day, "%Y %j")
    plt.title(
        "Precipitation intensity over "
        + region.name
        + ", "
        + time.strftime("%d/%m/%Y")
        + " "
        + hour
        + ":"
        + minute
        + "UTC, product = "
        + prd,
        y=1.02,
        fontsize=26,
    )

    # add rectangle to plot
    ax.add_patch(
        Rectangle(
            (region.rectangle[0], region.rectangle[2]),
            region.rectangle[1] - region.rectangle[0],
            region.rectangle[3] - region.rectangle[2],
            edgecolor="black",
            fill=False,
            lw=1,
        )
    )

    ax.ticklabel_format(style="plain")
    ax.set_xlim(region.rectangle[0] - region.delta, region.rectangle[1] + region.delta)
    ax.set_ylim(region.rectangle[2] - region.delta, region.rectangle[3] + region.delta)
    plt.xlabel("\nSwiss W-E", fontsize=18)
    plt.ylabel("Swiss S-N\n", fontsize=18)
    plt.yticks(rotation=90, va="center")

    if useOsmSingleFiles:
        if exists("osmdata_water.shp"):
            osm_water_lv95 = shp.Reader("osmdata_water.shp")
        for shape in osm_water_lv95.shapes():
            plotShapefile(shape, "blue", ax=ax)
    else:
        for shape in rivers.shapes():
            plotShapefile(shape, "blue", ax=ax)
    for shape in chlakes.shapes():
        plotShapefile(shape, "blue", ax=ax)

    for shape in sf.shapeRecords():
        plotShapefile(shape.shape, "white", linewidth=2.0, ax=ax)

    plt.plot()

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.5)

    cbar = plt.colorbar(boundaries=BOUNDS_AVG, ticks=BOUNDS_AVG, cax=cax, extend="max")
    cbar.ax.set_yticklabels(TICKLABELS_AVG)
    if prd == "AQC":
        cbar.ax.set_title("[mm / 5 min]", fontsize=20)
    else:
        cbar.ax.set_title("[mm/h]", fontsize=20)
    ax.tick_params(labelsize=16)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(size=0, labelsize=16)
    plt.savefig(outFile)
    plt.close(fig)
    subprocess.call(
        "mogrify -fuzz 25% -trim -border 25 -bordercolor white +repage " + outFile,
        shell=True,
    )
    print("Written: " + outFile)

    if not os.path.isdir(outDir + "/CSV"):
        os.makedirs(outDir + "/CSV")

    outFile = outDir + "/CSV/" + bname + ".csv"


def make_roiMap(region, outDir):
    import osmnx as ox
    from pyproj import Transformer
    import math
    import rasterio

    # inProj = Proj(init="epsg:2056")  # Swiss LV95
    # outProj = Proj(init="epsg:4326")  # lon lat
    dst_crs = "epsg:4326"  # lon lat
    # convert coordinates
    # x1, y1 = region.rectangle[0], region.rectangle[2]
    transformer = Transformer.from_crs("epsg:2056", "epsg:4326")
    lat1, lon1 = transformer.transform(region.rectangle[0], region.rectangle[2])
    lat2, lon2 = transformer.transform(region.rectangle[1], region.rectangle[3])

    # Bounding box
    bN, bS, bE, bW = lat2, lat1, lon2, lon1
    ox.config(use_cache=True, log_console=True)
    G_water = ox.geometries.geometries_from_bbox(
        bN + 0.1, bS - 0.1, bE + 0.1, bW - 0.1, tags={"natural": "water"}
    )
    G1_streets = ox.graph.graph_from_bbox(
        bN + 0.1,
        bS - 0.1,
        bE + 0.1,
        bW - 0.1,
        simplify=False,
        retain_all=True,
        truncate_by_edge=True,
        clean_periphery=True,
        custom_filter='["highway"~"primary|secondary"]',
    )
    G2_water = ox.graph.graph_from_bbox(
        bN + 0.1,
        bS - 0.1,
        bE + 0.1,
        bW - 0.1,
        simplify=False,
        retain_all=True,
        truncate_by_edge=True,
        clean_periphery=True,
        custom_filter='["waterway"~"river|stream"]',
    )
    G1_projected_streets = ox.project_graph(G1_streets, to_crs={"init": "epsg:4326"})
    G2_projected_water = ox.project_graph(G2_water, to_crs={"init": "epsg:4326"})

    G_water = G_water.to_crs("epsg:4326")
    # Plot
    outFile = outDir + "/" + region.file_info["eventCodeName"] + "-roimap.png"
    fig, ax = plt.subplots(figsize=(20, 20))
    ax.set_title(
        "Overview of region "
        + region.name
        + "\n[lon/lat coordinates] - Source: www.openstreetmap.org",
        fontsize=26,
    )

    if not os.path.isfile("/tmp/RGB.byte.wgs84_zero.tif"):
        from rasterio.warp import calculate_default_transform, reproject, Resampling

        transform, width, height = calculate_default_transform(
            dem.crs, dst_crs, dem.width, dem.height, *dem.bounds
        )
        kwargs = src.meta.copy()
        kwargs.update(
            {
                "crs": dst_crs,
                "transform": transform,
                "width": width,
                "height": height,
            }
        )

        with rasterio.open("/tmp/RGB.byte.wgs84.tif", "w", **kwargs) as dst:
            for i in range(1, dem.count + 1):
                reproject(
                    source=rasterio.band(dem, i),
                    destination=rasterio.band(dst, i),
                    src_transform=dem.transform,
                    src_crs=dem.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest,
                )

        rast = rasterio.open("/tmp/RGB.byte.wgs84.tif")
        meta = rast.meta
        bands = [x + 1 for x in list(range(rast.count))]
        rast.close()
        databands = [1]

        with rasterio.open("/tmp/RGB.byte.wgs84_zero.tif", "w", **meta) as dst:
            with rasterio.open("/tmp/RGB.byte.wgs84.tif") as src:
                for ID, b in enumerate(bands, 1):
                    if b in databands:
                        data = src.read(b)
                        data[data < 0] = 0
                        dst.write(data, ID)
                    else:
                        data = src.read(b)
                        dst.write(data, ID)
        os.remove("/tmp/RGB.byte.wgs84.tif")
        dst.close
    dem_lonlat = rasterio.open("/tmp/RGB.byte.wgs84_zero.tif")
    terrain_lonlat = dem_lonlat.read(1)
    terrain_lonlat[terrain_lonlat == terrain_lonlat.min()] = 0
    rasterio.plot.show(dem_lonlat, ax=ax, cmap="gray")

    ox.plot_graph(
        G1_projected_streets,
        ax=ax,
        node_alpha=0,
        figsize=(20, 20),
        edge_linewidth=2,
        edge_color="#000000",
        bgcolor="#00000000",
        show=False,
        close=False,
        bbox=[bN + 0.1, bS - 0.1, bE + 0.1, bW - 0.1],
    )
    ox.plot_graph(
        G2_projected_water,
        ax=ax,
        node_alpha=0,
        figsize=(20, 20),
        edge_linewidth=1,
        edge_color="b",
        bgcolor="#00000000",
        show=False,
        close=False,
        bbox=[bN + 0.1, bS - 0.1, bE + 0.1, bW - 0.1],
    )
    ox.plot_footprints(
        G_water,
        ax=ax,
        color="b",
        bgcolor="#00000000",
        show=False,
        close=False,
        bbox=[bN + 0.1, bS - 0.1, bE + 0.1, bW - 0.1],
    )

    ax.set_xlim([bW - 0.1, bE + 0.1])
    ax.set_ylim([bS - 0.1, bN + 0.1])
    ax.tick_params(which="both", direction="out")
    ax.get_xaxis().set_visible(True)
    ax.get_yaxis().set_visible(True)
    ax.set_xlabel("Longitude", fontsize=20)
    ax.set_ylabel("Latitude", fontsize=20)
    ax.tick_params(labelsize=16)
    fig.savefig(outFile)
    subprocess.call(
        "mogrify -fuzz 25% -trim -border 25 -bordercolor white +repage " + outFile,
        shell=True,
    )

    # save osm data
    G2_lv95_water = ox.project_graph(G2_water, to_crs={"init": "epsg:2056"})
    gdf_edges = ox.graph_to_gdfs(
        G2_lv95_water,
        nodes=False,
        edges=True,
        node_geometry=False,
        fill_edge_geometry=True,
    )
    gdf_edges.to_file("osmdata_water.shp")


def _get_colours(colours, bounds=None, colorscaleStep=5):
    """
    Create a colormap and normalization object from a list of colors.

    Args:
    -----
    colours: list
     A list of colors to use for the colormap.
    bounds: list, optional
     A list of bounds for the normalization.
     If not provided, default bounds are used.
    coloarscaleStep: int, optional
     The step size of the tick bounds. Default is 5

    Returns:
    --------
    cmap: colors.ListedColormap
     the colormap object
    norm: colors.BoundaryNorm
     the normalization object
    """
    if bounds == None:
        bounds, __ = _get_tick_bounds(colorscaleStep)
    cc = mcolors.ColorConverter().to_rgba
    c16 = [cc(c0, 0.85) for c0 in colours]
    c16[0] = cc(colours[0], 0.8)
    c16[1] = cc(colours[1], 0.2)
    cmap = mcolors.ListedColormap(c16)
    norm = mcolors.BoundaryNorm(bounds, cmap.N, clip=False)
    return cmap, norm


def _get_tick_bounds(colorscaleStep=5):
    """
    Calculate tick bounds and labels for a color scale.

    Args:
    -----
    coloarscaleStep: int, optional
     The step size of the tick bounds. Default is 5

    Returns:
    --------
    bounds: list
     a list of tick bounds
    ticklabels: list
     a list of tick labels, as strings
    """
    bounds = np.array(list(range(0, 19))) * colorscaleStep
    bounds = bounds.tolist()
    bounds.append(999)
    bounds.insert(0, -99)
    ticklabels = [str(x) for x in bounds]
    ticklabels[0] = "NA"
    ticklabels[len(ticklabels) - 1] = ""
    return bounds, ticklabels
