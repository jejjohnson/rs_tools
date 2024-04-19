from __future__ import annotations

import gc
import glob
import logging
import os
import random
from collections import Iterable
from typing import List, Union, Dict

import numpy as np
from dateutil.parser import parse
from torch.utils.data import Dataset, DataLoader, RandomSampler
from tqdm import tqdm
import numpy as np
from typing import List
from loguru import logger
from torch.utils.data import Dataset
from rs_tools._src.preprocessing.normalize import apply_spectral_normalizer, apply_coordinate_normalizer
import xarray as xr
from torch.utils.data import Dataset, DataLoader, RandomSampler
from rs_tools._src.utils.io import get_list_filenames
from rs_tools._src.datamodule.utils import get_split

from iti.data.editor import Editor
from iti.data.dataset import BaseDataset, ITIDataModule

class GeoDataset(BaseDataset):
    def __init__(
        self,
        data_dir: List[str],
        editors: List[Editor],
        splits_dict: Dict=None,
        ext: str="nc",
        limit: int=None,
        load_coords: bool=True,
        load_cloudmask: bool=True, 
        **kwargs
    ):
        """
        Initialize the GeoDataset class.

        Args:
            data_dir (List[str]): A list of directories containing the data files.
            editors (List[Editor]): A list of editors for data preprocessing.
            splits_dict (Dict, optional): A dictionary specifying the splits for the dataset. Defaults to None.
            ext (str, optional): The file extension of the data files. Defaults to "nc".
            limit (int, optional): The maximum number of files to load. Defaults to None.
            load_coords (bool, optional): Whether to load the coordinates. Defaults to True.
            load_cloudmask (bool, optional): Whether to load the cloud mask. Defaults to True.
            **kwargs: Additional keyword arguments.

        """
        self.data_dir = data_dir
        self.editors = editors
        self.splits_dict = splits_dict
        self.ext = ext
        self.limit = limit
        self.load_coords = load_coords
        self.load_cloudmask = load_cloudmask

        self.data = self.get_files()

        super().__init__(
            data=self.data,
            editors=self.editors,
            ext=self.ext,
            limit=self.limit,
            **kwargs
        )

    def get_files(self):
        # Get filenames from data_dir
        self.filenames = get_list_filenames(data_path=self.data_dir, ext=self.ext)
        # split files based on split criteria
        files = get_split(filenames=self.filenames, split_dict=self.splits_dict)
        return files

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        data_dict = {}
        # Load dataset
        ds: xr.Dataset = xr.load_dataset(self.file_list[idx], engine="netcdf4")

        # Extract data
        data = ds.Rad.compute().to_numpy()
        data_dict["data"] = data
        # Extract wavelengths
        wavelengths = ds.band_wavelength.compute().to_numpy()
        data_dict["wavelengths"] = wavelengths

        # Extract coordinates
        if self.load_coords:
            latitude = ds.latitude.compute().to_numpy()
            longitude = ds.longitude.compute().to_numpy()
            coords = np.stack([latitude, longitude], axis=0)
            data_dict["coords"] = coords

        # Extract cloud mask
        if self.load_cloudmask:
            cloudmask = ds.cloud_mask.compute().to_numpy()
            data_dict["cloudmask"] = cloudmask

        return data_dict