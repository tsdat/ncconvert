import pandas as pd
import pytest
import xarray as xr


@pytest.fixture(autouse=True, scope="module")
def dataset() -> xr.Dataset:
    return xr.Dataset(
        coords={
            "time": (
                "time",
                pd.date_range(
                    "2022-04-05",
                    "2022-04-06",
                    periods=3 + 1,
                    inclusive="left",
                ),  # type: ignore
                {"units": "Seconds since 1970-01-01 00:00:00"},
            ),
            "height": (
                "height",
                [0, 10, 20, 30],
                {"units": "m", "long_name": "Height AGL"},
            ),
        },
        data_vars={
            "temperature": (
                ("time", "height"),
                [
                    [88, 80, 75, 70],
                    [89, 81, 76, 71],
                    [88.5, 81.5, 75.5, 69.5],
                ],
                {"units": "degF", "_FillValue": -9999.0},
            ),
            "humidity": (
                "time",
                [60.5, 65.5, 63],
                {"units": "%", "_FillValue": -9999.0},
            ),
            "other": (
                "height",
                [1, 2, 3, 4],
                {"units": "1", "_FillValue": -9999.0},
            ),
            "static": 1.5,
        },
        attrs={
            "datastream": "humboldt.buoy.c1",
            "title": "title",
            "description": "description",
            "location_id": "humboldt",
            "dataset_name": "buoy",
            "data_level": "c1",
        },
    )


@pytest.fixture(autouse=True, scope="module")
def bad_dataset() -> xr.Dataset:
    return xr.Dataset(
        coords={
            "time": (
                "time",
                pd.date_range(
                    "2022-04-05",
                    "2022-04-06",
                    periods=3 + 1,
                    inclusive="left",
                ),  # type: ignore
                {"units": "Seconds since 1970-01-01 00:00:00"},
            ),
            "range": (
                "range",
                [1, 2, 3],
                {},
            ),
            "height": (
                "height",
                [0, 10, 20, 30],
                {"units": "m", "long_name": "Height AGL"},
            ),
        },
        data_vars={
            "temperature": (
                ("range", "height"),
                [
                    [88, 80, 75, 70],
                    [89, 81, 76, 71],
                    [88.5, 81.5, 75.5, 69.5],
                ],
                {"units": "degF", "_FillValue": -9999.0},
            ),
            "too_large": (
                ("time", "range", "height"),
                [
                    [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]],
                    [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]],
                    [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]],
                ],
                {"units": "1", "_FillValue": -9999.0},
            ),
            "humidity": (
                "range",
                [60.5, 65.5, 63],
                {"units": "%", "_FillValue": -9999.0},
            ),
            "other": (
                "height",
                [1, 2, 3, 4],
                {"units": "1", "_FillValue": -9999.0},
            ),
            "time_var": (
                "time",
                [1, 2, 3],
                {"units": "1", "_FillValue": -9999.0},
            ),
        },
        attrs={
            "datastream": "bad.buoy.c1",
            "title": "title",
            "description": "description",
            "location_id": "bad",
            "dataset_name": "buoy",
            "data_level": "c1",
        },
    )
