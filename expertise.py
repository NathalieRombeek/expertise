import subprocess
import os
from tools.retrieve_data import retrieve_input_data
from tools.main_expertise import make_expertise

DIR = os.path.abspath(os.path.dirname(__file__))

def run_expertise(
    date,
    product,
    file_dir="/scratch/nrombeek/expertise_package/example/2022196_saettele",*rg_args,**opt_kwargs,
):
    try:
        opt_kwargs=opt_kwargs['opt_kwargs']
    except KeyError:
        opt_kwargs={}

    # 1. Retrieve input
    outDir = retrieve_input_data(date, product="RZC", file_dir=file_dir)

    os.chdir(outDir)

    # 2. run the shell script using subprocess.run
    if os.path.exists(os.path.join(outDir,"totalroi.bin")) and os.path.exists(os.path.join(outDir,"totalroi.json")):
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
        singleFiles=opt_kwargs['singleFiles']
    else:
        singleFiles=False

    if "POHfiles" in opt_kwargs.keys():
        POHfiles=opt_kwargs['POHfiles']
    else:
        POHfiles=False

    if "POHSingleFiles" in opt_kwargs.keys():
        POHSingleFiles=opt_kwargs['POHSingleFiles']
    else:
        POHSingleFiles=False

    if "roiMap" in opt_kwargs.keys():
        roiMap=opt_kwargs['roiMap']
    else:
        roiMap=False

    if "visibMap" in opt_kwargs.keys():
        visibMap=opt_kwargs['visibMap']
    else:
        visibMap=False

    if "useOsm" in opt_kwargs.keys():
        useOsm=opt_kwargs['useOsm']
    else:
        useOsm=False

    if "useOsmSingleFiles" in opt_kwargs.keys():
        useOsmSingleFiles=opt_kwargs['useOsmSingleFiles']
    else:
        useOsmSingleFiles=False

    if "make_kml_file" in opt_kwargs.keys():
        make_kml_file=opt_kwargs['make_kml_file']
    else:
        make_kml_file=False

    # 3. run expertise
    make_expertise(
        outDir,
        product,
        singleFiles=singleFiles,
        POHfiles=POHfiles,
        POHSingleFiles=POHSingleFiles,
        roiMap=roiMap,
        visibMap=visibMap,
        useOsm=useOsm,
        useOsmSingleFiles=useOsmSingleFiles,
        make_kml_file=make_kml_file,
        *rg_args,
    )
