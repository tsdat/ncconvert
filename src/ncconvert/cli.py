import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union

import xarray as xr
from typing_extensions import Annotated

try:
    import tqdm
    import typer
except ImportError:
    logging.exception("")
    print(
        "\n"
        "The ncconvert CLI requires extra dependencies to work.\n"
        "Please run 'pip install ncconvert[cli]' to install these.\n"
        "\n"
        "Aborting..."
    )
    sys.exit(1)

from .csv import to_csv, to_csv_collection
from .parquet import to_parquet, to_parquet_collection


class Converter(Protocol):
    def __call__(
        self,
        dataset: xr.Dataset,
        filepath: Union[Path, str],
        metadata: bool = False,
        **kwargs: Optional[Any],
    ) -> Tuple[Union[Tuple[Path, ...], Path], Optional[Path]]:
        ...


# Register to_* methods as options. For now this is a manual process
AVAILABLE_METHODS: Dict[str, Converter] = {
    to_csv.__name__: to_csv,
    to_csv_collection.__name__: to_csv_collection,
    to_parquet.__name__: to_parquet,
    to_parquet_collection.__name__: to_parquet_collection,
}
_available_methods = list(AVAILABLE_METHODS)


def _expand_paths(filepaths: List[Path]) -> List[Path]:
    expanded_paths = []

    for filepath in filepaths:
        # If there is a glob in the path, expand it and add all matches
        # otherwise append the given path
        glob_match = re.search(r"[*?\[]", str(filepath))
        if glob_match:
            glob_char_idx = glob_match.start(0)
            parent = Path(str(filepath)[: glob_char_idx + 1]).parent
            pattern = str(filepath.relative_to(parent))
            expanded_paths.extend(Path(parent).glob(pattern))
        else:
            expanded_paths.append(filepath)

    return expanded_paths


app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def ncconvert(
    method: Annotated[
        str,
        typer.Argument(
            help=f"How to convert the netCDF file(s). Options are: {_available_methods}",
        ),
    ],
    files: Annotated[
        List[Path],
        typer.Argument(
            ...,
            resolve_path=True,
            dir_okay=False,
            callback=_expand_paths,
            help="The path to the netCDF files to convert.",
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            dir_okay=True,
            file_okay=False,
            help="The output dir where the converted file(s) should be saved.",
        ),
    ] = Path("./data"),
    metadata: Annotated[
        bool,
        typer.Option(help="Write dataset metadata to a .json file"),
    ] = True,
    verbose: Annotated[
        bool,
        typer.Option(help="Run in verbose mode."),
    ] = False,
):
    """Convert netCDF files to another format."""
    convert_function = AVAILABLE_METHODS[method]

    file_iterator = tqdm.tqdm(files) if verbose else files

    for file in file_iterator:
        ds = xr.open_dataset(file)
        output_filepath = output_dir / file.name
        output_data_files, metadata_file = convert_function(
            dataset=ds,
            filepath=output_filepath,
            metadata=metadata,
        )
        if verbose and output_data_files:
            typer.echo(f"Wrote data to {output_data_files}")
        if verbose and metadata:
            typer.echo(f"Wrote metadata to {metadata_file}")

    if verbose:
        typer.echo("Done!")

    return
