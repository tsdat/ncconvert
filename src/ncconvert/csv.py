from __future__ import annotations

import xarray as xr
from typing import Dict, Any


import json
from pathlib import Path


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


# class CSVWriter:
#     """---------------------------------------------------------------------------------
#     Converts a `xr.Dataset` object to a pandas `DataFrame` and saves the result to a csv
#     file using `pd.DataFrame.to_csv()`. Properties under the `to_csv_kwargs` parameter
#     are passed to `pd.DataFrame.to_csv()` as keyword arguments.

#     ---------------------------------------------------------------------------------"""

#     class Parameters:
#         dim_order: Optional[List[str]] = None
#         to_csv_kwargs: Dict[str, Any] = {}

#     parameters: Parameters = Parameters()
#     file_extension: str = ".csv"

#     def write(
#         self, dataset: xr.Dataset, filepath: Optional[Path] = None, **kwargs: Any
#     ) -> None:
#         # QUESTION: Is this format capable of "round-tripping"?
#         # (i.e., ds != read(write(ds)) for csv format)
#         d1: List[Hashable] = []
#         d2: List[Hashable] = []
#         d2_coord: List[Hashable] = [v for v in dataset.coords if v != "time"]
#         for var in dataset:
#             shp = dataset[var].shape
#             if len(shp) <= 1:
#                 d1.append(var)
#             elif len(shp) == 2:
#                 d2.append(var)
#             else:
#                 warnings.warn(
#                     "CSV writer cannot save variables with more than 2 dimensions."
#                 )

#         # Save header data
#         header_filepath = filepath.with_suffix(".hdr.csv")  # type: ignore
#         header = dataset.attrs
#         with open(str(header_filepath), "w", newline="\n") as fp:
#             for key in header:
#                 fp.write(f"{key},{header[key]}\n")

#         # Save variable metadata
#         metadata_filepath = filepath.with_suffix(".attrs.csv")  # type: ignore
#         var_metadata: List[Dict[str, Any]] = []
#         for var in dataset:
#             attrs = dataset[var].attrs
#             attrs.update({"name": var})
#             var_metadata.append(attrs)
#         df_metadata = pd.DataFrame(var_metadata)
#         df_metadata = df_metadata.set_index("name")  # type: ignore
#         df_metadata.to_csv(metadata_filepath)

#         if d1:
#             # Save 1D variables
#             dim1_filepath = filepath.with_suffix(".time.1d.csv")  # type: ignore
#             ds_1d = dataset.drop_vars(d2)  # drop 2D variables
#             ds_1d = ds_1d.drop_vars(d2_coord)
#             df_1d = ds_1d.to_dataframe()
#             df_1d.to_csv(dim1_filepath, **self.parameters.to_csv_kwargs)  # type: ignore

#         if d2:
#             # Save 2D variables
#             for coord in d2_coord:
#                 dim2_filepath = filepath.with_suffix("." + coord + ".2d.csv")  # type: ignore
#                 ds_2d = dataset.drop_vars(d1)  # drop 1D variables
#                 other_dim_vars = [
#                     v for v in ds_2d.data_vars if coord not in ds_2d[v].dims
#                 ]
#                 other_coords = d2_coord.copy()
#                 other_coords.remove(coord)
#                 ds_2d = ds_2d.drop_vars(other_dim_vars + other_coords)
#                 df_2d = ds_2d.to_dataframe(self.parameters.dim_order)  # type: ignore
#                 df_2d.to_csv(dim2_filepath, **self.parameters.to_csv_kwargs)  # type: ignore
