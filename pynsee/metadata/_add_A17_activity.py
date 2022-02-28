
import pandas as pd
from pynsee.utils._move_col_after import _move_col_after

def _add_A17_activity(df):

    df2 = df.copy()
    df2["A17"] = df2["A38"].copy()

    string = "|".join(["BZ", "DZ", "EZ"])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'DE', regex = True)

    df2["A17"] = df2["A17"].replace(to_replace = "CA", value = 'C1', regex = True)

    df2["A17"] = df2["A17"].replace(to_replace = "CD", value = 'C2', regex = True)    

    string = "|".join(["CI", "CJ", "CK"])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C3', regex = True)

    df2["A17"] = df2["A17"].replace(to_replace = "CL", value = 'C4', regex = True)

    string = "|".join(["CB", "CC", "CE", "CF", "CG", "CH", "CM"])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'C5', regex = True)

    df2["A17"] = df2["A17"].replace(to_replace = "JA|JB|JC", value = 'JZ', regex = True)

    string = "|".join(["MA", "MB", "MC", "NZ"])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'MN', regex = True)

    string = "|".join(["OZ", "PZ", "QA", "QB"])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'OQ', regex = True)

    string = "|".join(["RZ", "SZ", "TZ", "UZ"])
    df2["A17"] = df2["A17"].replace(to_replace = string, value = 'RU', regex = True)

    df2 = _move_col_after(df2, "A17", "A10")

    return df2
    