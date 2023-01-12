"""
Method for making a summary file of data in a txt or netCDF file
"""
from datetime import datetime
import numpy as np
from netCDF4 import Dataset
import pandas as pd
from visualization.utils import get_totalSum, makeSummaryFile
from utils.transformation import fname2timestring, make_timeserie


###############
# TXT
###############

def make_summary_file(region, allFiles, outDir, POHfiles=False, sizes=[3, 5, 7, 9, 11, 15]):
    """
    Args:
    -----
    region: object
    contains information about the region
    """
    
    bname = region.bname
    fname = region.fbname
    totalSumRoiS = region.totalSumRoiS
    timestamps = np.array(list(map(fname2timestring, allFiles)))

    outFile = outDir + "/" + bname['eventCodeName'] + "-summary.txt"
    with open(outFile, "w+") as summary_file:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        summary_file.write("Computed on: " + dt_string + "\n")
        summary_file.write("Region: " + region.name + "\n")
        summary_file.write(
            "Start period: "
            + bname['time'].strftime("%d/%m/%Y")
            + " "
            + bname['hour']
            + ":"
            + bname['minute']
            + "UTC\n"
        )
        summary_file.write(
            "End period: "
            + fname['time'].strftime("%d/%m/%Y")
            + " "
            + fname['hour']
            + ":"
            + fname['minute']
            + "UTC\n"
        )
        summary_file.write(
            "Region of interest (swiss coordinates of the rectangle): "
            + str(region.rectangle)
            + "\n"
        )
        summary_file.write("Region area: " + str(region.surfacekm2) + " km2\n")
        summary_file.write("Radar product used: " + bname['prd'] + "\n\n")
        summary_file.write("Maximum over region: " + str(np.nanmax(totalSumRoiS)) + " mm\n")
        summary_file.write("Minimum over region: " + str(np.nanmin(totalSumRoiS)) + " mm\n")
        summary_file.write(
            "Average over region: "
            + str(np.around(np.average(totalSumRoiS), decimals=2))
            + " mm\n"
        )
        summary_file.write(
            "Standard deviation over region: "
            + str(np.around(np.std(totalSumRoiS), decimals=2))
            + " mm\n"
        )
        summary_file.write(
            "Wet fraction over region: "
            + str(
                np.around((np.count_nonzero(totalSumRoiS) / totalSumRoiS.size), decimals=2)
            )
            + " \n\n"
        )

        if POHfiles:
            if np.count_nonzero(~np.isnan(region.POH_domain)) == 0:
                summary_file.write("No hail present over region" + "\n\n")
            else:
                summary_file.write(
                    "Hail fraction over region: "
                    + str(
                        np.around(
                            (np.count_nonzero(~np.isnan(region.POH_domain)) / region.POH_domain.size),
                            decimals=2
                        )
                    )
                    + "\n"
                )
                summary_file.write(
                    "Maximum POH over region: " + str(np.nanmax(region.POH_domain)) + "\n\n"
                )

        if region.bname['prd'] == "AQC":
            totalDomainSum = np.sum(region.totalDomain, axis=2)
        else:
            totalDomainSum = np.sum(region.totalDomain, axis=2) / 12.0

        # added in case there is nan values in totalDomainSum
        totalDomainSum[np.isnan(totalDomainSum)] = 0
        totalSumSizes = {f"totalSum{size}": get_totalSum(totalDomainSum,region.rectangle,size) for size in sizes}

        for size in sizes:
            summary_file.write(
                f"Minimum and maximum over {size}x{size} km within the region: "
                + str(np.around(np.nanmin(totalSumSizes[f"totalSum{size}"]), decimals=1))
                + "; "
                + str(np.around(np.nanmax(totalSumSizes[f"totalSum{size}"]), decimals=1))
                + " mm\n"
            )
        summary_file.write("\n")
        timestampsoneline = list()
        for ts in timestamps:
            timestampsoneline.append(ts.replace("\n", " "))

        summary_file.write(
            "Precipitation intensity and sum over time for region " + region.name + "\n"
        )

        intensityOverTime = np.around(region.intensityOverTime, decimals=2)
        intensities = np.column_stack((timestampsoneline, intensityOverTime))
        cumsum = np.around(region.sumOverTime, decimals=1)
        roiData = np.column_stack((timestampsoneline, intensityOverTime, cumsum))
        np.savetxt(
            summary_file,
            roiData,
            fmt="%s ; %s ; %s",
            header="time UTC ; intensity [mm/h] ; sum [mm]",
            newline="\n",
        )
        makeSummaryFile(summary_file, timestampsoneline, region)
        summary_file.write(
            "\nPrecipitation intensity and sum over time for region " + region.name + "\n"
        )

###############
# netCDF
###############

def make_netCDF_summary(region,outDir):
    fname = region.fbname
    bname = region.bname

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    ## Make netCDF
    timeserie = make_timeserie(bname,fname)

    diff_sec = [t - timeserie[0] for t in timeserie]

    outFile = outDir + "/" + bname['eventCodeName'] + "-summary.nc"

    with Dataset(outFile, "w", format="NETCDF4") as ncfile:

        ncfile.title = f'Summary of precipitation for {timeserie[0].strftime("%d/%m/%Y")}'
        ncfile.history = f"Created on {dt_string}"
        ncfile.institution = "MeteoSwiss (Switzerland)"
        ncfile.setncattr("Radar product", bname['prd'])
        ncfile.setncattr(
            "proj4",
            "+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=2600000 +y_0=1200000 +ellps=bessel +towgs84=674.374,15.056,405.346,0,0,0,0 +units=m +no_defs",
        )

        # group with whole domain
        domain = ncfile.createGroup("Domain")
        domain.createDimension("x", 710)
        domain.createDimension("y", 640)
        domain.createDimension(
            "time",
        )

        dom_t = domain.createVariable("time", np.int64, ("time",))
        dom_t.long_name = f'minutes since {timeserie[0].strftime("%d/%m/%Y %H:%M")} UTC'
        dom_t[:] = [(t.total_seconds()) / 60 for t in diff_sec]

        domx = domain.createVariable(
            "lat",
            np.float64,
            (
                "x",
                "y",
            ),
        )
        domy = domain.createVariable(
            "lon",
            np.float64,
            (
                "x",
                "y",
            ),
        )
        domx.long_name = "x-coordinate in Swiss coordinate system"
        domy.long_name = "y-coordinate in Swiss coordinate system"
        domx.units = "km"
        domy.units = "km"

        X_coord = list(range(2255000, 2965000, 1000))  # 710
        Y_coord = list(range(840000, 1480000, 1000))  # 640
        Y, X = np.meshgrid(Y_coord, X_coord)

        domy[:] = Y
        domx[:] = X

        dom_int = domain.createVariable(
            "intensity",
            np.float32,
            (
                "x",
                "y",
                "time",
            ),
        )
        dom_int.long_name = "Intensity"
        dom_int.units = "mm/h"

        tot_domain = np.transpose(region.totalDomain[:, :, :288], (1, 0, 2))
        dom_int[:] = tot_domain
        dom_sum = domain.createVariable(
            "sum",
            np.float32,
            (
                "x",
                "y",
            ),
        )
        dom_sum.long_name = "Total rainfall during day"
        dom_sum.units = "mm"
        dom_sum[:] = np.around(np.nansum(tot_domain / 12, axis=2), decimals=2)

        # group with basin
        basin = ncfile.createGroup(f"{region.name}")
        basin.createDimension("x", 7)
        basin.createDimension("y", 7)
        basin.createDimension(
            "time",
        )

        basin_t = basin.createVariable("time", np.int64, ("time",))
        basin_t.long_name = f'minutes since {timeserie[0].strftime("%Y/%m/%d %H:%M")} UTC'
        basin_t[:] = [(t.total_seconds()) / 60 for t in diff_sec]

        x_dim = basin.createVariable(
            "lat",
            np.float64,
            (
                "x",
                "y",
            ),
        )
        y_dim = basin.createVariable(
            "lon",
            np.float64,
            (
                "x",
                "y",
            ),
        )
        x_dim.long_name = "x-coordinate in Swiss coordinate system"
        y_dim.long_name = "y-coordinate in Swiss coordinate system"
        x_dim.units = "km"
        y_dim.units = "km"

        Y_coord = list(range(region.rectangle[0] + 500, region.rectangle[1] + 500, 1000))
        X_coord = list(range(region.rectangle[2] + 500, region.rectangle[3] + 500, 1000))
        Y, X = np.meshgrid(Y_coord, X_coord)

        y_dim[:] = Y
        x_dim[:] = X

        intensity = basin.createVariable(
            "intensity",
            np.float32,
            (
                "x",
                "y",
                "time",
            ),
        )
        intensity.long_name = "Intensity"
        intensity.units = "mm/h"

        intensity[:] = region.totalRoi[:, :, :288]
        sum = basin.createVariable(
            "sum",
            np.float32,
            (
                "x",
                "y",
            ),
        )
        sum.long_name = "Total rainfall during day"
        sum.units = "mm"
        sum[:] = np.around(np.sum(region.totalRoi / 12.0, axis=(2)), decimals=2)



###############
# CSV
###############

def get_zoom_csv(region,outDir):
    bname = region.bname

    outFile = outDir + "/" + bname['eventCodeName'] + "-zoom.csv"
        
    pdTotalSumRoiS = pd.DataFrame(region.totalSumRoiS)
    pdTotalSumRoiS.columns = np.linspace(
        region.rectangle[0] + 500,
        region.rectangle[1] - 500,
        num=len(pdTotalSumRoiS.columns),
        dtype=int,
    )
    pdTotalSumRoiS.index = np.linspace(
        region.rectangle[2] + 500,
        region.rectangle[3] - 500,
        num=len(pdTotalSumRoiS.index),
        dtype=int,
    )
    with open(outFile, "w+") as roi_file:
        # roi_file = open(outFile, "w+")
        roi_file.write(
            'Pixel values, mm of precipitation for region "'
            + region.name
            + '" ['
            + str(region.surfacekm2)
            + " km2]\nProduct = "
            + bname['prd']
            + "\nSwiss coordinates LV95\nColumn and row names (coordinates) refer to pixel centre\n\n"
        )
        pdTotalSumRoiS.to_csv(roi_file)

def get_sum_csv(region,outDir):
    totalSumS = np.around(region.totalSum, decimals=1)
    outFile = outDir + "/"+ region.bname['eventCodeName'] +"-sum.csv"
    totalSumS[totalSumS < 0] = np.NaN
    np.savetxt(outFile, totalSumS, delimiter=";", fmt='%4.2f', newline='\n')