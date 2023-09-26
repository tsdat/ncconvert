from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path

import pandas as pd
import xarray as xr

logger = logging.getLogger(__name__)


def _dump_metadata(dataset: xr.Dataset, filepath: str | Path) -> Path:
    metadata = dataset.to_dict(data=False, encoding=True)
    metadata_json = json.dumps(metadata, default=str, indent=4)
    metadata_path = Path(filepath).with_suffix(".json")
    metadata_path.write_text(metadata_json)
    return metadata_path


def _to_dataframe(
    dataset: xr.Dataset, filepath: str | Path, extension: str
) -> tuple[Path, pd.DataFrame]:
    extension = extension if extension.startswith(".") else "." + extension

    df = dataset.to_dataframe(dim_order=list(dataset.dims))

    return Path(filepath).with_suffix(extension), df


def _to_dataframe_collection(
    dataset: xr.Dataset, filepath: str | Path, extension: str
) -> tuple[tuple[Path, pd.DataFrame], ...]:
    outputs: list[tuple[Path, pd.DataFrame]] = []

    extension = extension[1:] if extension.startswith(".") else extension

    # Get variable dimension groupings
    dimension_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for var_name, data_var in dataset.data_vars.items():
        dims = tuple(str(d) for d in data_var.dims)
        dimension_groups[dims].append(var_name)

    # Create DataFrame collection
    for dim_group, variable_names in dimension_groups.items():
        if dim_group == ():
            # to_dataframe() doesn't support 0-D data so we make it into a series and
            # then convert it into a DataFrame
            df = pd.DataFrame(dataset[variable_names].to_pandas()).T
            dim_group_path = Path(filepath).with_suffix(f".{extension}")
        else:
            df = dataset[variable_names].to_dataframe(dim_order=dim_group)
            dim_group_path = Path(filepath).with_suffix(
                f".{'.'.join(dim_group)}.{extension}"
            )
        outputs.append((dim_group_path, df))

    return tuple(outputs)


def _to_faceted_dim_dataframe(
    dataset: xr.Dataset, filepath: str | Path, extension: str
) -> tuple[Path, pd.DataFrame]:
    extension = extension if extension.startswith(".") else "." + extension

    # Get variable dimension groupings
    dimension_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for var_name, data_var in dataset.data_vars.items():
        dims = tuple(str(d) for d in data_var.dims)
        if len(dims) > 2:
            logger.error(
                (
                    "Variable %s has more than 2 dimensions and will not be supported."
                    " Dims: %s"
                ),
                var_name,
                dims,
            )
            continue
        elif len(dims) == 2 and "time" not in dims:
            logger.error(
                (
                    "2D variables are only supported when 'time' is one of its"
                    " dimensions. Found variable %s with dimensions: %s."
                ),
                var_name,
                dims,
            )
            continue
        dimension_groups[dims].append(var_name)

    ds = dataset[["time"]].copy()
    for dims, var_list in dimension_groups.items():
        # simple case
        if dims == ("time",):
            ds.update(dataset[var_list])
            continue

        shape = dataset[var_list[0]].shape

        # If scalar, expand to make time the first dimension
        if not shape:
            _tmp = dataset[var_list].expand_dims({"time": dataset["time"]})
            ds.update(_tmp[var_list])
            continue

        _tmp = dataset[var_list]

        # If 1D, expand to make time a dimension (2D)
        if len(shape) == 1:
            _tmp = _tmp.expand_dims({"time": dataset["time"]})

        # For 2D, make time the first dimension and flatten the second
        new_dims = ("time", [d for d in dims if d != "time"][0])
        _tmp = _tmp.transpose(*new_dims)
        _tmp = _flatten_dataset(_tmp, new_dims[1])
        ds = ds.merge(_tmp)

    df = ds.to_dataframe()

    return Path(filepath).with_suffix(extension), df


def _flatten_dataset(ds: xr.Dataset, second_dim: str) -> xr.Dataset:
    """Transforms a 2D dataset into 1D by adding variables for each value of the second
    dimension. The first dimension must be 'time'.

    Args:
        ds (xr.Dataset): The dataset to flatten. Must only contain two dimensions/coords
            and only the variables to flatten.

    Returns:
        xr.Dataset: The flattened dataset. Preserves attributes.
    """

    output = ds[["time"]]

    dim_values = ds[second_dim].values

    dim_units = ds[second_dim].attrs.get("units")
    if not dim_units or dim_units == "1":
        dim_units = ""

    dim_suffixes = [f"{dim_val}{dim_units}" for dim_val in dim_values]

    for var_name, data in ds.data_vars.items():
        for i, suffix in enumerate(dim_suffixes):
            output[f"{var_name}_{suffix}"] = data[:, i]

    output = output.drop_vars(second_dim)  # remove from coords
    return output
