from pathlib import Path

import xarray as xr
from typer.testing import CliRunner


def test_convert_cli(dataset: xr.Dataset):
    from ncconvert.cli import app

    # Hack needed to prevent xarray from raising a ValueError caused by it trying to
    # overwrite the 'units' attribute opn the time variable.
    dataset = dataset.copy()
    dataset["time"].encoding.update({"units": dataset["time"].attrs.pop("units")})

    runner = CliRunner()

    with runner.isolated_filesystem():
        dataset.to_netcdf("test.20220405.000000.nc")
        dataset.to_netcdf("test.20220405.001200.nc")
        dataset.to_netcdf("test.20220406.000000.nc")
        dataset.to_netcdf("test.20220406.001200.nc")
        dataset.to_netcdf("test.20220410.000000.nc")
        dataset.to_netcdf("test.20220410.001200.nc")
        dataset.to_netcdf("test.20220420.000000.nc")
        dataset.close()

        result = runner.invoke(
            app,
            args=(
                "to_csv",
                "test.2022040*.nc",
                "test.2022041*.nc",
                "test.20220420.000000.nc",
                "--output-dir",
                "outputs",
                "--verbose",
            ),
        )

        assert result.exit_code == 0

        assert len(list(Path("./outputs").glob("*.csv"))) == 7
        assert len(list(Path("./outputs").glob("*.json"))) == 7
