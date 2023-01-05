import os
import numpy as np
from yaconfigobject import Config
from utils.transformation import get_file_str
from utils import open_data


class RegionInfo(object):
    def __init__(self,allFiles):
        
        WORKDIR = os.path.abspath(os.path.dirname(__file__))
        CFG = Config(name=os.path.join(WORKDIR, "expertise.config"))
        
        REGION = CFG.region
        regionRectangle = [REGION.xmin, REGION.xmax, REGION.ymin, REGION.ymax]
        self.rectangle = np.array(regionRectangle)
        self.delta = REGION.delta_region
        self.surfacekm2 = (
            (self.rectangle[1] - self.rectangle[0])
            * (self.rectangle[3] - self.rectangle[2])
            / (1000 * 1000)
        )
        self.roiCentre = (
            self.rectangle[0] + (self.rectangle[1] - self.rectangle[0]) / 2.0,
            self.rectangle[2] + (self.rectangle[3] - self.rectangle[2]) / 2.0,
        )       
        self.name = REGION.name

        fbname = allFiles[len(allFiles)-1].split(os.path.sep)[-1].split(os.path.sep)[-1]
        bname = allFiles[0].split(os.path.sep)[-1].split(os.path.sep)[-1]
        
        self.fbname = get_file_str(fbname)
        self.bname = get_file_str(bname)


    def fetch_precip_data(self,dir):
        prd = self.bname['prd']

        self.totalDomain = open_data.get_totalDomain(dir,prd)

        if prd == "AQC":
            self.totalSum = np.sum(self.totalDomain, axis=2)
        else:
            self.totalSum = np.sum(self.totalDomain, axis=2) / 12.0

        self.totalRoi = open_data.get_totalRoi(self.rectangle,self.totalDomain)
        self.totalSumRoiS = open_data.get_totalSumRois(self.totalRoi,prd)

        self.intensityOverTime = np.average(self.totalRoi, axis=(0, 1))

        if prd == "AQC":
            self.sumOverTime = np.cumsum(np.sum(self.totalRoi, axis=(0, 1))) / np.array(self.surfacekm2)
        else:
            self.sumOverTime = np.cumsum(np.sum(self.totalRoi / 12.0, axis=(0, 1))) / np.array(self.surfacekm2)

    def fetch_POH_data(self,dir,POHSingleFiles):
        self.POH_domain, self.MaxPOHOverTime = open_data.get_POH_domain(dir,self.rectangle,POHSingleFiles)