"""
Methods for visualizing data
"""
import os
import numpy as np
import pandas as pd
from scipy.ndimage import uniform_filter

from utils.transformation import coordx2ind, coordy2ind

#

dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))


# Definitions
colorscale = os.path.join(dir, "8bit_CPC_py.txt")
colorscale_rzc = os.path.join(dir, "8bit_Metranet_v103_py.txt")


def getRainscale(colorscale):
    """
    Read a rainscale color map from a file.
    The file should contain one row per color, with columns for the index, R, G, B, and value of each color.

    Args:
    -----
    colorscale: str
     The path to the file containing the color map.

    Returns:
    --------
    rainscale: ndarray
     An array containing the data from the color map file.
    """
    rainscale = np.array(
        pd.read_csv(
            colorscale,
            sep="\s{2,}|\t",
            header=None,
            skiprows=1,
            dtype={
                "names": ("index", "R", "G", "B", "value"),
                "formats": ("i4", "i4", "i4", "i4", "f4"),
            },
            engine="python",
        )
    )
    return rainscale


def plotShapefile(shape, colour, ax, linewidth=1.0):
    """
    Plot a shapefile on a given axis.

    Args:
    -----
    shape: shapefile.Shape
     The shapefile to plot.
    colour: str
     The color of the lines to use for plotting.
    ax: matplotlib.axes.Axes
     The axis on which to plot the shapefile.
    linewidth: float, optional
     The width of the lines to use for plotting. Defaults to 1.0.

    Returns:
    --------
    None
    """
    parts = shape.parts
    if parts != 0:
        parts.append(len(shape.points))
        for part in parts[:-1]:
            start = part
            end = parts[parts.index(part) + 1]
            x = [i[0] for i in shape.points[start:end]]
            y = [i[1] for i in shape.points[start:end]]
            ax.plot(x, y, color=colour, linewidth=linewidth)
    else:
        x = [i[0] for i in shape.points[:]]
        y = [i[1] for i in shape.points[:]]
        ax.plot(x, y, color=colour, linewidth=linewidth)


def get_totalSum(totalDomainSum, rectangle, size):
    """
    Calculate the total sum of an array within a given rectangle.

    Args:
    -----
    totalDomainSum: ndarray
     The array to sum.
    rectangle: tuple
     The rectangle within which to calculate the sum. It should be
     given as a tuple of (xmin, xmax, ymin, ymax).
    size: int
     The size of the uniform filter to apply.

    Returns:
    --------
    totalSum: ndarray
     The sum of the array within the specified rectangle.
    """

    totalSum = uniform_filter(totalDomainSum, size=size, mode="constant")
    totalSum = totalSum[
        coordy2ind(rectangle[3]) : coordy2ind(rectangle[2]),
        coordx2ind(rectangle[0]) : coordx2ind(rectangle[1]),
    ]
    return totalSum


def select_coord(df, region):
    """
    Select the coordinates in a dataframe that fall within a given region.

    Args:
    -----
    df: DataFrame
     The dataframe containing the coordinates.
    region: object
     An object representing the region. It should have a
     rectangle attribute, which is an array (xmin, xmax, ymin, ymax)
     specifying the bounds of the region.

    Returns:
    --------
    df: DataFrame
     Dataframe containing only the rows with coordinates within the specified region.
    """

    for i in range(0, len(df["xcoord"])):
        x = df["xcoord"][i]
        y = df["ycoord"][i]
        if x >= region.rectangle[0] and x <= region.rectangle[1]:
            pass
        else:
            df["xcoord"][i] = np.nan
        if y >= region.rectangle[2] and y <= region.rectangle[3]:
            pass
        else:
            df["ycoord"][i] = np.nan
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)

    return df


def find_nearest(array, value):
    """
    Find the index of the element in an array that is closest to a given value.

    Args:
    -----
    array: list
     The array to search
    value: float
     The value for which to find the nearest element in the array.=

    Returns:
    --------
    idx: int
     The index of the element in the array that is closest to the given value
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    if np.abs(array[idx] - value) == np.abs((array[idx + 1] - value)):
        idx = idx + 1
    return idx


def makeSummaryFile(summary_file, timestampsoneline, region):
    """
    Write summary data to file

    Args:
    -----
    summary_file: file object
     The file to which the summary data should be written
    timestampsoneline: list
     List containing timestamps in format DD-MM-YYYY HH:MMUTC
    region: object
     An object representing the region for which to generate the summary data.
     Should contain 'totalRoi' and 'rectangle' as attribute.

    Returns:
    --------
    None
    """
    height = region.totalRoi.shape[0]
    width = region.totalRoi.shape[1]

    yroicoords = list(range(region.rectangle[0] + 500, region.rectangle[1] + 500, 1000))
    xroicoords = list(range(region.rectangle[2] + 500, region.rectangle[3] + 500, 1000))
    xroicoords.reverse()

    for w in range(0, width):
        for h in range(0, height):
            summary_file.write(
                "\nPixel ["
                + str(yroicoords[w])
                + ", "
                + str(xroicoords[h])
                + "]\ntime UTC ; intensity [mm/h] ; sum [mm]\n"
            )
            pixelOverTime = region.totalRoi[h, w, :]
            if region.bname["prd"] == "AQC":
                pixelCumsum = np.around(np.cumsum(pixelOverTime), decimals=1)
            else:
                pixelCumsum = np.around(np.cumsum(pixelOverTime / 12.0), decimals=1)
            pixelOverTime = np.around(pixelOverTime, decimals=2)
            pixelData = np.column_stack((timestampsoneline, pixelOverTime, pixelCumsum))
            np.savetxt(
                summary_file, pixelData, fmt="%s ; %s ; %s", header="", newline="\n"
            )
