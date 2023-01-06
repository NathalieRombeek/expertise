import os
import numpy as np
from utils.transformation import get_file_str
from utils import open_data


class RegionInfo(object):
    """
    Class to store and manipulate information about a region of interest.

    Attributes:
    -----------
    rectangle: ndarray
     Array containing the bounds of the region as (xmin, xmax, ymin, ymax).
    delta: float
    surfacekm2: float
     The surface area of the region in square kilometers
    roiCentre: tuple
     Tuple containing the coordinates of the center of the region
    name: str
     The name of the region.
    bname: dict
     A dictionary containing information about the first file of the event
    fbname: dict
     A dictionary containing information about the last file of the event

    """

    def __init__(
        self,
        allFiles,
        name="Carrerabach",
        regionRectangle=[2739000, 2746000, 1178000, 1185000],
        delta_region=20000,
    ):
        """
        Initializes a Region

        Args:
        -----
        Allfiles: list
         All files for specific event
        name: str, optional
         Name of region of interest. Default is "Carrerabach".
        regionRectangle: list, optional
         Outer bounds of region of interest. Default is bounds corresponding to Carrerabach.
        delta_region: int, optional
        """
        self.rectangle = np.array(regionRectangle)
        self.delta = delta_region
        self.surfacekm2 = (
            (self.rectangle[1] - self.rectangle[0])
            * (self.rectangle[3] - self.rectangle[2])
            / (1000 * 1000)
        )
        self.roiCentre = (
            self.rectangle[0] + (self.rectangle[1] - self.rectangle[0]) / 2.0,
            self.rectangle[2] + (self.rectangle[3] - self.rectangle[2]) / 2.0,
        )
        self.name = name

        # first file
        bname = allFiles[0].split(os.path.sep)[-1].split(os.path.sep)[-1]
        # last file
        fbname = (
            allFiles[len(allFiles) - 1].split(os.path.sep)[-1].split(os.path.sep)[-1]
        )

        self.bname = get_file_str(bname)
        self.fbname = get_file_str(fbname)

    def fetch_precip_data(self, dir):
        """
        Class to store and manipulate precipiation data over a domain and
         region of interest

        Args:
        -----
        dir: str
         Directory containing precipiation files

        Attributes:
        -----------
        totalDomain: ndarray
         A 3-dimensional array containing the precipitation (mm/h) over the
         entire domain per 5-min.
        totalSum: ndarray
         A 2-dimensional array containing the total precipitation (mm)
         over the region of interest.
        totalRoi: ndarray
         A 3-dimensional array containing the total precipitation (mm/h)
         over the region of interest for each time step.
        totalSumRoiS: ndarray
         A 2-dimensional array containing the sum of the precipitation (mm) over the
         region of interest for the specified time interval.
        intensityOverTime: ndarray
         A 1-dimensional array containing the average intensity (mm/h) of the precipitation
         over the region of interest for each time step.
        sumOverTime: ndarray
         A 1-dimensional array containing the cummulative sum (mm)
         of the precipitation over the region of interest for each time step.

        """
        prd = self.bname["prd"]

        self.totalDomain = open_data.get_totalDomain(dir, prd)

        if prd == "AQC":
            self.totalSum = np.sum(self.totalDomain, axis=2)
        else:
            self.totalSum = np.sum(self.totalDomain, axis=2) / 12.0

        self.totalRoi = open_data.get_totalRoi(self.rectangle, self.totalDomain)
        self.totalSumRoiS = open_data.get_totalSumRois(self.totalRoi, prd)

        self.intensityOverTime = np.average(self.totalRoi, axis=(0, 1))

        if prd == "AQC":
            self.sumOverTime = np.cumsum(np.sum(self.totalRoi, axis=(0, 1))) / np.array(
                self.surfacekm2
            )
        else:
            self.sumOverTime = np.cumsum(
                np.sum(self.totalRoi / 12.0, axis=(0, 1))
            ) / np.array(self.surfacekm2)

    def fetch_POH_data(self, dir, POHSingleFiles=False):
        """
         Class to store and manipulate hail data over a domain
         and region of interest

        Args:
        -----
        dir: str
         Directory containing hail files
        POHSingleFiles: bool, optional

        Attributes:
        -----------
        POH_domain: ndarray:
         A 2-dimensional array containing the total Probability
         of Hail over the region of interest.
        MaxPOHOverTime: ndarray
         A 1-dimensional array containing the maximum
         Probability of Hail over the region of interest for each time step.

        """

        self.POH_domain, self.MaxPOHOverTime = open_data.get_POH_domain(
            dir, self.rectangle, POHSingleFiles
        )
