#!/usr/local/bin/bash

workDir=$1
outDir=$2
product=$3

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

$workDir/pexp $outDir/$product/
