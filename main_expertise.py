import numpy as np
import os
from yaconfigobject import Config

from visualization import summary, precipfields, timeserie, geographic
from utils import open_data
import region

import argparse

WORKDIR = os.path.abspath(os.path.dirname(__file__))
CFG = Config(name=os.path.join(WORKDIR, "expertise.config"))

###################
# Global variables
###################
RG1 = CFG.rain_gauges.rg1
RG2 = CFG.rain_gauges.rg2

rg1 = {"label": RG1.label, "depth": 96.6, "chx": RG1.chx, "chy": RG1.chy}
rg2 = {"label": RG2.label, "depth": 67.5, "chx": RG2.chx, "chy": RG2.chy}
rain_gauges = [rg1, rg2]

useOsm = CFG.output.useOsm
useOsmSingleFiles = CFG.output.useOsmSingleFiles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('product', type=str, default="")
    parser.add_argument('dir', type=str, default="")
    parser.add_argument('rg1', type=int)
    parser.add_argument('rg2', type=int)

    args = parser.parse_args()

    prd = args.product
    rg1d = args.rg1
    rg2d = args.rg2

    rg1 = {"label": RG1.label, "depth": rg1d, "chx": RG1.chx, "chy": RG1.chy}
    rg2 = {"label": RG2.label, "depth": rg2d, "chx": RG2.chx, "chy": RG2.chy}

    if rg1d and rg2d:
        rain_gauges = [rg1, rg2]
    else:
        rain_gauges=None

    #######################
    ###   Directories   ###
    #######################

    mainDir = args.dir
    outDir = os.path.join(mainDir,"Carrerabach")
    os.chdir(mainDir)
    if not os.path.isdir(outDir):
        os.makedirs(outDir)

    #######################
    ###  CONFIGURATION  ###
    #######################

    # step 1 open all files
    allFiles = open_data.get_precip_files(mainDir, prd)

    # step 2 extract precipitation from files
    Region = region.RegionInfo(allFiles)
    Region.fetch_precip_data(mainDir)

    # step 2b - optional - extract hail data
    if CFG.output.POHfiles:
        Region.fetch_POH_data(mainDir,CFG.output.POHSingleFiles)
        
    # step 3 get precipitation plots and csv files
    precipfields.make_avg_zoom(Region,outDir,useOsm=useOsm)
    precipfields.make_sum_zoom(Region,outDir,rain_gauges=rain_gauges,useOsm=useOsm) #define raingauges
    precipfields.make_sum(Region,outDir)
    summary.get_zoom_csv(Region,outDir)

    # step 3b - optional - get single precipitation files
    if CFG.output.singleFiles:
        allFiles = np.sort(allFiles)
        precipfields.processAllFiles(Region, allFiles, outDir, useOsmSingleFiles=useOsmSingleFiles)

    # step 4 get precipitation timeseries
    timeserie.make_ganglinie(Region,allFiles,outDir)

    # step 4b - optional - get POH timeseries
    if CFG.output.POHfiles and CFG.output.POHSingleFiles:
        if np.count_nonzero(~np.isnan(Region.POH_domain)) != 0:
            timeserie.make_POH_series()

    # step 5 get summary files
    summary.make_summary_file(Region, allFiles, outDir, POHfiles=CFG.output.POHfiles)
    summary.make_netCDF_summary(Region,outDir)
    summary.get_zoom_csv(Region,outDir)
    summary.get_sum_csv(Region,outDir)


    # step 6a - optional
    if CFG.output.roiMap:
        print("roi Map package osmnx not installed...")
        precipfields.make_roiMap(Region,outDir)

    # step 6b - optional - visibility map
    if CFG.output.visibMap:
        from visualization import visibility
        visibility.make_visibMap(Region,outDir)

    # step 6c - optional - ? -
    if CFG.output.make_kml_file:
        print('unsupported driver...')
        geographic.make_kml_file(Region)


if __name__ == "__main__":
    main()