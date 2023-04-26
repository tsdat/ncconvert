from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import pandas as pd

import xarray as xr


def _dump_metadata(dataset: xr.Dataset, filepath: str | Path) -> Path:
    metadata = dataset.to_dict(data=False, encoding=True)
    metadata_json = json.dumps(metadata, indent=4)
    metadata_path = Path(filepath).with_suffix(".json")
    metadata_path.write_text(metadata_json)
    return metadata_path


def _to_dataframe(
    dataset: xr.Dataset, filepath: str | Path
) -> tuple[Path, pd.DataFrame]:
    df = dataset.to_dataframe(dim_order=list(dataset.dims))

    return Path(filepath), df


def _to_dataframe_collection(
    dataset: xr.Dataset, filepath: str | Path, extension: str
) -> tuple[tuple[Path, pd.DataFrame], ...]:
    outputs: list[tuple[Path, pd.DataFrame]] = []

    if extension.startswith("."):
        extension = extension[1:]

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
