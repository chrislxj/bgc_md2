import xarray as xr
import os
from pathlib import Path
cableDataDir=os.environ['cableDataDir']
runId = "parallel_1901_1902_with_minimum_spinup"
outDir = "output/new4"
first_yr = 1901
last_yr = 1902
fns= ["out_ncar_"+str(yr)+"_ndep.nc"
        for yr in range(first_yr,last_yr+1)]
outpath=Path(cableDataDir).joinpath(runId,outDir)
ps=[outpath.joinpath(fn) for fn in fns]

dat0=xr.open_dataset(ps[0])
data=xr.open_mfdataset(paths=ps,combine='by_coords')
