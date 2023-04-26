# nc-convert

<p align="center">
    <a href="https://github.com/tsdat/ncconvert/actions/workflows/pytest.yml">
        <img src="https://github.com/tsdat/ncconvert/actions/workflows/pytest.yml/badge.svg">
    </a>
    <a href=https://badge.fury.io/py/ncconvert>
        <img src="https://badge.fury.io/py/ncconvert.svg">
    </a>
    <a href="https://codecov.io/gh/tsdat/ncconvert" >
        <img src="https://codecov.io/gh/tsdat/ncconvert/branch/main/graph/badge.svg"/>
    </a>
    <a href="https://codeclimate.com/github/tsdat/ncconvert/maintainability">
        <img src="https://api.codeclimate.com/v1/badges/c39461855d8c99b676d9/maintainability" />
    </a>
    <a href=https://github.com/psf/black>
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
</p>

Converts netCDF to other formats

## Usage

Coming soon...

## Developing

Create a python environment using at least python 3.8, then install the requirements:

```shell
pip install ".[dev,cli]"
```

Run `make coverage` to generate a report of test coverage.

Releasing the package is as simple as creating a tagged release in GitHub. Make sure to create a new tag using `vX.Y.Z`
format, where `X` is the major version, `Y` is the minor version, and `Z` is the micro version. Set the release title
to `X.Y.Z`.
