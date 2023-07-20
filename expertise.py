import subprocess
import os
from tools.retrieve_data import retrieve_input_data, access_local_data
from tools.main_expertise import make_expertise

DIR = os.path.abspath(os.path.dirname(__file__))


def run_expertise(
    start_time,
    end_time,
    product,
    file_dir,
    archive,
    name="Carrerabach",
    regionRectangle=[2739000, 2746000, 1178000, 1185000],
    *rg_args,
    **opt_kwargs,
):
    """
    Run the expertise script to retrieve data and generate plots for a given date and product (RZC or CPC).

    Args:
    -----
    start_time: datetime
     The start date and time for which to generate the expertise.
    endtime: datetime
     The end date and time for which to generate the expertise.
    product: str
     The product to use, either 'RZC' or 'CPC'.
    file_dir: str
     The directory where the data is stored and where the output will be saved.
    archive: str
     Path to where all the input data is stored and retrieved from.
     It accepts both "/store/msrad/radar/swiss/" or "/repos/repos_prod/radar/swiss/"
     or a local folder containing input files in {prd}{YYDOY}.zip or {YYDOY}_crowdsource.prd 
     (for hail crowdsource) data.
    name: str, optional
     Name of region of interest. Default is "Carrerabach".
    regionRectangle: list, optional
     Outer bounds of region of interest. Default is bounds corresponding to Carrerabach.
    *rg_args: list, optional
     Additional positional arguments for raingauges, output of func: make_rg
     should be passed.
    **opt_kwars: dict, optional
     Optional keyword arguments to be passed to the make_expertise function. The following keys are recognized:
     - POHfiles: bool, optional
     Whether to include POH daily data in the analysis. Default is False.
     - POHSingleFiles: bool, optional
     Whether to include 5-min POH file data in the analysis. Default is False.
     - singleFiles: bool, optional
     Whether to generate plots for 5-min files. Default is False.
     - roiMap: bool, optional
     Whether to generate a map of the region of interest. Default is False.
     - visibMap: bool, optional
     Whether to generate a visibility map. Default is False.
     - useOsm: bool, optional
     Whether to use OpenStreetMap data for the maps. Default is False.
     - useOsmSingleFiles: bool, optional
     Whether to use OpenStreetMap data for the individual file maps. Default is False.
     - make_kml_file: bool, optional
     Whether to generate a KML file for the region of interest. Default is False.

    Returns:
    --------
    None

    """
    try:
        opt_kwargs = opt_kwargs["opt_kwargs"]
    except KeyError:
        opt_kwargs = {}

    if "POHfiles" in opt_kwargs.keys():
        POHfiles = opt_kwargs["POHfiles"]
    else:
        POHfiles = False

    if "POHSingleFiles" in opt_kwargs.keys():
        POHSingleFiles = opt_kwargs["POHSingleFiles"]
    else:
        POHSingleFiles = False

    # 1. Retrieve input

    # 1a. Retrieve and extract from meteoswiss environment or CSCS
    if archive.startswith("/store/msrad/radar/swiss") or archive.startswith(
        "/repos/repos_prod/radar"
    ):
        print(
            "Data is extracted from either MeteoSwiss environment or CSCS environment"
        )
        outDir = retrieve_input_data(
            start_time,
            end_time,
            file_dir=file_dir,
            archive=archive,
            prd=product,
            get_daily_POH=POHfiles,
            get_single_POH=POHSingleFiles,
        )
    # 1b. Use copied files from own folder.
    else:
        outDir = access_local_data(
            start_time,
            end_time,
            prd=product,
            input_dir=archive,
            output_dir=file_dir,
            get_daily_POH=POHfiles,
            get_single_POH=POHSingleFiles,
        )
        print("zip files from a given path are used")

    os.chdir(outDir)

    # 2. run the shell script using subprocess.run
    if os.path.exists(os.path.join(outDir, "totalroi.bin")) and os.path.exists(
        os.path.join(outDir, "totalroi.json")
    ):
        print("totalroi already exists in this folder")

    else:
        bashCommand = f"{DIR}/expertise.sh {DIR} {outDir} {product}"
        result = subprocess.run([bashCommand], shell=True, check=True)

        # check the return code of the script
        if result.returncode == 0:
            print("Script ran successfully")
        else:
            print("Script failed with return code {}".format(result.returncode))

    if "singleFiles" in opt_kwargs.keys():
        singleFiles = opt_kwargs["singleFiles"]
    else:
        singleFiles = False

    if "roiMap" in opt_kwargs.keys():
        roiMap = opt_kwargs["roiMap"]
    else:
        roiMap = False

    if "visibMap" in opt_kwargs.keys():
        visibMap = opt_kwargs["visibMap"]
    else:
        visibMap = False

    if "useOsm" in opt_kwargs.keys():
        useOsm = opt_kwargs["useOsm"]
    else:
        useOsm = False

    if "useOsmSingleFiles" in opt_kwargs.keys():
        useOsmSingleFiles = opt_kwargs["useOsmSingleFiles"]
    else:
        useOsmSingleFiles = False

    if "make_kml_file" in opt_kwargs.keys():
        make_kml_file = opt_kwargs["make_kml_file"]
    else:
        make_kml_file = False

    # 3. run expertise
    make_expertise(
        outDir,
        product,
        name,
        regionRectangle,
        singleFiles,
        POHfiles,
        POHSingleFiles,
        roiMap,
        visibMap,
        useOsm,
        useOsmSingleFiles,
        make_kml_file,
        *rg_args,
    )
