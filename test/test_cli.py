import sys
from pathlib import Path

import pytest
import xarray as xr
from typer.testing import CliRunner


# NOTE: This test must run before any other tests that import ncconvert.cli, otherwise
# the ncconvert.cli import will already be cached and we cannot mock missing deps
def test_cli_import_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    # Simulate the absence of required modules
    monkeypatch.setitem(sys.modules, "tqdm", None)  # type: ignore
    monkeypatch.setitem(sys.modules, "typer", None)  # type: ignore

    # Importing the module with missing dependencies should exit with code 1
    with pytest.raises(SystemExit) as e:
        import ncconvert.cli  # noqa: F401
    assert e.value.code == 1

    # Check the output contains the expected error message
    captured = capsys.readouterr()
    assert "The ncconvert CLI requires extra dependencies" in captured.out
    assert "Please run 'pip install ncconvert[cli]' to install these" in captured.out
    assert "Aborting..." in captured.out


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
