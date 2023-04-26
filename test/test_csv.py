import json
import os
from pathlib import Path

import pandas as pd
import xarray as xr


def test_vanilla_csv(dataset: xr.Dataset):
    from ncconvert.csv import to_csv

    filepath = Path(".tmp/data/vanilla.csv")

    output_path, metadata_path = to_csv(dataset, filepath)

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

    assert len(output_paths) == 4
    assert filepath.with_suffix(".csv") in output_paths
    assert filepath.with_suffix(".height.csv") in output_paths
    assert filepath.with_suffix(".time.csv") in output_paths
    assert filepath.with_suffix(".time.height.csv") in output_paths
    assert metadata_path == filepath.with_suffix(".json")

    df = pd.read_csv(sorted(output_paths)[0])  # type: ignore
    assert len(df.index) == 1
    assert "static" in list(df.columns)  # may also have 'Unnamed: 0' column

    h_df = pd.read_csv(sorted(output_paths)[1])  # type: ignore
    assert len(h_df.index) == len(dataset.height)
    assert list(h_df.columns) == ["height", "other"]

    t_df = pd.read_csv(sorted(output_paths)[2])  # type: ignore
    assert len(t_df.index) == len(dataset.time)
    assert list(t_df.columns) == ["time", "humidity"]

    th_df = pd.read_csv(sorted(output_paths)[3])  # type: ignore
    assert len(th_df.index) == len(dataset.time) * len(dataset.height)
    assert list(th_df.columns) == ["time", "height", "temperature"]

    meta = json.loads(metadata_path.read_text())
    assert "datastream" in meta["attrs"]
    assert "time" in meta["coords"]

    for output_path in output_paths:
        os.remove(output_path)
    os.remove(metadata_path)
