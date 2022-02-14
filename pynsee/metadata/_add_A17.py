
import pandas as pd
from pynsee.utils._move_col_after import _move_col_after

def _add_A17(df):

    df2 = df
    df2["A17"] = df2["A38"]

    string = "|".join(["^" + s + "[A-Z]!" for s in ["B", "D", "E"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'DE', regex = True)

    string = "|".join(["^" + s + "!" for s in ["CA"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C1', regex = True)

    string = "|".join(["^" + s + "!" for s in ["CD"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C2', regex = True)    

    string = "|".join(["^" + s + "!" for s in ["CI", "CJ", "CK"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C3', regex = True)

    string = "|".join(["^" + s + "!" for s in ["CL"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C4', regex = True)

    string = "|".join(["^" + s + "!" for s in ["CB", "CC", "CE", "CF", "CG", "CH", "CM"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C5', regex = True)

    string = "|".join(["^" + s + "[A-Z]!" for s in ["J"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'JZ', regex = True)

    string = "|".join(["^" + s + "[A-Z]!" for s in ["M", "N"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'MN', regex = True)

    string = "|".join(["^" + s + "[A-Z]!" for s in ["O", "P", "Q"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'OQ', regex = True)

    string = "|".join(["^" + s + "[A-Z]!" for s in ["R", "S", "T", "U"]])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'RU', regex = True)

    df2 = _move_col_after(df2, "A17", "A10")

    return df2
    