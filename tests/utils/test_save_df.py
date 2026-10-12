# -*- coding: utf-8 -*-

import pandas as pd

import pynsee.utils.save_df as save_df_module
from pynsee.utils.save_df import save_df


def _cached_echo(tmp_path, monkeypatch):
    monkeypatch.setattr(
        save_df_module, "_create_insee_folder", lambda: str(tmp_path)
    )

    @save_df()
    def echo(*args, start=None, end=None, update=False, silent=True):
        return pd.DataFrame(
            {"args": [repr(args)], "start": [start], "end": [end]}
        )

    return echo


def test_save_df_cache_key_distinguishes_keyword_names(tmp_path, monkeypatch):
    echo = _cached_echo(tmp_path, monkeypatch)

    first = echo("A", start="2023")
    second = echo("A", end="2023")

    assert first.loc[0, "start"] == "2023"
    assert second.loc[0, "start"] is None
    assert second.loc[0, "end"] == "2023"


def test_save_df_cache_key_distinguishes_argument_boundaries(
    tmp_path, monkeypatch
):
    echo = _cached_echo(tmp_path, monkeypatch)

    first = echo("AB", "C")
    second = echo("A", "BC")

    assert first.loc[0, "args"] == repr(("AB", "C"))
    assert second.loc[0, "args"] == repr(("A", "BC"))


def test_save_df_reuses_cache_for_identical_calls(tmp_path, monkeypatch):
    echo = _cached_echo(tmp_path, monkeypatch)

    echo("A", start="2023", end="2024")
    echo("A", end="2024", start="2023")

    assert len(list(tmp_path.iterdir())) == 1
