#!/usr/local/bin/bash

product=$1
outDir=$2
rg1=$3
rg2=$4
#SBATCH --mail-user=nathalie.rombeek@meteoswiss.ch
#SBATCH --job-name=expertise_nr
#SBATCH --mail-type=FAIL
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --mem=5000M
#SBATCH --partition=postproc
#SBATCH --account=msrad
#SBATCH --output=expertise.log
#SBATCH --error=expertise.err

SOURCE=${BASH_SOURCE[0]}
workDir=$( dirname "$SOURCE" )
printf '%s\n' "SOURCE=$( dirname "$SOURCE" )"

$workDir/pexp $outDir/$product/
conda activate hydrexp
python3 $workDir/main_expertise.py $product $outDir $rg1 $rg2

