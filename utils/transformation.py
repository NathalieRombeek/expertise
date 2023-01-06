"""
Methods for transforming data
"""
from datetime import datetime, timedelta
import os
import math
import numpy as np
from numba import jit


@jit
def coordx2ind(coordx):
    x = (coordx - 2255000) / 1000
    return int(x)


@jit
def coordy2ind(coordy):
    y = (1480000 - coordy) / 1000
    return int(y)


# Result in radians, angle between the radar and the center of the ROI
@jit
def angle(radar_location_0, radar_location_1, poi):
    return np.arctan2((radar_location_0 - poi[0]), -1 * (radar_location_1 - poi[1]))


# Result is returned in meters
@jit
def beamHeight(R, elevation, radarHeight=0, earthRadius=6347):
    bh = (
        np.sqrt(
            R**2
            + (4 / 3 * earthRadius) ** 2
            + (2 * R * 4 / 3 * earthRadius * math.sin(np.deg2rad(elevation)))
        )
        - (4 / 3 * earthRadius)
        + radarHeight / 1000
    )
    return bh * 1000


def fname2timestring(fname, newline=True):
    bname = fname.split(os.path.sep)[-1].split(os.path.sep)[-1]
    year = "20" + bname[3:5]
    day = bname[5:8]
    hour = bname[8:10]
    minute = bname[10:12]
    time = datetime.strptime(year + " " + day, "%Y %j")
    if newline:
        dtstring = time.strftime("%d-%m-%Y") + "\n" + hour + ":" + minute + "UTC"
    else:
        dtstring = time.strftime("%d-%m-%Y") + " " + hour + ":" + minute + "UTC"
    return dtstring


def get_file_str(name):
    """
    Extracts information such as date, time, and productname from a file name with the format "prdYYDOYHHMM*".

    Args:
    -----
    name: str
     File name with structure "prdYYDOYHHMM*".

    Returns:
    --------
    file_info: dict
     A dictionary containing information about the file

    """
    file_info = {
        "bname": name,
        "prd": name[:3],
        "year": "20" + name[3:5],
        "day": name[5:8],
        "hour": name[8:10],
        "minute": name[10:12],
        "time": datetime.strptime("20" + name[3:5] + " " + name[5:8], "%Y %j"),
        "date": datetime.strptime(
            "20" + name[3:5] + name[5:8] + name[8:10] + name[10:12], "%Y%j%H%M"
        ),
        "eventCodeName": name[0:8],
    }
    return file_info


def nearest_5min(df):
    """
    Rounds time to the closest 5 min

    Args:
    -----
    df: DataFrame
     Dataframe containing time column

    Returns:
    df: DataFrame
     Dataframe with min rounded to 5 min.
    """
    for i in range(0, len(df["time"])):
        # Calculate the number of seconds until the nearest 5 minute interval
        t = datetime.strptime(df["time"][i], "%Y-%m-%d %H:%M:%S")
        seconds = (t.minute % 5) * 60 + t.second
        # Subtract that number of seconds from the current time to get the nearest 5 minute interval
        nearest = t - timedelta(seconds=seconds)
        # If the nearest interval is more than 2.5 minutes away, round up to the next interval instead
        if seconds > 150:
            nearest += timedelta(minutes=5)
        df["time"][i] = nearest
    return df


def make_timeserie(bname, fname):
    """
    Makes a timeserie of the event with a 5-min interval

    Args:
    -----
    bname: dict
     containing start date and time of the event
    fname: dict
     containing end time of the event

    Returns:
    --------
    timeserie: ndarray
     containing timeseries with 5-min interval
    """

    n_incr = int((fname["date"] - bname["time"]).total_seconds() / (60 * 5))
    timeserie = bname["time"] + np.array(
        [timedelta(minutes=5 * i) for i in range(n_incr + 1)]
    )
    return timeserie


def make_rg(label, depth, chx, chy):
    """
    makes a dictionary of the rain gauge

    Args:
    -----
    label: str
     label of the specific raingauge
    depth: float
     rainfall depth (mm) measured by raingauge
    chx: int
     xcoordinate of raingauge
    chy: int
     ycoordinate of raingauge

    Returns:
    rg: dict
     dictionary containing raingauge name, location and corresponding rainfall depth (mm)
    """

    rg = {"label": label, "depth": depth, "chx": chx, "chy": chy}
    return rg
