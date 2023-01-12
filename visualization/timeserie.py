"""
Methods for making timeseries of the data
"""
import os
import numpy as np
from math import floor
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
from glob import glob
from visualization.utils import select_coord
from utils.transformation import nearest_5min, fname2timestring, make_timeserie

###############
# PRECIPITATON
###############

def make_ganglinie(region,allFiles,outDir):
    bname = region.bname
    fname = region.fbname
    timestamps = np.array(list(map(fname2timestring, allFiles)))

    outFile = outDir + "/" + bname['eventCodeName'] + "-ganglinie.png"
    fig, axs = plt.subplots(2, figsize=(17, 12))
    fig.suptitle(
        "\nPrecipitation intensity [mm/h] and cumulative sum [mm] over region "
        + region.name
        + " ["
        + str(int(region.surfacekm2))
        + " km\u00b2]\nfrom: "
        + bname['time'].strftime("%d/%m/%Y")
        + " "
        + bname['hour']
        + ":"
        + bname['minute']
        + "UTC to: "
        + fname['time'].strftime("%d/%m/%Y")
        + " "
        + fname['hour']
        + ":"
        + fname['minute']
        + "UTC, product = "
        + bname['prd'],
        fontsize=22,
    )

    nticks = 5
    tistep = int(floor(len(allFiles) / nticks))
    ticks = list(range(tistep, len(allFiles) - tistep, tistep))
    ticks.append(len(allFiles) - 1)
    ticks.insert(0, 0)
    tlabels = timestamps[np.array(ticks)]

    axs[0].grid(axis="x")
    axs[0].plot(region.intensityOverTime, color="red")
    axs[0].set_ylabel("\nmm/h", fontsize=18)
    axs[0].set_xticklabels("")
    axs[0].set_xticks(ticks)
    axs[0].set_xticklabels(tlabels)
    axs[0].spines["bottom"].set_position("zero")
    axs[0].set_xlim([0, len(region.intensityOverTime) - 1])
    axs[0].xaxis.set_tick_params(pad=18, labelsize=14)
    axs[1].plot(region.sumOverTime)
    indexes = list(range(0, len(region.sumOverTime)))
    axs[1].fill_between(np.array(indexes), np.array(region.sumOverTime), interpolate=True)
    axs[1].set_ylabel("\nmm", fontsize=18)
    axs[1].set_xlabel("\nTime", fontsize=18)
    axs[1].set_xticks(ticks)
    axs[1].set_xticklabels(tlabels)
    axs[1].grid(axis="x")
    axs[1].set_xlim([0, len(region.sumOverTime) - 1])
    axs[1].xaxis.set_tick_params(pad=18, labelsize=14)
    axs[1].spines["bottom"].set_position("zero")
    fig.savefig(outFile)
    plt.close(fig)
    subprocess.call(
        "mogrify -fuzz 25% -trim -border 25 -bordercolor white +repage " + outFile,
        shell=True,
    )


###############
# POH
###############

def make_POH_series(region,allFiles,Dir):
    bname = region.bname
    fname = region.fbname
    allFiles = np.sort(allFiles)
    timestamps = np.array(list(map(fname2timestring, allFiles)))
    all_POH_files = glob(os.path.join(Dir,"POH", "SingleFiles", "*.h5"))

    outDir = os.path.join(Dir,region.name)
    CrowdPath = os.path.join(Dir,"HailCrowdsource.csv")
    outFile = outDir + "/" + bname['eventCodeName'] + "-POH-ganglinie.png"

    fig, ax = plt.subplots(figsize=(17, 12))
    fig.suptitle(
        "Maximum POH over region "
        + region.name
        + " ["
        + str(int(region.surfacekm2))
        + " km\u00b2]\nfrom: "
        + bname['time'].strftime("%d/%m/%Y")
        + " "
        + bname['hour']
        + ":"
        + bname['minute']
        + "UTC to: "
        + fname['time'].strftime("%d/%m/%Y")
        + " "
        + fname['hour']
        + ":"
        + fname['minute']
        + "UTC, product = "
        + bname['prd'],
        fontsize=22,
    )

    nticks = 5
    tistep = int(floor(len(all_POH_files) / nticks))
    ticks = list(range(tistep, len(all_POH_files) - tistep, tistep))
    ticks.append(len(all_POH_files) - 1)
    ticks.insert(0, 0)
    tlabels = timestamps[np.array(ticks)]

    timeserie=make_timeserie(bname,fname)

    ax.grid(axis="x")
    region.MaxPOHOverTime[np.isnan(region.MaxPOHOverTime) == True] = 0
    ax.plot(region.MaxPOHOverTime, color="red", label="POH")
    # ax.plot(timeserie, region.MaxPOHOverTime, color="red", label="POH")


    ax.set_ylabel("\nMax probability of hail", fontsize=18)
    ax.set_xticklabels("")
    ax.set_xticks(ticks)
    ax.set_xticklabels(tlabels)
    ax.spines["bottom"].set_position("zero")
    ax.set_xlim([0, len(region.MaxPOHOverTime) - 1])
    ax.set_ylim([0, 1])

    if os.path.exists(CrowdPath):
        fig.suptitle(
            "Maximum POH and hail size over region "
            + region.name
            + " ["
            + str(int(region.surfacekm2))
            + " km\u00b2]\nfrom: "
            + bname['time'].strftime("%d/%m/%Y")
            + " "
            + bname['hour']
            + ":"
            + bname['minute']
            + "UTC to: "
            + fname['time'].strftime("%d/%m/%Y")
            + " "
            + fname['hour']
            + ":"
            + fname['minute']
            + "UTC, product = "
            + bname['prd'],
            fontsize=22,
        )

        df = pd.read_csv(CrowdPath)
        df = select_coord(df,region)
        df = nearest_5min(df)
        df = df.groupby("time").max()
        df = df.reset_index(drop=False)

        POHseries = np.zeros(len(timeserie))
        for i in range(0, len(df["time"])):
            POHseries[timeserie == df["time"][i]] = df["hailsize"][i]
        POHseries[POHseries == 0] = np.nan

        ax2 = ax.twinx()
        ax2.plot(
            POHseries,
            color="blue",
            label="Hail size",
            marker="o",
            linestyle="",
            markersize=10,
        )

        if np.max(POHseries) in [1, 2, 3, 4]:
            ax2.set_ylim([1, 4])
            ax2.set_yticklabels(["0.5-0.8", "2.3", "3.15", ">4.3"])
        else:
            ax2.set_ylim([10, 17])
            ax2.set_yticklabels(
                ["", "<0.5", "0.5-0.8", "2.3", "3.15", "4.3", "6.5-6.8", ""]
            )
            ax2.set_ylabel("\nMax estimated hail size (cm)", fontsize=18)
            ax2.yaxis.set_tick_params(labelsize=14)
            ax2.legend(fontsize=18, bbox_to_anchor=(1, 0.95), loc="best")

    ax.legend(fontsize=18, alignment="left", loc="best")

    ax.xaxis.set_tick_params(pad=18, labelsize=14)
    fig.savefig(outFile)
    plt.close(fig)
    subprocess.call(
        "mogrify -fuzz 25% -trim -border 25 -bordercolor white +repage " + outFile,
        shell=True,
    )



    