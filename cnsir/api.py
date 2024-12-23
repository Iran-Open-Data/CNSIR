"""CNSIR, Iran Census Sample, Main API

This module provides a high-level API for accessing and analyzing data from the 
Iran Census Sample. It simplifies data loading, exploration, and analysis for 
users without extensive programming knowledge.

"""
# pylint: disable=too-many-arguments
# pylint: disable=unused-argument
# pylint: disable=too-many-locals

from typing import Any, Iterable, Literal
from pathlib import Path

import pandas as pd

from bssir.metadata_reader import config, _Years
from bssir.api import API


defaults, metadata = config.set_package_config(Path(__file__).parent)
api = API(defaults=defaults, metadata=metadata)

_Table = Literal["household", "individual"]
_Attribute = Literal["Province", "County", "Urban_Rural"]


def __get_optional_params(local_variables: dict) -> dict:
    return {key: value for key, value in local_variables.items() if value is not None}


def load_table(
    table_name: _Table,
    years: _Years = "last",
    form: Literal["normalized", "cleaned", "raw"] | None = None,
    *,
    on_missing: Literal["error", "download", "create"] | None = None,
    redownload: bool | None = None,
    save_downloaded: bool | None = None,
    recreate: bool | None = None,
    save_created: bool | None = None,
) -> pd.DataFrame:
    """Load a table for the given table name and year(s).

    This function loads original survey tables as well as package
    tables defined in this library.

    Original survey tables are available in three forms:

    - 'raw' - Contains the raw survey data without any modifications
    - 'cleaned' - Raw data with added labels, types, removed irrelevant
        values, but no changes to actual data
    - 'normalized' - Standardized data form with consistent column
        names, value encodings and table structure applied across data
        from multiple survey years. Also adds useful metadata like
        table name and year identifiers.

    Package tables are defined in this library to facilitate working
    with the data and are only available in normalized form.

    For more details on available tables, see the documentation
    [tables page](https://iran-open-data.github.io/CNSIR/tables/).

    Parameters
    ----------
    table_name : _Table, default "data"
        The name of the table to load.
    years : _Years, default "last"
        The years of data to load.
    form : {"normalized", "cleaned", "raw"}, default "normalized"
        The form of the data to load. Options are "normalized",
        "cleaned", or "raw".

    !!! note
        The `years` parameter accepts different input types:

        - int: A single year integer like 1390 or 90
        - list[int]: A list of integer years [1390, 1395, 1400]
        - str: A hyphenated string range like '1390-1395'
        - "all": A string indicating all available years
        - "last": A string indicating only the most recent year

    Other parameters
    ----------------
    on_missing : {"download", "create", "error"}, default "download"
        Behavior if table is missing. "download" downloads the table,
        "create" generates table from raw data, "error" raises an
        exception.
    redownload : bool, default False
        Whether to re-download table if it exists.
    save_downloaded : bool, default True
        Whether to save newly downloaded data.
    recreate : bool, default False
        Whether to recreate table if it exists.
    save_created : bool, default True
        Whether to save newly created data.

    Returns
    -------
    pd.DataFrame
        Loaded table as a pandas DataFrame.

    Raises
    ------
    FileNotFoundError
        If data is missing and on_missing='error'.


    Examples
    --------
    ``` python
    import cnsir
    table = cnsir.load_table("data", 1400) # Loads survey data for year 1400
    ```

    """

    parameters = __get_optional_params(locals())
    return api.load_table(**parameters)


def load_knowledge(name: str, years: _Years = "last") -> Any:
    """Retrieve tables and graphs stored in the library's Knowledge Base.

    This function allows users to access valuable information, including tables and
    graphs, created from survey data and drawn from associated articles and reports.
    The data is pre-processed, organized, and readily available in the library's
    Knowledge Base, reducing the necessity for extensive data processing.


    Parameters
    ----------
    name : str
        The name of artifact requested.

    years : _Years, default "last"
        The years for which knowledge data is requested.

    Returns
    -------
    Any
        The requested knowledge data, which includes tables, graphs, or other informative content.

    """
    return api.load_knowledge(name=name, years=years)


def add_attribute(
    table: pd.DataFrame,
    name: _Attribute,
    *,
    aspects: Iterable[str] | str | None = None,
    column_names: Iterable[str] | str | None = None,
    id_col: str | None = None,
    year_col: str | None = None,
) -> pd.DataFrame:
    """Add attributes to table based on ID column.

    This function takes a Pandas DataFrame containing a household ID column,
    and enriches it by adding columns indicating attributes like urban/rural
    status, province, county etc.

    Parameters
    ----------
    table : pd.DataFrame
        Input DataFrame containing the ID column.
    name : _Attribute
        Name of attribute to add.
    aspects : list of str, default "name"
        Specific aspects of the attribute to add as columns.

    !!! note
        Supported attribute names are:

        - "Urban_Rural": Urban or rural status (aspects: "name", "farsi_name")
        - "Province": Province name (aspects: "name", "farsi_name")
        - "ID_Year": Year of survey (aspects: "name")

    Other parameters
    ----------------
    column_names : list of str, optional
        Custom names to use for the added columns.
    id_col : str, default "ID"
        Name of the ID column in the table.
    year_col : str, default "Year"
        Name of the year column in the table.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with additional columns containing attribute values.

    Examples
    --------
    ``` python
    import cnsir
    table = cnsir.load_table(years=1401)
    table = cnsir.add_attribute(table, "Urban_Rural")
    table = cnsir.add_attribute(table, "Province", aspects="farsi_name")
    ```

    """
    if id_col is None:
        table["location_code"] = (
            table["Urban_Rural_Code"].astype("UInt64") * 10_000 +
            table["Province_Code"].astype("UInt64") * 100 +
            table["County_Code"].astype("UInt64")
        )
        id_col = "location_code"
    parameters = __get_optional_params(locals())
    return api.add_attribute(**parameters)


def add_classification(
    table: pd.DataFrame,
    target: str,
    *,
    aspects: Iterable[str] | str | None = None,
    levels: Iterable[int] | int | None = None,
    column_names: Iterable[str] | str | None = None,
    year_col: str | None = None,
) -> pd.DataFrame:
    """Add industry or occupation classification to table.

    This function takes a Pandas DataFrame containing ISIC industry codes
    or ISCO occupation codes, and enriches it by decoding these codes into
    descriptive categories.

    The output DataFrame will contain additional columns with attributes
    from the classification system at the specified hierarchical levels,
    providing more information alongside the original coded values.

    Parameters
    ----------
    table : pd.DataFrame
        Input DataFrame containing the classification code column.
    target : str
        Name of the column containing industry or occupation codes.

    Other parameters
    ----------------
    aspects : list of str, optional
        Classification aspects to add as columns, like "label", "farsi_label".
    levels : list of int, optional
        Hierarchy levels to include, like 1 or [1, 2].
    column_names : list of str, optional
        Custom names to use for the added columns.
    year_col : str, default "Year"
        Name of year column for resolving annual changes.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with additional columns containing classification
            attributes.

    Examples
    --------
    ```python
    import cnsir
    table = cnsir.load_table(years=1401)
    table = cnsir.add_classification(table, target="Main_Job_Workplace_ISIC_Code")
    ```

    """
    parameters = __get_optional_params(locals())
    return api.add_classification(**parameters)


def setup(
    years: _Years,
    *,
    replace: bool = False,
    method: Literal["create_from_raw", "download_cleaned"] = "download_cleaned",
    download_source: Literal["original", "mirror"] = "mirror",
) -> None:
    """Set up package data for the given years.

    This function handles downloading or generating the required data tables
    to enable full functionality of the package for the specified years.

    By default, it tries to download pre-cleaned data which allows the package
    to work out of the box. But advanced users can generate data locally
    from raw survey files for more control, transparency or customization.

    Parameters
    ----------
    years : _Years
        The years of data to set up.

    Other parameters
    ----------------
    replace : bool, default False
        Whether to re-download or re-generate data if it already exists.
    method : {"create_from_raw", "download_cleaned"}, default "download_cleaned"
        The method to use for setting up data.
    download_source : {"original", "mirror"}, default "mirror"
        Where to download data from.

    Returns
    -------
    None
        The function executes setup tasks but does not return anything.

    Examples
    --------
    Basic usage:

    ```python
    import cnsir

    cnsir.setup(years="1390-1400")
    ```

    Advanced usage:

    ```python
    cnsir.setup(years="1390-1400",
               method="create_from_raw",
               replace=True)
    ```

    This will recreate all tables from 1390 to 1400 from raw data even if they
    already exist.

    """
    parameters = __get_optional_params(locals())
    api.setup(**parameters)


def setup_config(replace: bool = False) -> None:
    """Copy default config file to data directory.

    Copies the default config file 'settings_sample.yaml' from the package
    directory to 'config/cnsir_settings.yaml' in the root data directory.

    Overwrites any existing file if replace=True.

    Parameters
    ----------
    replace : bool, default False
        Whether to overwrite existing config file.

    """
    api.setup_config(replace=replace)


def download_map(
    map_name: str,
    source: Literal['original'] = "original"
) -> None:
    parameters = __get_optional_params(locals())
    api.utils.download_map(**parameters)
