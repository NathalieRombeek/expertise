import subprocess
import os
from retrieve_data import retrieve_input_data
from main_expertise import make_expertise
from utils.transformation import make_rg

DIR = os.path.abspath(os.path.dirname(__file__))

rg1 = make_rg('BLZ',30,2720913,1116587)
rg2 = make_rg('BLZ',42,2720913,1116587)
raingauges=[rg1,rg2]

def run_expertise(date,product,file_dir="/scratch/nrombeek/expertise_package/example/2022196_saettele",**rg_kwargs):

    #1. Retrieve input
    outDir = retrieve_input_data(date, product="RZC", file_dir=file_dir)

    #2. run the shell script using subprocess.run
    bashCommand = f"{DIR}/test.sh {DIR} {outDir} {product}"
    result = subprocess.run([bashCommand], shell=True, check=True)

    # check the return code of the script
    if result.returncode == 0:
        print("Script ran successfully")
    else:
        print("Script failed with return code {}".format(result.returncode))

    #3. run expertise
    make_expertise(outDir, product, 
    singleFiles=False,
    POHfiles=False,
    POHSingleFiles=False,
    roiMap=False,
    visibMap=False,
    useOsm=False,
    useOsmSingleFiles=False,
    make_kml_file=False,**rg_kwargs)



