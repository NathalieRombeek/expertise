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
    name="Carrerabach",
    regionRectangle=[2739000, 2746000, 1178000, 1185000],
    singleFiles=False,
    POHfiles=False,
    POHSingleFiles=False,
    roiMap=False,
    visibMap=False,
    useOsm=False,
    useOsmSingleFiles=False,
    make_kml_file=False,
    *rg_args
):
    """
    Run the expertise script to generate plots for a given date and product (RZC or CPC).
    Optionally other output can be generated, such as a timeseries for POH, including hailsize
    crowdsource data, visibility map of the radars, map of the region of interest.

    Args:
    -----
    dir: str
     Direcotory where all extracted products are stored and where output needs to be saved
    prd: str
     The product to use, either 'RZC' or 'CPC'.
    name: str, optional
     Name of region of interest. Default is "Carrerabach".
    regionRectangle: list, optional
     Outer bounds of region of interest. Default is bounds corresponding to Carrerabach.
    POHfiles: bool, optional
     Whether to include POH daily data in the analysis. Default is False.
    POHSingleFiles: bool, optional
     Whether to include 5-min POH file data in the analysis. Default is False.
    singleFiles: bool, optional
     Whether to generate plots for 5-min files. Default is False.
    roiMap: bool, optional
     Whether to generate a map of the region of interest. Default is False.
    visibMap: bool, optional
     Whether to generate a visibility map. Default is False.
    useOsm: bool, optional
     Whether to use OpenStreetMap data for the maps. Default is False.
    useOsmSingleFiles: bool, optional
     Whether to use OpenStreetMap data for the individual file maps. Default is False.
    make_kml_file: bool, optional
     Whether to generate a KML file for the region of interest. Default is False.
    *rg_args: list, optional
     Additional positional arguments for raingauges, output of func: make_rg
     should be passed.

    Returns:
    --------
    None

    """
    #######################
    ###   Directories   ###
    #######################

    outDir = os.path.join(dir, name)
    os.chdir(dir)
    if not os.path.isdir(outDir):
        os.makedirs(outDir)

    #######################
    ###  CONFIGURATION  ###
    #######################

    # step 1 open all files
    allFiles = open_data.get_precip_files(dir, prd)
    allFiles = np.sort(allFiles)
    print("step 1 open files completed")
    
    # step 2 extract precipitation from files
    Region = region.RegionInfo(allFiles,name=name,regionRectangle=regionRectangle)
    Region.fetch_precip_data(dir)
    print("step 2a extract precipitation completed")

    # step 2b - optional - extract hail data
    if POHfiles:
        Region.fetch_POH_data(dir, POHSingleFiles)
        print("step 2b extract POHfiles completed")

    # step 3 get precipitation plots and csv files
    precipfields.make_avg_zoom(Region, outDir, useOsm=useOsm)
    precipfields.make_sum_zoom(
        Region, outDir, useOsm, *rg_args
    )  # define raingauges
    precipfields.make_sum(Region, outDir)
    summary.get_zoom_csv(Region, outDir)
    print("step 3a make precipitation plots completed")

    # step 3b - optional - get single precipitation files
    if singleFiles:
        allFiles = np.sort(allFiles)
        precipfields.processAllFiles(
            Region, allFiles, outDir, useOsmSingleFiles=useOsmSingleFiles
        )
        print("step 3b make single precpitation plots completed")

    # step 4 get precipitation timeseries
    timeserie.make_ganglinie(Region, allFiles, outDir)
    print("step 4a make precipitation timeseries completed")

    # step 4b - optional - get POH timeseries
    if POHfiles and POHSingleFiles:
        if np.count_nonzero(~np.isnan(Region.POH_domain)) != 0:
            timeserie.make_POH_series(Region,allFiles,dir)
            print("step 4b make POH timeseries completed")
        else:
            print("No hail in this region")

    # step 5 get summary files
    summary.make_summary_file(Region, allFiles, outDir, POHfiles=POHfiles)
    summary.make_netCDF_summary(Region, outDir)
    summary.get_zoom_csv(Region, outDir)
    summary.get_sum_csv(Region, outDir)
    print("step 5 make summary files completed")

    # step 6a - optional
    if roiMap:
        precipfields.make_roiMap(Region, outDir)

    # step 6b - optional - visibility map
    if visibMap:
        from visualization import visibility
        visibility.make_visibMap(Region, outDir)

    # step 6c - optional - kml file
    if make_kml_file:
        from visualization import geographic
        geographic.make_kml_file(Region)
