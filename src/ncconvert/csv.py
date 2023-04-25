from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

import xarray as xr


# Uses vanilla xarray and pandas settings to convert xarray to csv
# The csv will be indexed by the cartesian product of the dataset's
# indexes (coordinate variables). Returns path to the output file and
# the path to the metadata file
def to_vanilla_csv(
    dataset: xr.Dataset,
    filepath: str | Path,
    to_csv_kwargs: Dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    if to_csv_kwargs is None:
        to_csv_kwargs = {}

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    df = dataset.to_dataframe(dim_order=list(dataset.dims))
    df.to_csv(filepath, **to_csv_kwargs)  # type: ignore

    metadata = dataset.to_dict(data=False, encoding=True)
    metadata_json = json.dumps(metadata, indent=4)
    metadata_path = Path(filepath).with_suffix(".json")
    metadata_path.write_text(metadata_json)

    return Path(filepath), metadata_path


# Creates a collection of csv files. Csv files are split such that each file contains a
# unique index structure. For datasets with only 1 dimension this is exactly the same as
# the `to_vanilla_csv()` method. For a dataset with dimensions time & height with some
# variables dimensioned by time, some by height, and some dimensioned by both, this will
# result in 3 csv files; one for variables dimensioned only by time, another for
# variables dimensioned only by height, and one more for variables dimensioned by both.
# CSV files with more than one dimension will be indexed by the cartesian product of the
# dimensions (same as `to_vanilla_csv()`). Metadata is stored in a separate file.
def to_csv_collection(
    dataset: xr.Dataset,
    filepath: str | Path,
    to_csv_kwargs: Dict[str, Any] | None = None,
) -> tuple[tuple[Path, ...], Path]:
    if to_csv_kwargs is None:
        to_csv_kwargs = {}

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    # Get variable dimension groupings
    dimension_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for var_name, data_var in dataset.data_vars.items():
        dims = tuple(str(d) for d in data_var.dims)
        dimension_groups[dims].append(var_name)

    # Save each dimension group to a file
    csv_filepaths: list[Path] = []
    for dim_group, variable_names in dimension_groups.items():
        df = dataset[variable_names].to_dataframe(dim_order=dim_group)
        dim_group_path = Path(filepath).with_suffix(f".{'.'.join(dim_group)}.csv")
        csv_filepaths.append(dim_group_path)
        df.to_csv(dim_group_path, **to_csv_kwargs)

    metadata = dataset.to_dict(data=False, encoding=True)
    metadata_json = json.dumps(metadata, indent=4)
    metadata_path = Path(filepath).with_suffix(".json")
    metadata_path.write_text(metadata_json)

    return tuple(csv_filepaths), metadata_path
