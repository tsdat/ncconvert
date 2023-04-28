# nc-convert

Convert netCDF files to other formats

## Usage

```shell
pip install "ncconvert[cli]"
ncconvert to_csv data/*.nc --output-dir output_data/ --verbose
```

Formats other than csv are also supported. To see more information about supported formats, run

```shell
ncconvert --help
```

A python API is also available for each format, e.g.:

```python
import xarray as xr
from ncconvert import to_csv

ds = xr.open_dataset("netcdf-file.nc")

to_csv(ds, "output_folder/filename.csv")
```

## Developing

Create a python environment using at least python 3.8, then install the requirements:

```shell
pip install ".[dev,cli]"
```

Run `make coverage` to generate a report of test coverage.

Releasing the package is as simple as creating a tagged release in GitHub. Make sure to create a new tag using `vX.Y.Z`
format, where `X` is the major version, `Y` is the minor version, and `Z` is the micro version. Set the release title
to `X.Y.Z`.
