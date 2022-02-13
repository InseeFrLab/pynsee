
import pandas as pd

class MacroDataframe(pd.DataFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _constructor(self):
        return MacroDataframe

    from pynsee.macrodata.split_title import split_title
