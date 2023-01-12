"""
Method for extracting data in specified directory
"""
import shutil
import datetime
import zipfile
import os

WORKDIR = os.path.abspath(os.path.dirname(__file__))


def retrieve_input_data(
    date,
    file_dir,
    product="RZC",
    get_daily_POH=False,
    get_single_POH=False,
):
    """Extracts files of a specific product (RZC, CPC, POH and/or hailsize
     crowdsourcedata) from the MeteoSwiss database

    Args:
    -----
    date: datetime
     The date for which to retrieve the data
    product: str
     precipitation product that will be retrieved, either RZC or CPC
    file_dir: str
     The main directory where the retrieved data will be saved
    get_daily_POH: bool, optional
     Option to retrieve daily probability of hail product
    get_single_POH: bool, optional
     Option to retrieve 5-min probability of hail product

    Returns:
    --------
    sub_dir: str
     Directory where all files are saved.
    """

    YearDOY = str(date.strftime("%Y%j"))

    sub_dir = os.path.join(file_dir, YearDOY + "_saettele/")
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)

    retrieve_precip(date, product, sub_dir)

    if get_daily_POH:
        hail_path = os.path.join(sub_dir, "POH/")
        if not os.path.exists(hail_path):
            os.makedirs(hail_path)
        retrieve_POH(date, hail_path, single_POH=get_single_POH)
        if get_single_POH:
            retrieve_hail_crowdsource(date=date, dir=hail_path, transform=True)

    return sub_dir


def retrieve_precip(date, prd, dir):
    """Copies and extracts precipitation (RZC or CPC)
     from the MeteoSwiss database

    Args:
    -----
    date: datetime
     The date for which to retrieve the precipitation data
    product: str
     precipitation product that will be retrieved, either RZC or CPC
    dir: str
     The directory where the precipitation data should be saved

    Returns:
    --------
    None
    """

    year = date.strftime("%Y")
    YYDOY = str(date.strftime("%y%j"))
    YearDOY = str(date.strftime("%Y%j"))

    dst = os.path.join(dir, prd + "_" + YearDOY + ".zip")
    if prd == "RZC":
        try:
            src = f"/store/msrad/radar/swiss/hdf5/{year}/{YYDOY}/{prd}{YYDOY}.zip"
            shutil.copy(src, dst)
        except FileNotFoundError:
            src = f"/store/msrad/radar/swiss/hdf5/{year}/{YYDOY}/{prd}flt{YYDOY}.zip"
            shutil.copy(src, dst)
    elif prd == "CPC":
        src = f"/store/msrad/radar/swiss/data/{year}/{YYDOY}/{prd}{YYDOY}.zip"
        shutil.copy(src, dst)

    rain_path = os.path.join(dir, prd + "/")

    if not os.path.exists(rain_path):
        os.makedirs(rain_path)

    if prd == "RZC":
        with zipfile.ZipFile(dst, "r") as zip_ref:
            zip_ref.extractall(rain_path)
    if prd == "CPC":
        with zipfile.ZipFile(dst, "r") as zipObject:
            listOfFileNames = zipObject.namelist()
            for fileName in listOfFileNames:
                if fileName.endswith("00005.801.gif"):
                    zipObject.extract(fileName, rain_path)


def retrieve_POH(date, dir, single_POH=False):
    """
    Retrieve POH data for a given date and
     optionally extract single 5-min POH files,
     if single_POH is set to True.

    Args:
    -----
    date: datetime
     The date for which to retrieve the POH data
    dir: str
     The directory where the POH data should be saved
    single_POH: bool, optional
     Indicates whether to also retrieve the single
     5-min POH files. Defaults to False.

    Returns:
    --------
    None
    """
    year = date.strftime("%Y")
    YYDOY = str(date.strftime("%y%j"))

    # src = f"/store/msrad/radar/swiss/data/{year}/{YYDOY}/dBZCH{YYDOY}.zip"
    src = f"/store/msrad/radar/swiss/hdf5/{year}/{YYDOY}/dBZCH{YYDOY}.zip"
    with zipfile.ZipFile(src, "r") as zipObject:
        listOfFileNames = zipObject.namelist()
        for fileName in listOfFileNames:
            # if fileName.endswith("2400VL.845"):
            if fileName.endswith("2400VL.845.h5"):
                zipObject.extract(fileName, dir)

    if single_POH:
        src = f"/store/msrad/radar/swiss/hdf5/{year}/{YYDOY}/BZCH{YYDOY}.zip"
        dst = os.path.join(dir, "POH.zip")
        shutil.copy(src, dst)
        with zipfile.ZipFile(dst, "r") as zip_ref:
            zip_ref.extractall(dir)


def retrieve_hail_crowdsource(date, dir, transform=True):
    """
    Retrieve hail crowdsource data for a given date and optionally transform it.

    Args:
    -----
    date: datetime
     The date for which to retrieve the crowdsource data.
    dir: str
     The directory where the crowdsource data should be saved.
    transform: bool, optional
     Indicates whether to transform the crowdsource data. Defaults to True.

    Returns:
    --------
    None
    """

    YYDOY = str(date.strftime("%y%j"))

    # get crowdsource data
    crs_path = f"/store/msrad/crowdsourcing/hail/HQX/HQX{YYDOY}0000.prd"
    if os.path.isfile(crs_path):

        dst = os.path.join(dir, f"{YYDOY}_crowdsource.prd")
        shutil.copy(crs_path, dst)

        if transform:
            transform_crowdsource(YYDOY, dir)

    else:
        print(f"no crowdsource data available on {YYDOY}")


def transform_crowdsource(YYDOY, hail_dir):
    """
    Transform crowdsource data from the .prd
     format to a .csv format with Swiss coordinates

    Args:
    -----
    YYDOY: str
     The YYDOY identifier for the crowdsource data
    dir: str
     The directory containing the .prd file and
     where the .csv file will be saved

    Returns:
    --------
    None
    """
    import pandas as pd
    import pyproj

    df = pd.read_csv(
        os.path.join(hail_dir, YYDOY + "_crowdsource.prd"),
        sep=" ",
        header=None,
    )
    df = df.dropna(axis=1)
    df = df.drop(columns=[8])
    df = df.rename(columns={2: "time", 4: "ycoord", 6: "xcoord", 7: "hailsize"})
    df["time"] = pd.to_datetime(df["time"], unit="s")

    # Set up the transformation from LV03 to LV95
    lv95 = pyproj.Proj(init="epsg:2056")
    lv03 = pyproj.Proj(init="epsg:21781")

    # Convert the coordinates
    x_lv95, y_lv95 = pyproj.transform(
        lv03, lv95, df["xcoord"] * 1000, df["ycoord"] * 1000
    )
    df["xcoord"] = x_lv95
    df["ycoord"] = y_lv95

    df.to_csv(os.path.join(hail_dir, "HailCrowdsource.csv"), index=False)
