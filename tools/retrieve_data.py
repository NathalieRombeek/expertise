"""
Method for extracting data in specified directory
"""
from datetime import datetime, timedelta
import numpy as np
import shutil
import zipfile
import os

WORKDIR = os.path.abspath(os.path.dirname(__file__))


def retrieve_input_data(
    start_date,
    end_date,
    file_dir,
    archive,
    prd="RZC",
    get_daily_POH=False,
    get_single_POH=False,
):
    """Extracts files of a specific product (RZC, CPC, POH and/or hailsize
     crowdsourcedata) from the MeteoSwiss database

    Args:
    -----
    start_time: datetime
     The start date and time for which to generate the expertise. 
    endtime: datetime
     The end date and time for which to generate the expertise.
    prd: str
     precipitation product that will be retrieved, either RZC or CPC
    file_dir: str
     The main directory where the retrieved data will be saved
    archive: str
     Path to where all the input data is stored and retrieved from.
    get_daily_POH: bool, optional
     Option to retrieve daily probability of hail product
    get_single_POH: bool, optional
     Option to retrieve 5-min probability of hail product

    Returns:
    --------
    sub_dir: str
     Directory where all files are saved.
    """

    n_incr = int((end_date-start_date).total_seconds() / (60 * 5))
    timeserie = start_date + np.array(
        [timedelta(minutes=5 * i) for i in range(n_incr + 1)]
    )

    start_time = str(start_date.strftime("%y%j%H%M"))
    

    sub_dir = os.path.join(file_dir, start_time + "_output/")
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)

    retrieve_precip(timeserie, prd, archive, sub_dir)

    if get_daily_POH:
        hail_path = os.path.join(sub_dir, "POH/")
        if not os.path.exists(hail_path):
            os.makedirs(hail_path)
        retrieve_POH(timeserie, archive, hail_path, single_POH=get_single_POH)
        if get_single_POH:
            retrieve_hail_crowdsource(timeserie=timeserie, dir=hail_path, transform=True)

    return sub_dir


def retrieve_precip(timeserie, prd, archive, dir):
    """Copies and extracts precipitation (RZC or CPC)
     from the MeteoSwiss database

    Args:
    -----
    timeserie: list, datetime
     List containing a timeserie with all times for which to retrieve the precipitation data
    prd: str
     Precipitation product that will be retrieved, either RZC or CPC
    archive: str
     Path to where all the input data is stored and retrieved from.
    dir: str
     The directory where the precipitation data should be saved

    Returns:
    --------
    None
    """
    base_name = [None]*len(timeserie)
    YYDOYS = set()

    for i, date in enumerate(timeserie):
        base_name[i] = date.strftime("%y%j%H%M")
        YYDOYS.add(base_name[i][:5])

    rain_path = os.path.join(dir, prd + "/")

    if not os.path.exists(rain_path):
        os.makedirs(rain_path)


    for YYDOY in YYDOYS:
        dst = os.path.join(dir, prd + YYDOY + ".zip")
        year = "20"+YYDOY[:2]

        if prd == "RZC":
            try:
                if archive.startswith("/store"):
                    src = os.path.join(archive,"data","hdf5",year,YYDOY,f"{prd}{YYDOY}.zip")
                else:
                    src = os.path.join(archive,year,YYDOY,f"{prd}{YYDOY}.zip")
                shutil.copy(src, dst)
            except FileNotFoundError:
                if archive.startswith("/store"):
                    src = os.path.join(archive,"data","hdf5",year,YYDOY,f"{prd}flt{YYDOY}.zip")
                
                else:
                    src = os.path.join(archive,"hdf5",year,YYDOY,f"{prd}flt{YYDOY}.zip")
                shutil.copy(src, dst)

        elif prd == "CPC":
            try:
                src = os.path.join(archive,"data",year,YYDOY,f"{prd}{YYDOY}.zip")
            except FileNotFoundError:
                src = os.path.join(archive,year,YYDOY,f"{prd}{YYDOY}.zip")
            shutil.copy(src, dst)

        _unzip_precip(prd,dst,base_name,rain_path)


def _unzip_precip(prd,src,base_name,rain_path):
    if prd == "RZC":
        with zipfile.ZipFile(src, "r") as zipObject:
            files = zipObject.namelist()
            filtered_files = [file for file in files if any(date in file for date in base_name)]
            for fileName in filtered_files:
                zipObject.extract(fileName, rain_path)
    elif prd == "CPC":
        with zipfile.ZipFile(src, "r") as zipObject:
            files = zipObject.namelist()
            filtered_files = [file for file in files if any(date in file for date in base_name)]
            for fileName in filtered_files:
                if fileName.endswith("00005.801.gif"):
                    zipObject.extract(fileName, rain_path)

def retrieve_POH(timeserie, archive, dir, single_POH=False):
    """
    Retrieve POH data for a given date and
     optionally extract single 5-min POH files,
     if single_POH is set to True.

    Args:
    -----
    timeserie: list, datetime
     List containing a timeserie with all times for which to retrieve the POH data
    archive: str
     Path to where all the input data is stored and retrieved from.
    dir: str
     The directory where the POH data should be saved
    single_POH: bool, optional
     Indicates whether to also retrieve the single
     5-min POH files. Defaults to False.

    Returns:
    --------
    None
    """
    base_name = [None]*len(timeserie)
    YYDOYS = set()

    for i, date in enumerate(timeserie):
        base_name[i] = date.strftime("%y%j%H%M")
        YYDOYS.add(base_name[i][:5])

    for YYDOY in YYDOYS:
        year = "20"+YYDOY[:2]
        if archive.startswith("/store"):
            src = os.path.join(archive,"data","hdf5",year,YYDOY,f"dBZCH{YYDOY}.zip")
        else:
            src = os.path.join(archive,"hdf5",year,YYDOY,f"dBZCH{YYDOY}.zip")
        print(type(src))
        # src = f"/store/msrad/radar/swiss/hdf5/{year}/{YYDOY}/dBZCH{YYDOY}.zip"
        if os.path.exists(src):
            _unzip_daily_POH(src,dir)
        else:
            print("daily POH file does not exist in this format")

        if single_POH:
            if archive.startswith("/store"):
                src = os.path.join(archive,"data","hdf5",year,YYDOY,f"BZCH{YYDOY}.zip")
            else:
                src = os.path.join(archive,"hdf5",year,YYDOY,f"BZCH{YYDOY}.zip")
            if not os.path.exists(src):
                src = os.path.join(archive,year,YYDOY,f"BZCH{YYDOY}.zip")
            # src = f"/store/msrad/radar/swiss/hdf5/{year}/{YYDOY}/BZCH{YYDOY}.zip"
            dst = os.path.join(dir, f"BZCH{YYDOY}.zip")
            shutil.copy(src, dst)
            _unzip_single_POH(dst,base_name,out_dir=dir)


def _unzip_daily_POH(src,out_dir):
    with zipfile.ZipFile(src, "r") as zipObject:
        listOfFileNames = zipObject.namelist()
        for fileName in listOfFileNames:
            if fileName.endswith("2400VL.845.h5"):
                zipObject.extract(fileName, out_dir)

def _unzip_single_POH(src,base_name,out_dir):
    hail_dir = os.path.join(out_dir,"SingleFiles")
    if not os.path.exists(hail_dir):
        os.makedirs(hail_dir)    
    with zipfile.ZipFile(src, "r") as zipObject:
        files = zipObject.namelist()
        filtered_files = [file for file in files if any(date in file for date in base_name)]
        for fileName in filtered_files:
            zipObject.extract(fileName,hail_dir)    

def retrieve_hail_crowdsource(timeserie, dir, transform=True):
    """
    Retrieve hail crowdsource data for a given date and optionally transform it.

    Args:
    -----
    timeserie: list, datetime
     List containing a timeserie with all times for which to retrieve the crowdsource data
    dir: str
     The directory where the crowdsource data should be saved.
    transform: bool, optional
     Indicates whether to transform the crowdsource data. Defaults to True.

    Returns:
    --------
    None
    """

    YYDOYS = set()
    for date in timeserie:
        YYDOYS.add(date.strftime("%y%j"))

    for YYDOY in YYDOYS:
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


def access_local_data(start_date,end_date,prd,input_dir,output_dir,get_daily_POH=False,
    get_single_POH=False):

    n_incr = int((end_date-start_date).total_seconds() / (60 * 5))
    timeserie = start_date + np.array(
        [timedelta(minutes=5 * i) for i in range(n_incr + 1)]
    )

    start_time = str(start_date.strftime("%y%j%H%M")) 

    sub_dir = os.path.join(output_dir, start_time + "_output/")
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)

    base_name = [None]*len(timeserie)
    YYDOYS = set()

    for i, date in enumerate(timeserie):
        base_name[i] = date.strftime("%y%j%H%M")
        YYDOYS.add(base_name[i][:5])
    rain_path = os.path.join(sub_dir, prd + "/")
    hail_path = os.path.join(sub_dir, "POH/")

    if not os.path.exists(rain_path):
        os.makedirs(rain_path)
    
    if not os.path.exists(hail_path):
        os.makedirs(hail_path)

    for YYDOY in YYDOYS:
        input_rain = os.path.join(input_dir, prd + YYDOY + ".zip")
        output_rain = os.path.join(sub_dir,f"{prd}_{YYDOY}.zip")
        shutil.copy(input_rain,output_rain)
        _unzip_precip(prd,input_rain,base_name,rain_path)

        if get_daily_POH:
            input_dPOH = os.path.join(input_dir, f"dBZCH{YYDOY}.zip")
            _unzip_daily_POH(input_dPOH,hail_path)
        if get_single_POH:
            input_sPOH = os.path.join(input_dir, f"BZC{YYDOY}.zip")
            _unzip_single_POH(input_sPOH,base_name,hail_path)
            crs_path = os.path.join(input_dir,f"HQX{YYDOY}0000.prd")
            if os.path.isfile(crs_path):
                transform_crowdsource(YYDOY, dir)
            else:
                print(f"no crowdsource data available on {YYDOY}")    

    return sub_dir