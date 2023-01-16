from datetime import datetime

from expertise import run_expertise
from utils.transformation import make_rg

rg1 = make_rg("BLZ", 30, 2720913, 1116587)
rg2 = make_rg("BLZ", 42, 2720913, 1116587)
rain_gauges = [rg1, rg2]

date=datetime(2022,6,10)
product="RZC"

run_expertise(
    date,
    product,
    file_dir="../example/",
    rg_args = rain_gauges,
    opt_kwargs={"visibMap": True, "POHfiles": True})