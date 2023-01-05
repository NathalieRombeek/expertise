import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import subprocess
import shapefile as shp
import math
import shapely, shapely.geometry

from visualization.utils import plotShapefile
from common import constants
from utils import transformation

radars = constants.RADARS
elevations = constants.ELEVATIONS
terrainBg = constants.TERRAINBG
rivers = constants.RIVERS
dem = constants.DEM
terrain = constants.TERRAIN
sf = constants.SF


def make_visibMap(region,outDir):
    outFile = outDir + "/" + region.bname['eventCodeName'] + "-radars.png"
    fig, ax = plt.subplots(figsize=(20, 20))
    plt.imshow(
        terrainBg.read(1),
        extent=[
            terrainBg.bounds[0],
            terrainBg.bounds[2],
            terrainBg.bounds[1],
            terrainBg.bounds[3],
        ],
        cmap="gray",
    )
    ax.set_xlim([2255000, 2965000])
    ax.set_ylim([840000, 1480000])
    ax.set_title("Radars position -  Region: " + region.name, fontsize=24)

    for shape in rivers.shapes():
        plotShapefile(shape, "blue", ax=ax)
    for shape in sf.shapeRecords():
        plotShapefile(shape.shape, "white", linewidth=2.0, ax=ax)

    ax.add_patch(
        Rectangle(
            (region.rectangle[0], region.rectangle[2]),
            region.rectangle[1] - region.rectangle[0],
            region.rectangle[3] - region.rectangle[2],
            edgecolor="yellow",
            fill=False,
            lw=1,
        )
    )

    for radar in radars:
        if math.dist([radar["chx"], radar["chy"]], region.roiCentre) <= 245000:
            angleRS = transformation.angle(radar["chx"], radar["chy"], region.roiCentre)
            targetRS = [
                radar["chx"] - 245000 * math.sin(angleRS),
                radar["chy"] + 245000 * math.cos(angleRS),
            ]
            ax.plot(
                [radar["chx"], targetRS[0]],
                [radar["chy"], targetRS[1]],
                "yellow",
                linestyle="-",
                marker="",
            )
        ax.plot(radar["chx"], radar["chy"], "^", markersize=14, color="green")

    ax.set_aspect("equal")
    plt.xlabel("\nSwiss W-E", fontsize=18)
    plt.ylabel("Swiss S-N\n", fontsize=18)
    ax.ticklabel_format(style="plain")
    ax.tick_params(labelsize=10)
    fig.savefig(outFile)
    plt.close(fig)
    subprocess.call(
        "mogrify -fuzz 25% -trim -border 25 -bordercolor white +repage " + outFile,
        shell=True,
    )

    for radar in radars:
        locationDistance = math.dist([radar["chx"], radar["chy"]], region.roiCentre)
        maxrange = 160000
        if locationDistance <= maxrange:
            num = 2000
            outFile = (
                outDir + "/" + region.name + "-transects-" + radar["code"] + ".png"
            )
            fig, axs = plt.subplots(2, figsize=(17, 12))
            fig.suptitle(
                "\nVisibility of radar "
                + radar["name"]
                + " over "
                + region.name
                + ", distance = "
                + str(int(locationDistance / 1000.0))
                + " km",
                fontsize=24,
            )
            angleRS = transformation.angle(radar["chx"], radar["chy"], region.roiCentre)
            targetRS = [
                radar["chx"] - maxrange * math.sin(angleRS),
                radar["chy"] + maxrange * math.cos(angleRS),
            ]
            # pixel coordinates
            radarX = int(np.round((radar["chx"] - dem.bounds[0]) / dem.res[0]))
            radarY = int(
                np.round(
                    (dem.bounds[3] - dem.bounds[1]) / dem.res[1]
                    - (radar["chy"] - dem.bounds[1]) / dem.res[1]
                )
            )
            targetRSX = int(np.round((targetRS[0] - dem.bounds[0]) / dem.res[0]))
            targetRSY = int(
                np.round(
                    (dem.bounds[3] - dem.bounds[1]) / dem.res[1]
                    - (targetRS[1] - dem.bounds[1]) / dem.res[1]
                )
            )

            x, y = np.linspace(radarX, targetRSX, num), np.linspace(
                radarY, targetRSY, num
            )
            profile = terrain[y.astype(int), x.astype(int)]

            axs[1].axvline(
                x=(locationDistance * num) / maxrange,
                color="red",
                linestyle="-",
                zorder=0,
            )

            axs[1].fill_between(
                list(range(0, num)), profile, interpolate=True, color="gray", zorder=1
            )
            axs[1].set_ylabel("\nTerrain height [m.a.s.l.]", fontsize=18)
            axs[1].set_xlabel("\nDistance from radar [km]", fontsize=18)
            axs[1].spines["bottom"].set_position("zero")
            axs[1].spines["left"].set_position("zero")
            axs[1].spines["bottom"].set_linewidth(0)
            axs[1].spines["top"].set_linewidth(0)
            axs[1].spines["left"].set_linewidth(0)
            axs[1].spines["right"].set_linewidth(0)
            ticks = list(range(0, int(num), int(num / 6)))
            ticks[6] = num
            tlabels = list(range(0, int(maxrange / 1000), int(maxrange / (6 * 1000))))
            tlabels[6] = maxrange / 1000
            axs[1].set_xticks(ticks)
            axs[1].set_xticklabels(tlabels)
            axs[1].set_ylim([0, 10000])

            for el in elevations:
                rangelist = list(range(0, maxrange, int(maxrange / num)))
                rangelist = [i / 1000.0 for i in rangelist]
                radarBeam = list(
                    map(
                        lambda x: transformation.beamHeight(
                            x, elevation=el, radarHeight=radar["height"]
                        ),
                        rangelist,
                    )
                )

                firstOccurrence = True
                for i in list(range(0, num)):
                    if not firstOccurrence:
                        radarBeam[i] = np.nan
                    elif radarBeam[i] <= profile[i]:
                        radarBeam[i] = np.nan
                        firstOccurrence = False
                axs[1].plot(radarBeam, color="black", linestyle="dotted", zorder=1)

            axs[0].imshow(
                terrainBg.read(1),
                extent=[
                    terrainBg.bounds[0],
                    terrainBg.bounds[2],
                    terrainBg.bounds[1],
                    terrainBg.bounds[3],
                ],
                cmap="gray",
            )
            axs[0].axis("off")
            axs[0].set_xlim([2255000, 2965000])
            axs[0].set_ylim([840000, 1480000])
            axs[0].plot(
                [radar["chx"], targetRS[0]],
                [radar["chy"], targetRS[1]],
                "yellow",
                linestyle="-",
                marker="",
            )
            axs[0].plot(radar["chx"], radar["chy"], "^", markersize=14, color="green")
            for shape in sf.shapeRecords():
                plotShapefile(shape.shape, "white", linewidth=2.0, ax=axs[0])

            # axs[0].plot(x, y, 'o', markersize=4, color="green") # for debug
            fig.savefig(outFile)
            plt.close(fig)
