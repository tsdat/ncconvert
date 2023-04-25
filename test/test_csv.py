import json
import os
from pathlib import Path

import pandas as pd
import pytest
import xarray as xr


@pytest.fixture
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
                [0.0, 10.0, 20.0, 30.0],
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


def test_vanilla_csv(dataset: xr.Dataset):
    from ncconvert.csv import to_vanilla_csv

    filepath = Path(".tmp/data/vanilla.csv")

    output_path, metadata_path = to_vanilla_csv(dataset, filepath)

    assert output_path == filepath
    assert metadata_path == filepath.with_suffix(".json")

    df = pd.read_csv(output_path)

    assert len(df.index) == len(dataset.time) * len(dataset.height)
    assert len(df.columns) == len(dataset.coords) + len(dataset.data_vars)

    meta = json.loads(metadata_path.read_text())

    assert "datastream" in meta["attrs"]
    assert "time" in meta["coords"]

    os.remove(output_path)
    os.remove(metadata_path)


def test_csv_collection(dataset: xr.Dataset):
    from ncconvert.csv import to_csv_collection

    filepath = Path(".tmp/data/collection.20220405.000000.csv")

    output_paths, metadata_path = to_csv_collection(dataset, filepath)

    assert len(output_paths) == 3
    assert filepath.with_suffix(".height.csv") in output_paths
    assert filepath.with_suffix(".time.csv") in output_paths
    assert filepath.with_suffix(".time.height.csv") in output_paths
    assert metadata_path == filepath.with_suffix(".json")

    h_df = pd.read_csv(sorted(output_paths)[0])  # type: ignore
    assert len(h_df.index) == len(dataset.height)
    assert list(h_df.columns) == ["height", "other"]

    t_df = pd.read_csv(sorted(output_paths)[1])  # type: ignore
    assert len(t_df.index) == len(dataset.time)
    assert list(t_df.columns) == ["time", "humidity"]

    th_df = pd.read_csv(sorted(output_paths)[2])  # type: ignore
    assert len(th_df.index) == len(dataset.time) * len(dataset.height)
    assert list(th_df.columns) == ["time", "height", "temperature"]

    meta = json.loads(metadata_path.read_text())
    assert "datastream" in meta["attrs"]
    assert "time" in meta["coords"]

    for output_path in output_paths:
        os.remove(output_path)
    os.remove(metadata_path)
