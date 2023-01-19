from datetime import datetime

from expertise import run_expertise
from utils.transformation import make_rg

rg1 = make_rg("BLZ", 30, 2720913, 1116587)
rg2 = make_rg("BLZ", 42, 2720913, 1116587)
rain_gauges = [rg1, rg2]

start_date=datetime(2022,7,20,12,0)
end_date=datetime(2022,7,21,18,0)

product="RZC"

run_expertise(
    start_date,
    end_date,
    product,
    file_dir="../example",
    rg_args = rain_gauges,
    opt_kwargs={"visibMap": True, "POHfiles": True})