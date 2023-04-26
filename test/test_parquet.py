import json
import os
from pathlib import Path

import pandas as pd
import xarray as xr


def test_vanilla_parquet(dataset: xr.Dataset):
    from ncconvert.parquet import to_parquet

    filepath = Path(".tmp/data/vanilla.parquet")

    output_path, metadata_path = to_parquet(dataset, filepath)

    assert output_path == filepath
    assert metadata_path == filepath.with_suffix(".json")

    df = pd.read_parquet(output_path)

    assert len(df.index) == len(dataset.time) * len(dataset.height)
    assert len(df.columns) == len(dataset.data_vars)  # pq idxs don't count towards cols

    meta = json.loads(metadata_path.read_text())

    assert "datastream" in meta["attrs"]
    assert "time" in meta["coords"]

    os.remove(output_path)
    os.remove(metadata_path)


def test_parquet_collection(dataset: xr.Dataset):
    from ncconvert.parquet import to_parquet_collection

    filepath = Path(".tmp/data/collection.20220405.000000.parquet")

    output_paths, metadata_path = to_parquet_collection(dataset, filepath)

    assert len(output_paths) == 4
    assert filepath.with_suffix(".height.parquet") in output_paths
    assert filepath.with_suffix(".parquet") in output_paths
    assert filepath.with_suffix(".time.parquet") in output_paths
    assert filepath.with_suffix(".time.height.parquet") in output_paths
    assert metadata_path == filepath.with_suffix(".json")

    h_df = pd.read_parquet(sorted(output_paths)[0])  # type: ignore
    assert len(h_df.index) == len(dataset.height)
    assert list(h_df.columns) == ["other"]

    df = pd.read_parquet(sorted(output_paths)[1])  # type: ignore
    assert len(df.index) == 1
    assert list(df.columns) == ["static"]

    th_df = pd.read_parquet(sorted(output_paths)[2])  # type: ignore
    assert len(th_df.index) == len(dataset.time) * len(dataset.height)
    assert list(th_df.columns) == ["temperature"]

    t_df = pd.read_parquet(sorted(output_paths)[3])  # type: ignore
    assert len(t_df.index) == len(dataset.time)
    assert list(t_df.columns) == ["humidity"]

    meta = json.loads(metadata_path.read_text())
    assert "datastream" in meta["attrs"]
    assert "time" in meta["coords"]

    for output_path in output_paths:
        os.remove(output_path)
    os.remove(metadata_path)
