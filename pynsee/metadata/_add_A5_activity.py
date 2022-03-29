
import pandas as pd
from pynsee.utils._move_col_after import _move_col_before

def _get_A5_activity_label():
    
    A5 = pd.DataFrame(
        {'A5': ['AZ', 'BE', 'FZ', 'GU', 'OQ'],
        'TITLE_A5_FR': ['Agriculture, sylviculture et pêche',
        'Industrie manufacturière, industries extractives et autres',
        'Construction', 'Services principalement marchands',
        'Services principalement non marchands'],
        'TITLE_A5_EN': ['Agriculture, forestry, and fisheries',
        'Mining, quarrying and manufacturing',
        'Construction', 'Mainly market services', 'Mainly non-market services']}
    )

    return A5

def _add_A5_activity(df):

    df2 = df.copy()
    df2["A5"] = df2["A10"].copy()

    string = "|".join(["GI", "JZ", "KZ", "LZ", "LI", "MN", "RU"])
    df2["A5"] = df2["A5"].replace(to_replace = string, value = 'GU', regex = True)

    df2 = _move_col_before(df2, "A5", "A10")

    return df2
    


