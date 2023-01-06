"""
Methods for opening and processing data
"""

import glob
import os
import numpy as np
from netCDF4 import Dataset
import json

from utils.transformation import coordx2ind, coordy2ind


def get_meta(dir):
    """
    Load metadata from a JSON file.

    Args:
    -----
    dir: str
     The directory containing the JSON file.

    Returns:
    --------
    meta: dict
     A dictionary containing the metadata from the JSON file
    """

    with open(os.path.join(dir, "totalroi.json")) as f:
        metajson = f.readlines()
    meta = json.loads(metajson[0])
    f.close()
    return meta


def get_precip_files(dir, prd="RZC"):
    """
    Get a list of precipitation files in a given directory. The product can be
     either "RZC" or "CPC". The file format is determined based on the metadata
     for the directory.

    Args:
    -----
    dir: str
     The main directory containing the precipitation files.
    prd: str
     The product for which to get the files. Can be either "RZC" (default)
     or "CPC".

    Returns:
    --------
    allFiles: list
     A list of filenames for the precipitation files with a 5-minute timestep,
     for the specified product
    """
    meta = get_meta(dir)
    if meta["fmt"] == ".gif":
        allFiles = glob.glob(os.path.join(dir, prd, "*.gif"))
    elif meta["fmt"] == ".h5":
        allFiles = glob.glob(os.path.join(dir, prd, "*.h5"))
    return allFiles


def get_totalDomain(dir, prd):
    """
    Get the precipitation (mm/h) for a region over time.

    Args:
    -----
    dir: str
     The directory containing the binary file.
    prd: str
     The product for which the data is intended, either "CPC" or "RZC".

    Returns:
    --------
    totalDomain: ndarray
     A 3D array containing the precipitation (mm/h) over the entire domain,
     with dimensions (time,x,y).
    """

    meta = get_meta(dir)
    dtype = np.dtype("f")
    if meta["prd"] != prd:
        print("Be careful, you are mixing up products!")
    f = open(os.path.join(dir, "totalroi.bin"), "rb")
    rdata = np.fromfile(f, dtype)
    totalDomain = np.flipud(
        np.rot90(
            np.transpose(
                rdata.reshape([int(meta["z"]), int(meta["height"]), int(meta["width"])])
            )
        )
    )
    totalDomain[totalDomain < 0] = -1.0

    return totalDomain


def get_totalRoi(rectangle, totalDomain):
    """
    Get the precipitation (mm/h) of a subregion.

    Args:
    -----
    rectangle: tuple
     A tuple specifying the bounds of the region as (xmin, xmax, ymin, ymax).
    totalDomain: ndarray
     Array cotaining the whole region region.

    Returns:
    --------
    totalRoi: ndarray
     A 3-dimensional array containing the precipitation (mm/h)
     over the region of interest.
    """
    totalRoi = totalDomain[
        coordy2ind(rectangle[3]) : coordy2ind(rectangle[2]),
        coordx2ind(rectangle[0]) : coordx2ind(rectangle[1]),
        :,
    ]
    totalRoi[totalRoi < 0] = 0
    return totalRoi


def get_totalSumRois(totalRoi, prd):
    """
    Get the rainfall depth (mm) over the region of interest

    Args:
    -----
    totalRoi: ndarray
     An array containing precipitation (mm/h) within the specified region per timestep.
    prd: str
     The product for which the data is intended, either "CPC" or "RZC"

    Returns:
    --------
    totalSumRoiS: ndarray
     A 2-dimensional array containing the sum of the precipitation (mm) over the
     region of interest for the specified time interval.

    """
    if prd == "AQC":
        totalSumRoi = np.sum(totalRoi, axis=2)
    else:
        totalSumRoi = np.sum(totalRoi / 12.0, axis=2)

    totalSumRoiS = np.around(totalSumRoi, decimals=1)
    totalSumRoiS[totalSumRoiS < 0] = np.NaN

    return totalSumRoiS


def get_POH_domain(dir, rectangle, POHSingleFiles=False):
    """
    Get the probability of hail (POH) over a given region,
     optionally, get per 5-min timestep the max of the region.

    Args:
    -----
    dir: str
     The directory containing the POH files.
    rectangle: tuple
     A tuple specifying the bounds of the region as (xmin, xmax, ymin, ymax).
    POHSingleFiles: bool, optional
     If set to true, also the maximum POH of the region at 5-min interval
     is returned. Default is False.

    Returns:
    --------
    POH_domain: ndarray
     A 2-dimensional array containing the total Probability
     of Hail over the region of interest.
    maxPOHOverTime: ndarray or None
     if True, a 1-dimensional array containing the maximum Probability
     of Hail over the region of interest for each (5-min) time step.
    """
    POH_Dir = os.path.join(dir, "POH")
    POH_file = glob.glob(os.path.join(POH_Dir, "*2400VL.845.h5"))
    POH_daily = Dataset(POH_file[0])
    POH_full = np.transpose(np.ma.getdata(POH_daily["dataset1"]["data1"]["data"][:]))
    POH_domain = POH_full[
        coordy2ind(rectangle[3]) : coordy2ind(rectangle[2]),
        coordx2ind(rectangle[0]) : coordx2ind(rectangle[1]),
    ]
    maxPOHOverTime = None
    if np.count_nonzero(~np.isnan(POH_domain)) != 0 and POHSingleFiles:
        maxPOHOverTime = get_single_POH(POH_Dir, rectangle)
    return POH_domain, maxPOHOverTime


def get_single_POH(dir, rectangle):
    """
    Get per 5-min timestep the max POH of the region.

    Args:
    -----
    dir: str
     The directory containing the POH files.
    rectangle: tuple
     A tuple specifying the bounds of the region as (xmin, xmax, ymin, ymax).

    Returns:
    --------
    maxPOH: ndarray
     A 1-dimensional array containing the maximum Probability of
     Hail over the region of interest for each (5-min) time step.
    """
    all_POH_files = glob.glob(os.path.join(dir, "SingleFiles", "*.h5"))
    all_POH_files = np.sort(all_POH_files)
    maxPOH = np.zeros(len(all_POH_files))
    for i, file in enumerate(all_POH_files):
        POH_single = (Dataset(file))["dataset1"]["data1"]["data"][:]
        POH_single_domain = POH_single[
            coordy2ind(rectangle[3]) : coordy2ind(rectangle[2]),
            coordx2ind(rectangle[0]) : coordx2ind(rectangle[1]),
        ]
        maxPOH[i] = np.nanmax(POH_single_domain)

    return maxPOH
