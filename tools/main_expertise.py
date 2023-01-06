import numpy as np
import os

from visualization import summary, precipfields, timeserie
from utils import open_data
import tools.region as region


###################
# Global variables
###################


def make_expertise(
    dir,
    prd="RZC",
    singleFiles=False,
    POHfiles=False,
    POHSingleFiles=False,
    roiMap=False,
    visibMap=False,
    useOsm=False,
    useOsmSingleFiles=False,
    make_kml_file=False,
    *rg_kwargs
):
    #######################
    ###   Directories   ###
    #######################

    outDir = os.path.join(dir, "Carrerabach")
    os.chdir(dir)
    if not os.path.isdir(outDir):
        os.makedirs(outDir)

    #######################
    ###  CONFIGURATION  ###
    #######################

    # step 1 open all files
    allFiles = open_data.get_precip_files(dir, prd)

    # step 2 extract precipitation from files
    Region = region.RegionInfo(allFiles)
    Region.fetch_precip_data(dir)

    # step 2b - optional - extract hail data
    if POHfiles:
        Region.fetch_POH_data(dir, POHSingleFiles)

    # step 3 get precipitation plots and csv files
    precipfields.make_avg_zoom(Region, outDir, useOsm=useOsm)
    precipfields.make_sum_zoom(
        Region, outDir, useOsm=useOsm, *rg_kwargs
    )  # define raingauges
    precipfields.make_sum(Region, outDir)
    summary.get_zoom_csv(Region, outDir)

    # step 3b - optional - get single precipitation files
    if singleFiles:
        allFiles = np.sort(allFiles)
        precipfields.processAllFiles(
            Region, allFiles, outDir, useOsmSingleFiles=useOsmSingleFiles
        )

    # step 4 get precipitation timeseries
    timeserie.make_ganglinie(Region, allFiles, outDir)

    # step 4b - optional - get POH timeseries
    if POHfiles and POHSingleFiles:
        if np.count_nonzero(~np.isnan(Region.POH_domain)) != 0:
            timeserie.make_POH_series()

    # step 5 get summary files
    summary.make_summary_file(Region, allFiles, outDir, POHfiles=POHfiles)
    summary.make_netCDF_summary(Region, outDir)
    summary.get_zoom_csv(Region, outDir)
    summary.get_sum_csv(Region, outDir)

    # step 6a - optional
    if roiMap:
        print("roi Map package osmnx not installed...")
        precipfields.make_roiMap(Region, outDir)

    # step 6b - optional - visibility map
    if visibMap:
        from visualization import visibility

        visibility.make_visibMap(Region, outDir)

    # step 6c - optional - ? -
    if make_kml_file:
        from visualization import geographic
        print("unsupported driver...")
        geographic.make_kml_file(Region)