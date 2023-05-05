from __future__ import annotations

from pathlib import Path
from typing import Any

import xarray as xr

from .utils import _dump_metadata, _to_dataframe, _to_dataframe_collection


def to_csv(
    dataset: xr.Dataset,
    filepath: str | Path,
    metadata: bool = True,
    **kwargs: Any,
) -> tuple[Path, Path | None]:
    """Writes an xarray dataset to a csv file using basic settings.

    The output file will be indexed by the cartesian product of the dataset's indexes
    (coordinate variables).

    Args:
        dataset (xr.Dataset): The dataset to write.
        filepath (str | Path): Where to write the file. This should be the path to a
            file, not the path to a folder. This should include the file extension.
        metadata (bool): If True, metadata from the xr.Dataset will be written to a
            .json file next to the output file. Defaults to True.
        to_csv_kwargs (Dict[str, Any] | None, optional): Extra arguments to provide to
            pandas.DataFrame.to_csv() as keyword arguments. Defaults to None.

    Returns:
        tuple[Path, Path | None]: The path to the written csv file and associated
            metadata file.
    """
    to_csv_kwargs = kwargs.get("to_csv_kwargs", {})

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    filepath, df = _to_dataframe(dataset, filepath, ".csv")
    df.to_csv(filepath, **to_csv_kwargs)  # type: ignore

    metadata_path = _dump_metadata(dataset, filepath) if metadata else None

    return Path(filepath), metadata_path


def to_csv_collection(
    dataset: xr.Dataset,
    filepath: str | Path,
    metadata: bool = True,
    **kwargs: Any,
) -> tuple[tuple[Path, ...], Path | None]:
    """Writes an xarray dataset to a collection of csv files.

    Output files are split such that each file contains the cartesian product of each
    unique pairing of coordinate dimensions.

    E.g., for a dataset with dimensions time and height with some variables dimensioned
    by time, some by height, and some by both, this will create three output files: one
    for variables dimensioned only by time (indexed by time), another for variables
    dimensioned only by height (indexed by height), and a final one for variables
    dimensioned by both (indexed by the cartesian product of time and height).

    Args:
        dataset (xr.Dataset): The dataset to write.
        filepath (str | Path): The base path for where to write the files. This should
            be the path to a file, not the path to a folder. This does not need to
            include a file extension; one will be added if not provided.
        metadata (bool): If True, metadata from the xr.Dataset will be written to a
            .json file next to the output file(s). Defaults to True.
        to_csv_kwargs (Dict[str, Any] | None, optional): Extra arguments to provide to
            pandas.DataFrame.to_csv() as keyword arguments. Defaults to None.

    Returns:
        tuple[tuple[Path, ...], Path | None]: The paths to the written csv files and
            associated metadata file.
    """
    to_csv_kwargs = kwargs.get("to_csv_kwargs", {})

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    data_groups = _to_dataframe_collection(dataset, filepath, ".csv")

    filepaths = []
    for fpath, df in data_groups:
        df.to_csv(fpath, **to_csv_kwargs)
        filepaths.append(fpath)

    metadata_path = _dump_metadata(dataset, filepath) if metadata else None

    return tuple(filepaths), metadata_path
