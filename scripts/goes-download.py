"""
Summary: The download script to interact directly with the goes2go package.
We only want to specify what is necessary and compatible with the goes2go package.
In general, we want to satellite, the spatial domain, and the period.

Args:
    satellite_number: 

**Input Parameters**

Downloading:
- satellite number: int --> (16,17,18)
- spatial extent: str --> full disk (F), CONUS (C), Mesoscale domains (M, M1, M2)
- goes instrument: str --> e.g. ABI radiance (or SUVI for helio)
- preprocessing level: str --> e.g. level-1b
- directory: str
- return xarray dataset or list of files --> return as file list works better?
- band specifications: list[int] --> download all or subset only
- start time (of range of times to be downloaded): str
- end time: str
- timesteps/number of files: str
- day vs. night mode: --> e.g. for only downloading day mode images

----------

---
Basic Processing:
- resolution: --> downscale all bands to common resolution (e.g. 2 km)
- coordinate system transformations
- etc.


=================
INPUT PARAMETERS
=================

# LIST OF DATES | START DATE, END DATE, STEP
np.arange, np.linspace
t0, t1, dt | num_files
timestamps = [t0, t1, t2]
# create list of dates
list_of_dates: list = ["2020-10-19 12:00:00", "2020-10-12 12:00:00", ...]

# SATELLITE INFORMATION
satellite_number: int = (16, 17, 18)i
instrument: str  = (ABI, ...)
processing_level: str = (level-1b,): str = (level-1b, ...)
data_product: str = (radiances, ...)

# LIST OF BANDS
list_of_bands: list = [1, 2, ..., 15, 16]

# TARGET-GRID
target_grid: xr.Dataset = ...


=================
ALGORITHMS
=================

for itime in timestamps:
    for iband in list_of_bands:
        # -------------------------------------------------
        # download to folder - use GOES2GO loader
        # -------------------------------------------------
        
        # open data in folder
        
        # -------------------------------------------------
        # quality check 1 - did it download
        # -------------------------------------------------
        if download_criteria:
            continue if allow_missing else break
        
        # quality check 2 - day and/or night specification
        if day_night_criteria:
            continue if allow_missing else break
        
        # -------------------------------------------------
        # CRS Transformation (Optional, preferred)
        # -------------------------------------------------
        # load dataset
        ds: xr.Dataset = xr.load_dataset(...)
        # coordinate transformation
        ds: xr.Dataset = crs_transform(ds, target_crs, *args, **kwargs)
        # resave
        ds.to_netcdf(...)
        
        # -------------------------------------------------
        # downsample/upscale/lower-res (optional, preferred)
        # -------------------------------------------------
        # load dataset
        ds: xr.Dataset = xr.load_dataset(...)
        # resample
        ds: xr.Dataset = downsample(ds, target_grid, *args, **kwargs)
        ds: xr.Dataset = transform_coords(ds, target_coords)
        # resave
        ds.to_netcdf(...)

"""
from typing import Optional, List, Union
import os
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import tqdm
import typer
from loguru import logger

from goes2go import GOES

def goes_download(
    list_of_dates: List[str],
    # t0: str,
    # t1: str,
    # dt: str,
    satellite_number: int=16,
    save_dir: Optional[str]=".",
    num_files: Optional[int]=None,
    instrument: str = 'ABI',
    processing_level: str = 'L1b',
    data_product: str = 'Rad',
    domain: str = 'F',
    bands: str = 'all'
    
):

    # run checks
    _check_input_processing_level(processing_level=processing_level)
    _check_instrument(instrument=instrument)
    _check_satellite_number(satellite_number=satellite_number)
    _check_domain(domain=domain)
    _check_bands(bands=bands)
    # TODO: check bands
    data_product = f"{instrument}-{processing_level}-{data_product}"
    logger.info(f"Data Product: {data_product}")
    _check_data_product_name(data_product=data_product)

    G = GOES(satellite=satellite_number, product=data_product, domain=domain)
    # get list of times
    # TODO: get timetimes
    if bands == 'all':
        list_of_bands = list(np.arange(1, 17))
    else:
        list_of_bands = bands
    # time_stamps = np.arange(t0, t1, dt)
    logger.info(f"Satellite Number: {satellite_number}")
    files = []
    with tqdm.tqdm(list_of_dates) as pbar_time:
        with tqdm.tqdm(list_of_bands) as pbar_bands:
            for itime in pbar_time:
                pbar_time.set_description(f"{itime}")
                for iband in pbar_bands:
                    pbar_bands.set_description(f"{iband}")
                    continue
                    # files.append(G.nearesttime(itime, bands=iband, return_as='filelist', save_dir=save_dir))

    return files


def _check_domain(domain: str) -> bool:
    """checks domain GOES data"""
    # TODO: Check mesoscale
    if str(domain) in ["F", "C", "M"]:
        return True
    else:
        msg = "Unrecognized domain "
        msg += f"\nNeeds to be 'F', 'C', 'M'."
        msg += "\nOthers are not yet implemented"
        raise ValueError(msg)
    

def _check_satellite_number(satellite_number: str) -> bool:
    """checks satellite number for GOES data"""
    if str(satellite_number) in ["16", "17", "18"]:
        return True
    else:
        msg = "Unrecognized satellite number level"
        msg += f"\nNeeds to be '16', '17', or '18'."
        msg += "\nOthers are not yet implemented"
        raise ValueError(msg)
    

def _check_input_processing_level(processing_level: str) -> bool:

    """checks processing level for GOES datas"""
    if processing_level in ["L1b"]:
        return True
    else:
        msg = "Unrecognized processing level"
        msg += f"\nNeeds to be 'L1b'. Others are not yet implemented"
        raise ValueError(msg)


def _check_instrument(instrument: str) -> bool:
    """checks instrument for GOES data."""
    if instrument in ["ABI"]:
        return True
    else:
        msg = "Unrecognized instrument"
        msg += f"\nNeeds to be 'ABI'. Others are not yet implemented"
        raise ValueError(msg)
    
def _check_data_product_name(data_product: str) -> bool:
    if data_product in ['ABI-L1b-Rad']:
        return True
    else:
        msg = "Unrecognized data product"
        msg += f"\nNeeds to be 'ABI-L1b-Rad'. Others are not yet implemented"
        raise ValueError(msg)
        
def _check_bands(bands: Union[List[str], str]) -> bool:
    if isinstance(bands, str):
        if bands in ['all']:
            return True
        else:
            msg = "Unrecognized bands"
            msg += f"\nNeeds to be 'all' or list of bands."
            raise ValueError(msg)
    elif isinstance(bands, list):
        criteria: lambda x: 17 > int(x) > 0

        result = list(map(criteria, bands))
        
        assert result.sum() == len(bands)
        

def main(input: str):

    print(input)
    



if __name__ == '__main__':
    typer.run(goes_download)

    """
    python rs_tools/scripts/goes-download.py LIST_OF_DATES "2020-10-19 00:00" "2020-10-19 12:00" SATELLITE_NUMBER 16
    """
