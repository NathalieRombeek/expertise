from datetime import datetime

from expertise import run_expertise
from utils.transformation import make_rg

rg1 = make_rg("BLZ", 30, 2720913, 1116587)
rg2 = make_rg("BLZ", 42, 2720913, 1116587)
rain_gauges = [rg1, rg2]

start_date = datetime(2022, 7, 20, 16, 0)
end_date = datetime(2022, 7, 21, 14, 0)

opt_kwargs = {
        "visibMap": False,
        "POHfiles": True,
        "POHSingleFiles": False,
        "singleFiles": False,
        "roiMap": False,
        "visibMap": False,
        "useOsm": False,
        "UseOsmSingleFiles": False,
        "make_kml_file": False,
    }

product = "RZC"
name = "Carrerabach"
regionRectangle = [2739000, 2746000, 1178000, 1185000]
archive="/store/msrad/radar/swiss/"

run_expertise(
    start_date,
    end_date,
    product,
    "../example/", #path where output needs to be stored
    archive,#"/store/msrad/radar/swiss/", #path where input is stored (or use local path containig .zip and optionally .prd file)
    name,
    regionRectangle,
    *rg_args,
    **opt_kwargs
)
